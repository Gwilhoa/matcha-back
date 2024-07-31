import re

import psycopg2
from config import BaseConfig
from utils.logger import get_console_logger

from managers.database_manager.model_interface import ModelInterface

database_logger = get_console_logger('database_connection')


def validate_identifier(identifier):
    """Validate that the identifier (table or column name) is safe."""
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', identifier):
        raise ValueError(f'Invalid identifier: {identifier}')
    return identifier


def convert_value(field_type, value):
    """Convert the value to the appropriate type based on the field_type."""
    conversion_functions = {
        'VARCHAR': str,
        'INTEGER': int,
        'FLOAT': float,
        'BOOLEAN': lambda v: v.lower() in ['true', '1'],
        'DATE': str,
        'UUID': str,
    }

    # Determine the conversion function based on the field type
    for key in conversion_functions.keys():
        if key in field_type:
            return conversion_functions[key](value)

    raise Exception(f'Unsupported field type: {field_type}')


class DatabaseConnection:
    def __init__(self, config: BaseConfig):
        self.name = config.DB_NAME
        self.port = config.DB_PORT
        self.user = config.DB_USER
        self.password = config.DB_PASS
        self.ip = config.DB_IP
        self.database = None
        self.connect()

    def connect(self):
        try:
            self.database = psycopg2.connect(
                host=self.ip,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.name,
            )
            database_logger.info(f'Connected to database {self.name}')
        except Exception as e:
            database_logger.error(f'Could not connect to database {self.name}: {e}')
            raise e

    def health_check(self):
        try:
            with self.database.cursor() as cur:
                cur.execute('SELECT 1')
                database_logger.info('Database is connected')
                return True
        except Exception as e:
            database_logger.error(f'Database is not connected: {e}')
            return False

    def reset_tables(self):
        with self.database.cursor() as cur:
            cur.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
            self.database.commit()
            database_logger.info('Tables reset')

    def create_table(self):
        self.reset_tables()
        references = []
        subclass = set(ModelInterface.__subclasses__())
        for model in subclass:
            name = validate_identifier(model.__name__.replace('Model', '')).lower()
            fields = model.get_class_fields()
            field_definitions = []

            for field, value in fields.items():
                validated_field = validate_identifier(field)
                if value['type'] == 'foreign_key':
                    execute_reference = f"ALTER TABLE public.{name} {value['reference'].replace('FIELD', validated_field)}"
                    references.append(execute_reference)
                if value['type'] != 'relationship':
                    field_definitions.append(f'{validated_field} {value["value"]}')

            field_definitions_str = ', '.join(field_definitions)
            request = f'CREATE TABLE IF NOT EXISTS public.{name} ({field_definitions_str});'
            database_logger.debug(f'running {request}')
            with self.database.cursor() as cur:
                cur.execute(request)
                self.database.commit()
                database_logger.info(f'Table {name} created')
        for reference in references:
            with self.database.cursor() as cur:
                database_logger.debug(f'execute {reference}')
                cur.execute(reference)
                self.database.commit()

    def get_primary_key(self, model):
        name = validate_identifier(model.__class__.__name__.replace('Model', '').lower())
        qualified_name = f'public.{name}'

        query = """
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """

        try:
            with self.database.cursor() as cur:
                cur.execute(query, (qualified_name,))
                primary_key = cur.fetchone()
                if primary_key:
                    return primary_key[0]
                else:
                    raise Exception(f'No primary key found for table {qualified_name}')
        except Exception as e:
            database_logger.error(f'An error occurred while fetching the primary key: {e}')
            return None

    def get_all(self, model):
        name = validate_identifier(model.__class__.__name__.replace('Model', '').lower())
        query = f'SELECT * FROM public.{name}'

        try:
            with self.database.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                self.database.commit()

                result = []
                fields = model.get_class_fields()

                for row in rows:
                    instance = model.__class__()
                    for idx, field in enumerate(fields.keys()):
                        field_value = row[idx]
                        field_type = fields[field]

                        if isinstance(field_type, dict) and field_type.get('type') == 'relationship':
                            join_field = field_type['join_field']
                            related_field = self.get_related_field(join_field)
                            related_model_name = related_field['model']
                            related_model = self.get_model_by_name(related_model_name)
                            related_instance = self.get_one(related_model, field_value)
                            setattr(instance, field, related_instance)
                        else:
                            setattr(instance, field, field_value)
                    result.append(instance)

                return result
        except Exception as e:
            database_logger.error(f'An error occurred while fetching data: {e}')
            return []

    def get_one(self, model: ModelInterface, id_class: str):
        name = validate_identifier(model.__class__.__name__.replace('Model', '').lower())
        id_field = self.get_primary_key(model)

        if model.get_class_fields().get(id_field) is None:
            raise Exception('Model does not have an id')

        query = f'SELECT * FROM public.{name} WHERE {id_field} = %s'

        database_logger.debug(f'running {query}')
        try:
            with self.database.cursor() as cur:
                cur.execute(query, (id_class,))
                row = cur.fetchone()
                self.database.commit()

                if row is None:
                    raise Exception(f'No record found with {id_field} = {id_class}')

                instance = model.__class__()
                fields = model.get_class_fields()
                for idx, field in enumerate(fields.keys()):
                    field_value = row[idx]
                    field_type = fields[field]

                    if isinstance(field_type, dict) and field_type.get('type') == 'relationship':
                        join_field = field_type['join_field']
                        related_field = self.get_related_field(join_field)
                        related_model_name = related_field['model']
                        related_model = self.get_model_by_name(related_model_name)
                        related_instance = self.get_one(related_model, field_value)
                        setattr(instance, field, related_instance)
                    else:
                        setattr(instance, field, field_value)
                return instance

        except Exception as e:
            database_logger.error(f'An error occurred while fetching data: {e}')
            return None

    def get_related_field(self, join_field):
        # This function retrieves the related model and field for the given join_field
        for model in ModelInterface.__subclasses__():
            fields = model.get_class_fields()
            for _field, field_type in fields.items():
                if isinstance(field_type, dict) and field_type.get('type') == 'foreign_key' and field_type['field'] == join_field:
                    return {'model': field_type['model']}
        raise Exception(f'Related field for join_field {join_field} not found')

    def create_one(self, model):
        name = validate_identifier(model.__class__.__name__.replace('Model', '').lower())
        fields = model.get_class_fields()

        field_names = []
        placeholders = []
        values = []

        for field, field_type in fields.items():
            validate_identifier(field)
            field_names.append(field)
            placeholders.append('%s')
            value = model.__dict__.get(field)

            # Convert value based on field type
            converted_value = convert_value(field_type, value)
            values.append(converted_value)

        query = f'INSERT INTO public.{name} ({", ".join(field_names)}) VALUES ({", ".join(placeholders)})'
        database_logger.debug(f'running {query}')

        try:
            with self.database.cursor() as cur:
                cur.execute(query, values)
                self.database.commit()
        except Exception as e:
            self.database.rollback()
            database_logger.error(f'An error occurred: {e}')

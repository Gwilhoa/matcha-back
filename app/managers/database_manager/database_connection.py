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


class DatabaseConnection:
    def __init__(self, config: BaseConfig):
        self.name = config.DB_NAME
        self.port = config.DB_PORT
        self.user = config.DB_USER
        self.password = config.DB_PASS
        self.ip = config.DB_IP

        try:
            with psycopg2.connect(
                host=self.ip,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.name,
            ) as conn:
                with conn.cursor():
                    conn.commit()
                    database_logger.info(f'Connected to database {self.name}')
                    self.database = conn
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
        subclass = set(ModelInterface.__subclasses__())
        for model in subclass:
            name = validate_identifier(model.__name__.replace('Model', ''))
            fields = model.get_class_fields()
            field_definitions = []

            for field, value in fields.items():
                validated_field = validate_identifier(field)
                field_definitions.append(f'{validated_field} {value}')

            field_definitions_str = ', '.join(field_definitions)
            request = f'CREATE TABLE IF NOT EXISTS {name} ({field_definitions_str});'
            database_logger.debug(f'running {request}')

            with self.database.cursor() as cur:
                cur.execute(request)
                self.database.commit()
                database_logger.info(f'Table {name} created')

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

        print(f'Executing query: {query}', flush=True)

        try:
            with self.database.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                self.database.commit()
                print(f'Rows fetched: {rows}', flush=True)

                result = []
                fields = model.get_class_fields()
                for row in rows:
                    # Create an instance of the model and set its fields
                    instance = model.__class__()
                    for idx, field in enumerate(fields.keys()):
                        setattr(instance, field, row[idx])
                    result.append(instance)

                return result
        except Exception as e:
            database_logger.error(f'An error occurred while fetching the primary key: {e}')
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
                for idx, field in enumerate(model.get_class_fields().keys()):
                    setattr(instance, field, row[idx])
                return instance

        except Exception as e:
            database_logger.error(f'An error occurred while fetching the primary key: {e}')
            return None

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

            if 'VARCHAR' in field_type:
                values.append(str(value))
            elif 'INTEGER' in field_type:
                values.append(int(value))
            else:
                raise Exception(f'Unsupported field type: {field_type}')

        query = f'INSERT INTO public.{name} ({", ".join(field_names)}) VALUES ({", ".join(placeholders)})'
        database_logger.debug(f'running {query}')

        try:
            with self.database.cursor() as cur:
                cur.execute(query, values)
                self.database.commit()
        except Exception as e:
            self.database.rollback()
            print(f'An error occurred: {e}', flush=True)

    @staticmethod
    def string(length: int = 255, *, nullable: bool = False, primary_key: bool = False, default: str = None, unique: bool = False):
        return (
            f"VARCHAR({length}) "
            f"{'NOT NULL ' if not nullable else ' '}"
            f"{'PRIMARY KEY ' if primary_key else ' '}"
            f"{'DEFAULT ' + default if default else ' '}"
            f"{'UNIQUE ' if unique else ' '}"
        )

    @staticmethod
    def int(*, nullable: bool = False, primary_key: bool = False, default: int = None, unique: bool = False, auto_increment: bool = False):
        return (
            f"INTEGER "
            f"{'NOT NULL ' if not nullable else ' '}"
            f"{'PRIMARY KEY ' if primary_key else ' '}"
            f"{'DEFAULT ' + str(default) if default else ' '}"
            f"{'UNIQUE ' if unique else ' '}"
            f"{'AUTO_INCREMENT ' if auto_increment else ' '}"
        )

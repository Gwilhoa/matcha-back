import psycopg2
from config import BaseConfig
from utils.logger import get_console_logger

from managers.database_manager.model_interface import ModelInterface

database_logger = get_console_logger('database_connection')


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
        print(subclass, flush=True)
        for model in subclass:
            name = model.__name__.replace('Model', '')
            print(model.get_class_fields(), flush=True)
            request = f'CREATE TABLE IF NOT EXISTS {name} ('
            for field, value in model.get_class_fields().items():
                request += f'{field} {value},'
            request = request[:-1] + ');'
            with self.database.cursor() as cur:
                cur.execute(request)
                self.database.commit()
                database_logger.info(f'Table {name} created')

    def get_all(self, model):
        name = model.__class__.__name__.replace('Model', '').lower()
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
            print(f'An error occurred: {e}', flush=True)
            return []

    def get_one(self, model: ModelInterface, id_class: str):
        name = model.__class__.__name__.replace('Model', '').lower()
        if model.get_class_fields().get('id_' + name) is None:
            raise Exception('Model does not have an id')
        with self.database.cursor() as cur:
            cur.execute(f'SELECT * FROM {name} WHERE id_{name} = {id_class}')
            row = cur.fetchone()
            self.database.commit()
            instance = model.__class__()
            for idx, field in enumerate(model.get_class_fields().keys()):
                setattr(instance, field, row[idx])
            return instance

    def create_one(self, model):
        name = model.__class__.__name__.replace('Model', '').lower()
        fields = model.get_class_fields()
        values = []
        for field in fields:
            value = model.__dict__[field]
            if 'VARCHAR' in fields[field]:
                values.append(f"'{value}'")
            else:
                values.append(str(value))
        query = f'INSERT INTO public.{name} ({", ".join(fields.keys())}) VALUES ({", ".join(values)})'

        try:
            with self.database.cursor() as cur:
                cur.execute(query)
                self.database.commit()
        except Exception as e:
            self.database.rollback()
            print(f'An error occurred: {e}', flush=True)

    @staticmethod
    def string(length: int = 255, *, nullable: bool = False, primary_key: bool = False, default: str = None, unique: bool = False):
        return (
            f"VARCHAR({length}) "
            f"{'NOT NULL' if not nullable else ''} "
            f"{'PRIMARY KEY' if primary_key else ''} "
            f"{'DEFAULT ' + default if default else ''} "
            f"{'UNIQUE' if unique else ''}"
        )

    @staticmethod
    def int(*, nullable: bool = False, primary_key: bool = False, default: int = None, unique: bool = False, auto_increment: bool = False):
        return (
            f"INTEGER "
            f"{'NOT NULL' if not nullable else ''} "
            f"{'PRIMARY KEY' if primary_key else ''} "
            f"{'DEFAULT ' + str(default) if default else ''} "
            f"{'UNIQUE' if unique else ''} "
            f"{'AUTO_INCREMENT' if auto_increment else ''} "
        )

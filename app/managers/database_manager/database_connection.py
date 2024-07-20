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

    def get_all(self, model: ModelInterface):
        name = model.__name__.replace('Model', '')
        with self.database.cursor() as cur:
            cur.execute(f'SELECT * FROM {name}')
            return cur.fetchall()

    @staticmethod
    def string(length: int = 255, *, nullable: bool = False, primary_key: bool = False, default: str = None, unique: bool = False):
        return (
            f"VARCHAR({length})"
            f"{'NOT NULL' if not nullable else ''}"
            f"{'PRIMARY KEY' if primary_key else ''} "
            f"{'DEFAULT ' + default if default else ''} "
            f"{'UNIQUE' if unique else ''}"
        )

    @staticmethod
    def int():
        return 'INT'

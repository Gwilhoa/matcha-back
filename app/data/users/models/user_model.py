from managers.database_manager import ModelInterface, db_foreign_key, db_relationship, db_string, db_uuid


class TestModel(ModelInterface):
    id_test = db_uuid(nullable=False, primary_key=True, default='gen_random_uuid()')
    name = db_string(nullable=False)


class UserModel(ModelInterface):
    id_user = db_uuid(nullable=False, primary_key=True, default='gen_random_uuid()')
    password = db_string(nullable=False)
    first_name = db_string(nullable=False)
    last_name = db_string(nullable=False)
    gender = db_string(nullable=False)
    sexual_preference = db_string(nullable=False)
    test_id = db_foreign_key(TestModel, 'id_test', 'UUID')
    test = db_relationship(test_id)

from marshmallow import fields


class ModelInterface:
    def __init__(self):
        pass

    @classmethod
    def get_class_fields(cls):
        return {k: v for k, v in vars(cls).items() if not k.startswith('__') and not callable(v)}

    @classmethod
    def get_class_fiels_type(cls):
        value_type = {
            'VARCHAR': fields.String,
            'INTEGER': fields.Integer,
        }
        return_fields = {}
        class_fields = cls.get_class_fields()
        for key, value in class_fields.items():
            for v in value_type:
                if v in value:
                    return_fields[key] = value_type[v]()
        return return_fields

    def create_one(self):
        from setup import db

        db.create_one(self)

    def get_all(self) -> list['ModelInterface']:
        from setup import db

        return db.get_all(self)

    def get_one(self, id_class):
        from setup import db

        return db.get_one(self, id_class)

    def dump(self):
        return self.__dict__

    @classmethod
    def load(cls, data):
        obj = cls()
        for key, value in data.items():
            setattr(obj, key, value)
        return obj

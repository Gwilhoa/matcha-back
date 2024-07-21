class ModelInterface:
    def __init__(self):
        pass

    @classmethod
    def get_class_fields(cls):
        return {k: v for k, v in vars(cls).items() if not k.startswith('__') and not callable(v)}

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

    def load(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        return self

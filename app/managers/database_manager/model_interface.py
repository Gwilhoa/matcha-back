class ModelInterface:
    def __init__(self, name):
        self.name = name

    @classmethod
    def get_class_fields(cls):
        return {k: v for k, v in vars(cls).items() if not k.startswith('__') and not callable(v)}

    def create_one(self):
        from setup import db

        db.create_one(self)

    def get_all(self):
        from setup import db

        db.get_all(self)

    def commit(self):
        pass

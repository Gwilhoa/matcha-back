class ModelInterface:
    def __init__(self, name):
        self.name = name

    def get_class_fields(self):
        return {k: v for k, v in vars(self).items() if not k.startswith('__') and not callable(v)}

    def get_all(self):
        from setup import db

        db.get_all(self)

    def commit(self):
        pass

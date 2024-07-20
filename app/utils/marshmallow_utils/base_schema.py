from marshmallow.schema import BaseSchema as MaSchema
from setup import db, docs


class BaseSchema(MaSchema):
    """
    Base schema auto-attaching the session and keeping track of media resources during load().

    This base schema extends SQLAlchemyAutoSchema to automatically attach the database session
    and handle media resources during data loading.

    Attributes
    ----------
    Meta : Meta
        Configuration class defining the schema's behavior.

    Notes
    -----
    - This schema assumes that 'db' is an instance of SQLAlchemy and is imported correctly.
    - It automatically attaches 'db.session' to the schema if 'session' is not provided in kwargs.
    - Media resources handling during data loading can be extended in subclasses as needed.
    """

    class Meta:
        """
        A class used to represent metadata configuration for a model or component.

        Attributes
        ----------
        required : bool
            Indicates whether this metadata is required. Defaults to True.
        """

        required = True

    def __init__(self, *args, **kwargs):
        r"""
        Initializes the schema instance.

        Parameters
        ----------
        \*args
            Positional arguments passed to SQLAlchemyAutoSchema.
        \**kwargs
            Keyword arguments passed to SQLAlchemyAutoSchema.
        session : Session, optional
            SQLAlchemy session to use for database operations. Value is set to 'db.session' if not found in kwargs
        """
        if not kwargs.get('session'):
            kwargs['session'] = db.session

        super().__init__(*args, **kwargs)
        docs.register_schema(self)

def db_string(length: int = 255, *, nullable: bool = False, primary_key: bool = False, default: str = None, unique: bool = False):
    return {
        'type': 'string',
        'value': (
            f"VARCHAR({length})"
            f"{' NOT NULL' if not nullable else ''}"
            f"{' PRIMARY KEY' if primary_key else ''}"
            f"{' DEFAULT ' + default if default else ''}"
            f"{' UNIQUE' if unique else ''}"
        ),
    }


def db_integer(
    *, nullable: bool = False, primary_key: bool = False, default: int = None, unique: bool = False, auto_increment: bool = False
):
    return {
        'type': 'integer',
        'value': (
            f"INTEGER"
            f"{' NOT NULL' if not nullable else ''}"
            f"{' PRIMARY KEY' if primary_key else ''}"
            f"{' DEFAULT ' + str(default) if default else ''}"
            f"{' UNIQUE' if unique else ''}"
            f"{' AUTO_INCREMENT' if auto_increment else ''}"
        ),
    }


def db_float(*, nullable: bool = False, primary_key: bool = False, default: float = None, unique: bool = False):
    return {
        'type': 'float',
        'value': (
            f"FLOAT"
            f"{' NOT NULL' if not nullable else ''}"
            f"{' PRIMARY KEY' if primary_key else ''}"
            f"{' DEFAULT ' + str(default) if default else ''}"
            f"{' UNIQUE' if unique else ''}"
        ),
    }


def db_boolean(*, nullable: bool = False, primary_key: bool = False, default: bool = None, unique: bool = False):
    return {
        'type': 'boolean',
        'value': (
            f"BOOLEAN"
            f"{' NOT NULL' if not nullable else ''}"
            f"{' PRIMARY KEY' if primary_key else ''}"
            f"{' DEFAULT ' + str(default).upper() if default is not None else ''}"
            f"{' UNIQUE' if unique else ''}"
        ),
    }


def db_date(*, nullable: bool = False, primary_key: bool = False, default: str = None, unique: bool = False):
    return {
        'type': 'date',
        'value': (
            f"DATE"
            f"{' NOT NULL' if not nullable else ''}"
            f"{' PRIMARY KEY' if primary_key else ''}"
            f"{' DEFAULT ' + default if default else ''}"
            f"{' UNIQUE' if unique else ''}"
        ),
    }


def db_uuid(*, nullable: bool = False, primary_key: bool = False, default: str = None, unique: bool = False):
    return {
        'type': 'uuid',
        'value': (
            f"UUID"
            f"{' NOT NULL' if not nullable else ''}"
            f"{' PRIMARY KEY' if primary_key else ''}"
            f"{' DEFAULT ' + default if default else ''}"
            f"{' UNIQUE' if unique else ''}"
        ),
    }


def db_foreign_key(ref_table, ref_field: str, type_field: str):
    if isinstance(ref_table, str):
        arranged_def_table = ref_table.replace('Model', '').lower()
    else:
        arranged_def_table = ref_table.__name__.replace('Model', '').lower()
    return {
        'type': 'foreign_key',
        'value': f'{type_field}',
        'reference': (
            f'ADD CONSTRAINT fk_{arranged_def_table}_{ref_field} ' f'FOREIGN KEY(FIELD) REFERENCES {arranged_def_table} ({ref_field}) '
        ),
    }


def db_relationship(join_field: str):
    return {'type': 'relationship', 'value': join_field}

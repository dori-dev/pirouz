from typing import Union


class Column:
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        self.type = None
        self.unique = unique
        self.nullable = nullable
        self.default = default

    def __repr__(self):
        constraints = ''
        if self.nullable:
            if self.default is not None:
                constraints += f'DEFAULT {self.default}'
        else:
            constraints += 'NOT NULL'
        if self.unique:
            constraints += ' UNIQUE'
        return f'{self.type} {constraints.strip()}'


class Int(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'INT'


class Integer(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'INTEGER'


class TinyInt(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'TINYINT'


class SmallInt(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'SMALLINT'


class MediumInt(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'MEDIUMINT'


class Text(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'TEXT'


class VarChar(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'VARCHAR(255)'


class Blob(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'BLOB'


class Real(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'REAL'


class Double(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'DOUBLE'


class Float(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'FLOAT'


class Numeric(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'NUMERIC'


class Decimal(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'DECIMAL(10,5)'


class Boolean(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'BOOLEAN'


class Date(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'DATE'


class DateTime(Column):
    def __init__(self, unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'DATETIME'


class ForeignKey(Column):
    def __set_name__(self, owner, name):
        self.column_name_ = name

    def __init__(self, reference: Union[object, str], unique: bool = False,
                 nullable: bool = True, default: str = None) -> None:
        super().__init__(unique, nullable, default)
        self.type = 'INTEGER'
        if isinstance(reference, object):
            reference = reference.__name__
        self.reference = reference.lower()

    def get_foreign_key(self):
        name = self.column_name_
        return f'FOREIGN KEY ({name}) REFERENCES {self.reference} (id)'

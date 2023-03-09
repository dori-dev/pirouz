from __future__ import annotations
import os
import sqlite3
import inspect
from typing import Dict, List, NamedTuple, Tuple, Union
from dori_orm.operators import OPERATORS
from dori_orm.columns import ForeignKey


class GenerateTableName:
    def __get__(self, instance, owner) -> str:
        return owner.__name__.lower()


class GenerateDBName:
    def __get__(self, instance, owner) -> str:
        file_address = inspect.getfile(owner)
        db_name = os.path.basename(file_address)[:-3]
        return f"{db_name}.db"


class GetColumns:
    def get_columns(self, owner) -> Tuple[str, str]:
        class_variables: Dict[str, str] = owner.__dict__
        return (
            (key, value)
            for key, value in class_variables.items()
            # remove python magic method from class variables
            if not key.startswith('_')
        )

    def __get__(self, instance, owner) -> Dict[str, str]:
        columns = {
            name.lower(): f"{name.lower()} {value}"
            for name, value in self.get_columns(owner)
        }
        return {
            'id': 'id INTEGER PRIMARY KEY UNIQUE NOT NULL',
            **columns,
        }


class GetForeignKeys:
    def get_foreign_key_columns(self, owner) -> Tuple[str, str]:
        class_variables: Dict[str, str] = owner.__dict__
        return (
            (key, value.get_foreign_key())
            for key, value in class_variables.items()
            if isinstance(value, ForeignKey)
        )

    def __get__(self, instance, owner) -> Dict[str, str]:
        return {
            key: value
            for key, value in self.get_foreign_key_columns(owner)
        }


class Row:
    def __init__(self, db_name_: str, table_name_: str, **data):
        self.data = data
        for key, value in data.items():
            self.__setattr__(key, value)
        Row.db_name = db_name_
        Row.table_name = table_name_

    def remove(self):
        where = ' AND '.join([
            f'{key} = {repr(value)}'
            for key, value in self.data.items()
        ])
        query = f'DELETE FROM {self.table_name} WHERE {where}'
        self._execute(query)

    def update(self, **kwargs):
        where = ' AND '.join([
            f'{key} = {repr(value)}'
            for key, value in self.data.items()
        ])
        new_data = ', '.join([
            f'{key} = {repr(value)}'
            for key, value in kwargs.items()
        ])
        if new_data.strip():
            query = (
                f'UPDATE {self.table_name} SET {new_data} WHERE {where}'
            )
            self._execute(query)

    @ classmethod
    def _execute(cls, query: str):
        conn = sqlite3.connect(cls.db_name)
        conn.execute(query)
        conn.commit()
        conn.close()

    def __repr__(self) -> str:
        result = ', '.join([
            f'{repr(attr)}:{repr(value)}'
            for attr, value in self.data.items()
        ])
        return f"<{result}>"


class Rows:
    def __init__(self, rows: List[Row]):
        self.rows = rows

    def count(self) -> int:
        return len(self.rows)

    def first(self) -> Union[Row, None]:
        if self.rows:
            return self.rows[0]
        return None

    def last(self) -> Union[Row, None]:
        if self.rows:
            return self.rows[-1]
        return None

    def __repr__(self) -> str:
        return repr(self.rows)

    def __iter__(self) -> List[Row]:
        return iter(self.rows)


class ResultConfig(NamedTuple):
    limit: Union[int, None] = None
    order_by: Union[str, None] = None
    reverse: bool = False


class DB:
    db_name = GenerateDBName()
    table_name = GenerateTableName()
    columns = GetColumns()
    foreign_keys = GetForeignKeys()
    _query = ''

    def __init__(self, **data):
        data = {
            'id': self._get_max_id() + 1,
            **data,
        }
        for key, value in data.items():
            if key in self.foreign_keys.keys():
                data[key] = value.id
        self.data = data
        for key, value in data.items():
            self.__setattr__(key, value)
        self.id = self.id  # just for type hinting
        self.insert(**data)

    def __init_subclass__(cls, **kwargs):
        cls._manage_table()

    @classmethod
    def insert(cls, **data: dict):
        fields = ', '.join(data.keys())
        values = ', '.join(
            map(repr, data.values())
        )
        query = (f'INSERT OR IGNORE INTO {cls.table_name} '
                 f'({fields}) VALUES ({values});')
        cls._execute(query)

    @ classmethod
    def all(cls, config: Union[ResultConfig, None] = None) -> List[Row]:
        configs = cls._set_config(config)
        query = f'SELECT * FROM {cls.table_name}{configs};'
        return cls._fetchall(query)

    @ classmethod
    def get(cls, *fields: dict,
            config: Union[ResultConfig, None] = None) -> List[Row]:
        fields = [
            field
            for field in fields
            if field in cls.columns
        ]
        fields_string = ', '.join(fields) or '*'
        configs = cls._set_config(config)
        query = f'SELECT {fields_string} FROM {cls.table_name}{configs};'
        return cls._fetchall(query)

    @ classmethod
    def filter(cls, *args, config: Union[ResultConfig, None] = None,
               **kwargs) -> List[Row]:
        conditions = []
        for key, value in kwargs.items():
            if '__' in key:
                condition = cls._set_operator_filter(key, value)
            else:
                condition = f'{key} = {repr(value)}'
            if condition is not None:
                conditions.append(condition)
                condition = None
        conditions.extend(list(map(repr, args)))
        statements = ' AND '.join(conditions) or 'true'
        configs = cls._set_config(config)
        query = (
            f'SELECT * FROM {cls.table_name} WHERE {statements}{configs};'
        )
        return cls._fetchall(query)

    @ classmethod
    def max(cls, column_name: str):
        query = f'SELECT MAX({column_name}) FROM {cls.table_name};'
        result = cls._fetch_result(query)
        if result:
            return {column_name: result[0]}

    @ classmethod
    def min(cls, column_name: str):
        query = f'SELECT MIN({column_name}) FROM {cls.table_name};'
        result = cls._fetch_result(query)
        if result:
            return {column_name: result[0]}

    @ classmethod
    def avg(cls, column_name: str):
        query = f'SELECT AVG({column_name}) FROM {cls.table_name};'
        result = cls._fetch_result(query)
        if result:
            return {column_name: result[0]}

    @ classmethod
    def sum(cls, column_name: str):
        query = f'SELECT SUM({column_name}) FROM {cls.table_name};'
        result = cls._fetch_result(query)
        if result:
            return {column_name: result[0]}

    @ classmethod
    def count(cls):
        query = f'SELECT COUNT(1) FROM {cls.table_name};'
        result = cls._fetch_result(query)
        if result:
            return {'count': result[0]}

    @classmethod
    def first(cls) -> DB:
        query = f'SELECT * FROM {cls.table_name} WHERE id=1;'
        result = cls._fetch_result(query)
        if result is None:
            return None
        row = dict(zip(cls.columns.keys(), result))
        return Row(cls.db_name, cls.table_name, **row)

    @classmethod
    def last(cls) -> DB:
        max_id = cls._get_max_id()
        query = f'SELECT * FROM {cls.table_name} WHERE id={max_id};'
        result = cls._fetch_result(query)
        if result is None:
            return None
        row = dict(zip(cls.columns.keys(), result))
        return Row(cls.db_name, cls.table_name, **row)

    def remove(self):
        where = ' AND '.join([
            f'{key} = {repr(value)}'
            for key, value in self.data.items()
        ])
        query = f'DELETE FROM {self.table_name} WHERE {where};'
        self._execute(query)

    def update(self, **kwargs):
        where = ' AND '.join([
            f'{key} = {repr(value)}'
            for key, value in self.data.items()
        ])
        new_data = ', '.join([
            f'{key} = {repr(value)}'
            for key, value in kwargs.items()
        ])
        if new_data.strip():
            query = (
                f'UPDATE {self.table_name} SET {new_data} WHERE {where};'
            )
            self._execute(query)
        query = f'SELECT * FROM {self.table_name} WHERE id={self.id};'
        result = self._fetch_result(query)
        data = dict(zip(self.columns.keys(), result))
        self.data = data
        self.__dict__.update(data)

    @ classmethod
    def remove_table(cls):
        query = f'DROP TABLE {cls.table_name}'
        cls._execute(query)

    @ classmethod
    def queries(cls):
        return cls._query.strip()

    @ classmethod
    def _manage_table(cls) -> str:
        try:
            current_columns = cls._get_current_table_columns()
            if current_columns != list(cls.columns.keys()):
                cls._alter_columns(current_columns)
                cls._drop_columns(current_columns)
        except sqlite3.OperationalError:
            cls._create_table()

    @ classmethod
    def _create_table(cls) -> str:
        columns = list(cls.columns.values()).copy()
        foreign_keys = ', '.join(cls.foreign_keys.values())
        if foreign_keys:
            columns.append(foreign_keys)
        string_columns = ', '.join(columns)
        query = (f'CREATE TABLE IF NOT EXISTS {cls.table_name}'
                 f'({string_columns});')
        cls._execute(query)

    @classmethod
    def _alter_columns(cls, current_columns):
        new_columns = [
            value
            for column, value in cls.columns.items()
            if column not in current_columns
        ]
        for field in new_columns:
            query = f'ALTER TABLE {cls.table_name} ADD {field};'
            cls._execute(query)

    @classmethod
    def _drop_columns(cls, current_columns):
        removed_columns = [
            column
            for column in current_columns
            if column not in cls.columns.keys()
        ]
        for field in removed_columns:
            query = f'ALTER TABLE {cls.table_name} DROP {field};'
            cls._execute(query)

    @ staticmethod
    def _set_config(config: Union[ResultConfig, None]) -> str:
        if config is None:
            return ''
        limit, order_by, reverse = config
        if limit is None:
            limit = ''
        else:
            limit = f' LIMIT {limit}'
        if order_by is None:
            order_by = ''
            sorting = ''
        else:
            order_by = F'ORDER BY {order_by}'
            if reverse is False:
                sorting = ' ASC'
            else:
                sorting = ' DESC'
        return f' {order_by}{sorting}{limit}'

    @ staticmethod
    def _set_operator_filter(key: str, value: str):
        filter = key.split('__')
        if len(filter) != 2:
            return None
        key, operator = filter
        key, operator = key.lower(), operator.lower()
        if operator in OPERATORS:
            return (
                f'{key} {OPERATORS[operator]} {repr(value)}'
            )
        elif operator == 'between':
            start, *_, end = value
            return (
                f'{key} BETWEEN {repr(start)} AND {repr(end)}'
            )
        else:
            return None

    @ classmethod
    def _get_max_id(cls):
        query = f'SELECT MAX(id) FROM {cls.table_name}'
        result = cls._fetch_result(query)
        return result[0] or 0

    @ classmethod
    def _execute(cls, query: str):
        cls._query += f"{query}\n\n"
        conn = sqlite3.connect(cls.db_name)
        conn.execute(query)
        conn.commit()
        conn.close()

    @ classmethod
    def _fetchall(cls, query: str) -> Rows:
        cls._query += f"{query}\n\n"
        conn = sqlite3.connect(cls.db_name)
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        result = []
        for row in rows:
            row = dict(zip(
                cls.columns.keys(),
                row
            ))
            result.append(
                Row(cls.db_name, cls.table_name, **row)
            )
        conn.close()
        return Rows(result)

    @ classmethod
    def _fetch_result(cls, query: str):
        cls._query += f"{query}\n\n"
        conn = sqlite3.connect(cls.db_name)
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchone()
        conn.close()
        return result

    @classmethod
    def _get_current_table_columns(cls):
        query = f'SELECT * FROM {cls.table_name}'
        conn = sqlite3.connect(cls.db_name)
        cur = conn.cursor()
        cur.execute(query)
        columns = [description[0] for description in cur.description]
        conn.close()
        return columns

    def __repr__(self) -> str:
        result = ', '.join([
            f'{repr(attr)}:{repr(value)}'
            for attr, value in self.data.items()
        ])
        return f"<{result}>"

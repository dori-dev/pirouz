OPERATORS = {
    'lt': '<',
    'lte': '<=',
    'gt': '>',
    'gte': '>=',
    'n': '!=',
    'in': 'IN',
    'like': 'LIKE',
}


class Operator:
    def __init__(self, *args, **kwargs):
        self.fields = kwargs
        self.args = args
        self.operator = self.__class__.__name__

    def generate_statements(self):
        operator = f' {self.operator} '
        statements = []
        for key, value in self.fields.items():
            if '__' in key:
                statements.append(self._set_operator_filter(key, value))
                continue
            statements.append(f'{key}={repr(value)}')
        args_statements = operator.join(
            map(str, self.args))
        if args_statements:
            statements.append(args_statements)
        return f"({operator.join(statements)})"

    @staticmethod
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

    def __repr__(self) -> str:
        return self.generate_statements()


class AND(Operator):
    pass


class OR(Operator):
    pass


class NOT(Operator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operator = 'AND'

    def __repr__(self) -> str:
        return f"NOT {super().__repr__()}"

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
        statements = [
            f'{key}={repr(value)}'
            for key, value in self.fields.items()
        ]
        args_statements = operator.join(
            map(str, self.args))
        if args_statements:
            statements.append(args_statements)
        return f"({operator.join(statements)})"

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

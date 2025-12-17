class LLMError(Exception):
    pass


class ResponseValidationError(Exception):
    pass


class SqlValidationError(Exception):
    pass


class SqlExecutionError(Exception):
    pass


class InvalidSqlResultError(Exception):
    pass

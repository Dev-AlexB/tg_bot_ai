from sqlglot import exp, parse_one

from errors.errors import SqlValidationError


ALLOWED_AGGREGATES = {
    "COUNT",
    "SUM",
    "AVG",
    "MIN",
    "MAX",
}


class SqlValidator:
    def validate(self, sql: str) -> None:
        tree = self._parse(sql)
        self._check_select_only(tree)
        self._check_no_forbidden_nodes(tree)
        self._check_single_scalar_expression(tree)
        self._check_aggregate(tree)

    def _parse(self, sql: str):
        try:
            return parse_one(sql)
        except Exception as e:
            raise SqlValidationError(f"Invalid SQL syntax: {e}")

    def _check_select_only(self, tree):
        if not isinstance(tree, exp.Select):
            raise SqlValidationError("Only SELECT queries are allowed")

    def _check_no_forbidden_nodes(self, tree):
        forbidden = (
            exp.Insert,
            exp.Update,
            exp.Delete,
            exp.Drop,
            exp.Alter,
            exp.Union,
            exp.Subquery,
            exp.With,
        )
        if tree.find(forbidden):
            raise SqlValidationError("Forbidden SQL construct detected")

    def _check_single_scalar_expression(self, tree):
        if len(tree.expressions) != 1:
            raise SqlValidationError(
                "Only one expression in SELECT is allowed"
            )

    def _check_aggregate(self, tree):
        aggregates = [
            node for node in tree.walk() if isinstance(node, exp.AggFunc)
        ]
        if not aggregates:
            raise SqlValidationError("Aggregate function is required")

        for agg in aggregates:
            if agg.sql_name().upper() not in ALLOWED_AGGREGATES:
                raise SqlValidationError(
                    f"Aggregate {agg.sql_name()} is not allowed"
                )

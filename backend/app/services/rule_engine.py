import ast
import operator

from ..models import TransferSimulation
from ..reason_codes import ReasonCode


class RuleEvaluationError(ValueError):
    pass


class SafeExpressionEvaluator:
    binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
    }
    unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
    }
    compare_ops = {
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
    }

    def __init__(self, fields: dict):
        self.fields = fields

    def evaluate(self, expression: str) -> bool:
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise RuleEvaluationError(str(exc)) from exc
        return bool(self._eval(tree.body))

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, bool, str)) or node.value is None:
                return node.value
            raise RuleEvaluationError("Unsupported literal")
        if isinstance(node, ast.Name):
            if node.id not in self.fields:
                raise RuleEvaluationError(f"Unknown field: {node.id}")
            return self.fields[node.id]
        if isinstance(node, ast.BinOp):
            op = self.binary_ops.get(type(node.op))
            if op is None:
                raise RuleEvaluationError("Unsupported arithmetic operator")
            return op(self._eval(node.left), self._eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op = self.unary_ops.get(type(node.op))
            if op is None:
                raise RuleEvaluationError("Unsupported unary operator")
            return op(self._eval(node.operand))
        if isinstance(node, ast.BoolOp):
            values = [bool(self._eval(value)) for value in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
            raise RuleEvaluationError("Unsupported boolean operator")
        if isinstance(node, ast.Compare):
            left = self._eval(node.left)
            for op_node, comparator in zip(node.ops, node.comparators):
                op = self.compare_ops.get(type(op_node))
                if op is None:
                    raise RuleEvaluationError("Unsupported comparison operator")
                right = self._eval(comparator)
                if not op(left, right):
                    return False
                left = right
            return True
        raise RuleEvaluationError("Unsupported expression")


def evaluate_custom_rules(
    sim: TransferSimulation,
    custom_rules: list[dict] | None,
) -> list[ReasonCode]:
    if not custom_rules:
        return []

    evaluator = SafeExpressionEvaluator(sim.model_dump())
    violations: list[ReasonCode] = []
    for rule in custom_rules:
        condition = str(rule.get("condition", "")).strip()
        if not condition:
            continue
        if not evaluator.evaluate(condition):
            continue
        reason_code = str(rule.get("reason_code", ReasonCode.CUSTOM.value))
        try:
            violations.append(ReasonCode(reason_code))
        except ValueError:
            violations.append(ReasonCode.CUSTOM)
    return violations

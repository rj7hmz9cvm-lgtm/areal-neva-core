import os
import ast
import operator

_ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY_OPS = {
    ast.USub: operator.neg,
    ast.UAdd: lambda x: x,
}

def _max_abs_value() -> float:
    return float(os.getenv("MAX_MATH_ABS_VALUE", "1000000000"))

def _max_abs_result() -> float:
    return float(os.getenv("MAX_MATH_ABS_RESULT", "1000000000"))

def _check_number(value):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError("Only int/float allowed")
    if abs(value) > _max_abs_value():
        raise ValueError("Value exceeds safe bounds")
    return value

def _safe_eval_node(node):
    if isinstance(node, ast.Constant):
        return _check_number(node.value)

    if isinstance(node, ast.BinOp):
        if type(node.op) not in _ALLOWED_BIN_OPS:
            raise TypeError(f"Unsupported op: {type(node.op).__name__}")
        left = _safe_eval_node(node.left)
        right = _safe_eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 20:
            raise ValueError("Exponent out of bounds")
        result = _ALLOWED_BIN_OPS[type(node.op)](left, right)
        if abs(result) > _max_abs_result():
            raise ValueError("Result exceeds bounds")
        return result

    if isinstance(node, ast.UnaryOp):
        if type(node.op) not in _ALLOWED_UNARY_OPS:
            raise TypeError(f"Unsupported unary: {type(node.op).__name__}")
        result = _ALLOWED_UNARY_OPS[type(node.op)](_safe_eval_node(node.operand))
        if abs(result) > _max_abs_result():
            raise ValueError("Result exceeds bounds")
        return result

    raise TypeError(f"Unsupported syntax: {type(node).__name__}")

def process_math(expression: str) -> str:
    if os.getenv("MATH_SAFE_MODE", "1") != "1":
        return "SYS_SKIP: MATH_DISABLED"

    expr = str(expression or "").strip()
    if not expr:
        return "MATH_ERROR: Empty expression"

    if len(expr) > int(os.getenv("MAX_MATH_EXPR_LEN", "100")):
        return "MATH_ERROR: Expression too long"

    try:
        return str(_safe_eval_node(ast.parse(expr, mode="eval").body))
    except Exception as e:
        return f"MATH_ERROR: {e}"

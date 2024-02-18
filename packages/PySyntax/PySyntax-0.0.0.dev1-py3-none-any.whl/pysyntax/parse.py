from typing import Any as _Any
import ast as _ast


def function_call(code: str) -> tuple[str, dict[str, _Any]]:
    """
    Parse a Python function call from a string.

    Parameters
    ----------
    code : str
        The code to parse.

    Returns
    -------
    tuple[str, dict[str, Any]]
        A tuple containing the function name and a dictionary of keyword arguments.
    """

    class CallVisitor(_ast.NodeVisitor):

        def visit_Call(self, node):
            # Function name
            self.func_name = getattr(node.func, 'id', None)
            # Keyword arguments
            self.args = {arg.arg: self._arg_value(arg.value) for arg in node.keywords}

        def _arg_value(self, node):
            if isinstance(node, _ast.Constant):
                return node.value
            elif isinstance(node, (_ast.List, _ast.Tuple, _ast.Dict)):
                return _ast.literal_eval(node)
            return "Complex value"  # Placeholder for complex expressions

    tree = _ast.parse(code)
    visitor = CallVisitor()
    visitor.visit(tree)
    return visitor.func_name, visitor.args

from __future__ import annotations

import ast
from collections import OrderedDict


class VariableVisitor(ast.NodeVisitor):
    def __init__(self):
        self.variables: OrderedDict[str, None] = OrderedDict()
        self.processed_variables: set[str] = set()
        self.function_calls: set[str] = set()
        self.function_call_args: set[str] = set()
        self.function_call_kwargs: set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self.extract_variables_from_target(target)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        var_name = node.id
        # get functions args and kwargs
        args_kwargs = self.function_call_args.union(self.function_call_kwargs)
        if var_name not in self.processed_variables and var_name not in args_kwargs:
            self.variables[var_name] = None
            self.processed_variables.add(var_name)
        self.generic_visit(node)

    def extract_variables_from_target(self, target: ast.expr) -> None:
        if isinstance(target, ast.Constant):
            return
        if isinstance(target, ast.Name):
            self.visit_Name(target)
        elif isinstance(target, ast.Tuple):
            for element in target.elts:
                if isinstance(element, ast.Name):
                    self.visit_Name(element)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            # Record function calls and get function args, kwargs
            args = node.args + node.keywords
            for arg in args:
                try:
                    self.function_call_args.add(arg.id)  # pyright: ignore[reportAttributeAccessIssue]
                except AttributeError:
                    pass
            self.function_calls.add(node.func.id)
        self.generic_visit(node)

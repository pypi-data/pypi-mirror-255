import ast


def is_transaction(statement: ast.AST) -> bool:
    if not isinstance(statement, ast.AsyncFunctionDef | ast.FunctionDef):
        return False

    if not statement.decorator_list:
        return False

    return any(
        decorator
        for decorator in statement.decorator_list
        if (
            (isinstance(decorator, ast.Name) and decorator.id == 'transaction')
            or (
                isinstance(decorator, ast.Call)
                and isinstance(
                    decorator.func,
                    ast.Name,
                )
                and decorator.func.id == 'transaction'
            )
        )
    )

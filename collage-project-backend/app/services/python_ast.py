import ast


def parse_python_code(source_code: str):
    """
    Convert Python source code into an Abstract Syntax Tree.
    """

    try:
        return ast.parse(source_code)

    except SyntaxError as e:
        raise ValueError(f"Invalid Python code: {e}")


def normalize_ast(tree):
    """
    Convert an AST into a normalized structural token sequence.
    """

    tokens = []

    def visit(node):

        if isinstance(node, ast.FunctionDef):
            tokens.append("FUNCTION")

        elif isinstance(node, ast.AsyncFunctionDef):
            tokens.append("FUNCTION")

        elif isinstance(node, ast.ClassDef):
            tokens.append("CLASS")

        elif isinstance(node, ast.Name):
            tokens.append("VAR")

        elif isinstance(node, ast.arg):
            tokens.append("ARG")

        elif isinstance(node, ast.Constant):

            if isinstance(node.value, bool):
                tokens.append("BOOL")

            elif isinstance(node.value, (int, float, complex)):
                tokens.append("NUM")

            elif isinstance(node.value, str):
                tokens.append("STR")

            elif node.value is None:
                tokens.append("NONE")

            else:
                tokens.append("CONST")

        else:
            tokens.append(type(node).__name__)

        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)

    return tokens
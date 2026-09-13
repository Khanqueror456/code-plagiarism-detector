import re


LANGUAGE_KEYWORDS = {
    "python": {
        "def": "FUNCTION",
        "class": "CLASS",
        "return": "RETURN",
        "if": "IF",
        "else": "ELSE",
        "elif": "ELSE_IF",
        "for": "FOR",
        "while": "WHILE",
        "in": "IN",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "True": "BOOL",
        "False": "BOOL",
        "None": "NULL",
    },

    "java": {
        "public": "ACCESS",
        "private": "ACCESS",
        "protected": "ACCESS",
        "static": "STATIC",
        "class": "CLASS",
        "return": "RETURN",
        "if": "IF",
        "else": "ELSE",
        "for": "FOR",
        "while": "WHILE",
        "true": "BOOL",
        "false": "BOOL",
        "null": "NULL",
        "int": "TYPE",
        "long": "TYPE",
        "double": "TYPE",
        "float": "TYPE",
        "boolean": "TYPE",
        "void": "TYPE",
    },

    "javascript": {
        "function": "FUNCTION",
        "class": "CLASS",
        "return": "RETURN",
        "if": "IF",
        "else": "ELSE",
        "for": "FOR",
        "while": "WHILE",
        "true": "BOOL",
        "false": "BOOL",
        "null": "NULL",
        "let": "DECL",
        "const": "DECL",
        "var": "DECL",
    },

    "cpp": {
        "class": "CLASS",
        "return": "RETURN",
        "if": "IF",
        "else": "ELSE",
        "for": "FOR",
        "while": "WHILE",
        "true": "BOOL",
        "false": "BOOL",
        "nullptr": "NULL",
        "int": "TYPE",
        "long": "TYPE",
        "double": "TYPE",
        "float": "TYPE",
        "bool": "TYPE",
        "void": "TYPE",
    },

    "c": {
        "return": "RETURN",
        "if": "IF",
        "else": "ELSE",
        "for": "FOR",
        "while": "WHILE",
        "int": "TYPE",
        "long": "TYPE",
        "double": "TYPE",
        "float": "TYPE",
        "char": "TYPE",
        "void": "TYPE",
        "true": "BOOL",
        "false": "BOOL",
    },
}


TOKEN_PATTERN = re.compile(
    r"""
    //.*?$ |
    \#.*?$ |
    /\*.*?\*/ |
    "(?:\\.|[^"\\])*" |
    '(?:\\.|[^'\\])*' |
    \b\d+(?:\.\d+)?\b |
    \b[A-Za-z_][A-Za-z0-9_]*\b |
    ==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|&&|\|\| |
    [+\-*/%=<>]
    """,
    re.MULTILINE | re.DOTALL | re.VERBOSE,
)


def get_semantic_tokens(code: str, language: str) -> list[str]:

    language = language.lower()

    keyword_map = LANGUAGE_KEYWORDS.get(language, {})

    raw_tokens = TOKEN_PATTERN.findall(code)

    result = []

    for token in raw_tokens:

        token = token.strip()

        if not token:
            continue

        # Comments
        if (
            token.startswith("//")
            or token.startswith("#")
            or token.startswith("/*")
        ):
            continue

        # Strings
        if token.startswith('"') or token.startswith("'"):
            result.append("STR")
            continue

        # Numbers
        if re.fullmatch(r"\d+(?:\.\d+)?", token):
            result.append("NUM")
            continue

        # Keywords
        if token in keyword_map:
            result.append(keyword_map[token])
            continue

        # Operators
        operator_map = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "%": "MOD",
            "=": "ASSIGN",
            "==": "COMPARE",
            "!=": "COMPARE",
            "<": "COMPARE",
            ">": "COMPARE",
            "<=": "COMPARE",
            ">=": "COMPARE",
            "+=": "ADD_ASSIGN",
            "-=": "SUB_ASSIGN",
            "*=": "MUL_ASSIGN",
            "/=": "DIV_ASSIGN",
            "&&": "AND",
            "||": "OR",
        }

        if token in operator_map:
            result.append(operator_map[token])
            continue

        # Everything else that looks like an identifier
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token):
            result.append("VAR")
            continue

    return result
import re
from difflib import SequenceMatcher

# --------------------------------------------------
# KEYWORDS BY LANGUAGE
# --------------------------------------------------

LANGUAGE_KEYWORDS = {
    "python": {
        "def",
        "return",
        "if",
        "else",
        "elif",
        "for",
        "while",
        "in",
        "not",
        "and",
        "or",
        "True",
        "False",
        "None",
        "class",
        "import",
        "from",
        "as",
        "try",
        "except",
        "finally",
        "with",
        "lambda",
        "yield",
        "break",
        "continue",
        "pass",
        "raise",
        "is",
        "async",
        "await",
    },
    "java": {
        "public",
        "private",
        "protected",
        "static",
        "final",
        "class",
        "interface",
        "extends",
        "implements",
        "new",
        "return",
        "if",
        "else",
        "for",
        "while",
        "do",
        "switch",
        "case",
        "break",
        "continue",
        "try",
        "catch",
        "finally",
        "throw",
        "throws",
        "import",
        "package",
        "this",
        "true",
        "false",
        "null",
        "void",
        "int",
        "long",
        "float",
        "double",
        "boolean",
        "char",
        "byte",
        "short",
    },
    "javascript": {
        "function",
        "return",
        "if",
        "else",
        "for",
        "while",
        "do",
        "switch",
        "case",
        "break",
        "continue",
        "class",
        "extends",
        "new",
        "const",
        "let",
        "var",
        "import",
        "export",
        "from",
        "try",
        "catch",
        "finally",
        "throw",
        "async",
        "await",
        "true",
        "false",
        "null",
        "undefined",
    },
    "cpp": {
        "class",
        "struct",
        "public",
        "private",
        "protected",
        "static",
        "const",
        "return",
        "if",
        "else",
        "for",
        "while",
        "do",
        "switch",
        "case",
        "break",
        "continue",
        "new",
        "delete",
        "try",
        "catch",
        "throw",
        "true",
        "false",
        "nullptr",
        "void",
        "int",
        "long",
        "float",
        "double",
        "char",
        "bool",
        "short",
        "unsigned",
        "signed",
        "include",
        "using",
        "namespace",
    },
    "c": {
        "struct",
        "static",
        "const",
        "return",
        "if",
        "else",
        "for",
        "while",
        "do",
        "switch",
        "case",
        "break",
        "continue",
        "sizeof",
        "typedef",
        "void",
        "int",
        "long",
        "float",
        "double",
        "char",
        "short",
        "unsigned",
        "signed",
    },
}


# --------------------------------------------------
# BUILT-IN FUNCTIONS
# --------------------------------------------------

BUILTINS = {
    "print",
    "len",
    "range",
    "str",
    "int",
    "float",
    "list",
    "dict",
    "set",
    "sum",
    "max",
    "min",
    "abs",
    "open",
    "System",
    "println",
    "console",
    "log",
    "printf",
    "scanf",
}


# --------------------------------------------------
# TOKENIZE
# --------------------------------------------------


def tokenize_code(code):
    """
    Convert source code into lexical tokens.
    """

    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[^\s\w]", code)


# --------------------------------------------------
# NORMALIZE TOKENS
# --------------------------------------------------


def normalize_lexical_tokens(tokens, language="python"):
    """
    Normalize lexical tokens into language-independent
    representations.

    Example:

        Python:
            def add(a, b)

        JavaScript:
            function add(a, b)

    become structurally similar.
    """

    language = language.lower()

    keywords = LANGUAGE_KEYWORDS.get(language, set())

    normalized = []

    function_name_next = False
    inside_parameters = False
    parameter_depth = 0

    for token in tokens:

        # ------------------------------------------
        # FUNCTION DECLARATION
        # ------------------------------------------

        if token in {"def", "function"}:

            normalized.append("FUNCTION")
            function_name_next = True

            continue

        # ------------------------------------------
        # FUNCTION NAME
        # ------------------------------------------

        if function_name_next:

            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):

                normalized.append("FUNC_NAME")

                function_name_next = False

                continue

            # The token right after 'def'/'function' was not a valid
            # identifier (e.g. an anonymous JS function like
            # `function(a, b) {...}`). Clear the flag here so it
            # doesn't stay stuck "True" and mis-tag a later, unrelated
            # identifier as FUNC_NAME.
            function_name_next = False

        # ------------------------------------------
        # PARAMETERS
        # ------------------------------------------

        if token == "(":

            normalized.append("(")

            if function_name_next is False:

                # We cannot always know whether this
                # is a function call or parameter list.
                # Keep the punctuation for now.
                pass

            continue

        # ------------------------------------------
        # LANGUAGE KEYWORDS
        # ------------------------------------------

        if token in keywords:

            # Normalize control-flow keywords.

            if token in {"return"}:
                normalized.append("RETURN")

            elif token in {"if"}:
                normalized.append("IF")

            elif token in {"else", "elif"}:
                normalized.append("ELSE")

            elif token in {"for"}:
                normalized.append("FOR")

            elif token in {"while"}:
                normalized.append("WHILE")

            elif token in {"class"}:
                normalized.append("CLASS")

            elif token in {"true", "True"}:
                normalized.append("BOOL")

            elif token in {"false", "False"}:
                normalized.append("BOOL")

            elif token in {"null", "None", "nullptr"}:
                normalized.append("NONE")

            # Types are normalized.

            elif token in {
                "int",
                "long",
                "float",
                "double",
                "boolean",
                "bool",
                "char",
                "short",
                "byte",
                "void",
            }:
                normalized.append("TYPE")

            # Other keywords retain a generic marker.

            else:
                normalized.append("KEYWORD")

            continue

        # ------------------------------------------
        # NUMBERS
        # ------------------------------------------

        if token.isdigit():

            normalized.append("NUM")

            continue

        # ------------------------------------------
        # BUILT-IN FUNCTIONS
        # ------------------------------------------

        if token in BUILTINS:

            normalized.append("BUILTIN")

            continue

        # ------------------------------------------
        # IDENTIFIERS
        # ------------------------------------------

        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", token):

            normalized.append("IDENTIFIER")

            continue

        # ------------------------------------------
        # OPERATORS
        # ------------------------------------------


        if token in {
            "+",
            "-",
            "*",
            "/",
            "%",
            "=",
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">=",
            "&&",
            "||",
        }:

            # Preserve the actual operator.
            # This allows + and * to remain
            # distinguishable during comparison.
            normalized.append(f"OP_{token}")

            continue

            # ------------------------------------------
            # OTHER SYMBOLS
            # ------------------------------------------

        normalized.append(token)

    return normalized


# --------------------------------------------------
# TOKEN SIMILARITY
# --------------------------------------------------


def calculate_token_similarity(tokens_a, tokens_b):

    if not tokens_a or not tokens_b:
        return 0.0

    return SequenceMatcher(None, tokens_a, tokens_b).ratio()


# --------------------------------------------------
# LINE COUNT
# --------------------------------------------------


def count_lines(code):

    return len([line for line in code.splitlines() if line.strip()])


def calculate_line_ratio(code_a, code_b):

    lines_a = count_lines(code_a)
    lines_b = count_lines(code_b)

    if lines_a == 0 and lines_b == 0:
        return 1.0

    if lines_a == 0 or lines_b == 0:
        return 0.0

    return min(lines_a, lines_b) / max(lines_a, lines_b)


# --------------------------------------------------
# TOKEN COUNT RATIO
# --------------------------------------------------


def calculate_token_ratio(tokens_a, tokens_b):

    if not tokens_a and not tokens_b:
        return 1.0

    if not tokens_a or not tokens_b:
        return 0.0

    return min(len(tokens_a), len(tokens_b)) / max(len(tokens_a), len(tokens_b))
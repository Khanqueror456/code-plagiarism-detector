from tree_sitter_language_pack import get_parser


SUPPORTED_LANGUAGES = {
    "python",
    "java",
    "javascript",
    "cpp",
    "c"
}


EXTENSION_TO_LANGUAGE = {
    ".py": "python",

    ".java": "java",

    ".js": "javascript",
    ".jsx": "javascript",

    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",

    ".c": "c"
}


def detect_language_from_extension(filename):
    filename = filename.lower()

    for extension, language in EXTENSION_TO_LANGUAGE.items():

        if filename.endswith(extension):
            return language

    raise ValueError(
        f"Unsupported file type: {filename}"
    )


def validate_language(language):

    language = language.lower()

    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language: {language}"
        )

    return language


def parse_source_code(
    source_code,
    language
):

    language = validate_language(
        language
    )

    try:

        parser = get_parser(
            language
        )

        tree = parser.parse(
            source_code.encode("utf-8")
        )

        return tree

    except Exception as e:

        raise ValueError(
            f"Unable to parse {language} code: {e}"
        )


# --------------------------------------------------
# LANGUAGE-INDEPENDENT NORMALIZATION
# --------------------------------------------------

def normalize_tree(tree):
    """
    Convert a Tree-sitter AST into a
    language-independent structural representation.
    """

    tokens = []

    def visit(node):

        node_type = node.type.lower()

        # ------------------------------------------
        # IDENTIFIERS
        # ------------------------------------------

        if node_type in {
            "identifier",
            "type_identifier",
            "field_identifier",
            "property_identifier"
        }:

            tokens.append("IDENTIFIER")

        # ------------------------------------------
        # NUMBERS
        # ------------------------------------------

        elif any(
            word in node_type
            for word in [
                "integer",
                "number",
                "float",
                "double",
                "decimal"
            ]
        ):

            tokens.append("NUM")

        # ------------------------------------------
        # STRINGS
        # ------------------------------------------

        elif (
            "string" in node_type
            or "template_string" in node_type
        ):

            tokens.append("STR")

        # ------------------------------------------
        # BOOLEAN
        # ------------------------------------------

        elif node_type in {
            "true",
            "false",
            "true_literal",
            "false_literal"
        }:

            tokens.append("BOOL")

        # ------------------------------------------
        # NULL / NONE
        # ------------------------------------------

        elif node_type in {
            "null",
            "null_literal",
            "none"
        }:

            tokens.append("NONE")

        # ------------------------------------------
        # COMMENTS
        # ------------------------------------------

        elif node_type in {
            "comment",
            "line_comment",
            "block_comment"
        }:

            pass

        # ------------------------------------------
        # FUNCTIONS / METHODS
        # ------------------------------------------

        elif any(
            word in node_type
            for word in [
                "function_definition",
                "function_declaration",
                "method_declaration",
                "method_definition"
            ]
        ):

            tokens.append("FUNCTION")

        # ------------------------------------------
        # CLASSES
        # ------------------------------------------

        elif any(
            word in node_type
            for word in [
                "class_definition",
                "class_declaration"
            ]
        ):

            tokens.append("CLASS")

        # ------------------------------------------
        # RETURN
        # ------------------------------------------

        elif "return_statement" in node_type:

            tokens.append("RETURN")

        # ------------------------------------------
        # IF
        # ------------------------------------------

        elif (
            node_type == "if_statement"
            or node_type == "if"
        ):

            tokens.append("IF")

        # ------------------------------------------
        # ELSE
        # ------------------------------------------

        elif (
            node_type == "else_clause"
            or node_type == "else"
        ):

            tokens.append("ELSE")

        # ------------------------------------------
        # FOR LOOP
        # ------------------------------------------

        elif (
            node_type == "for_statement"
            or node_type == "for_in_statement"
            or node_type == "for"
        ):

            tokens.append("FOR")

        # ------------------------------------------
        # WHILE LOOP
        # ------------------------------------------

        elif (
            node_type == "while_statement"
            or node_type == "while"
        ):

            tokens.append("WHILE")

        # ------------------------------------------
        # ASSIGNMENT
        # ------------------------------------------

        elif (
            "assignment" in node_type
            or node_type in {
                "variable_declarator",
                "init_declarator"
            }
        ):

            tokens.append("ASSIGNMENT")

        # ------------------------------------------
        # FUNCTION CALL
        # ------------------------------------------

        elif (
            "call" in node_type
            or "invocation" in node_type
        ):

            tokens.append("CALL")

        # ------------------------------------------
        # BINARY OPERATIONS
        # ------------------------------------------

        elif (
            "binary_expression" in node_type
            or "binary_operator" in node_type
        ):

            tokens.append("BINARY_OP")

        # ------------------------------------------
        # BLOCKS
        # ------------------------------------------

        elif node_type in {
            "block",
            "statement_block",
            "compound_statement",
            "class_body"
        }:

            tokens.append("BLOCK")

        # ------------------------------------------
        # PARAMETERS
        # ------------------------------------------

        elif (
            "parameter" in node_type
            or "parameters" in node_type
        ):

            tokens.append("PARAMETERS")

        # ------------------------------------------
        # PROGRAM ROOT
        # ------------------------------------------

        elif node_type in {
            "module",
            "program",
            "translation_unit"
        }:

            tokens.append("PROGRAM")

        # ------------------------------------------
        # OPERATORS
        # ------------------------------------------

        elif node_type in {
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
            "||"
        }:

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
                "&&": "AND",
                "||": "OR"
            }

            tokens.append(
                operator_map[node_type]
            )

        # ------------------------------------------
        # OTHER STRUCTURAL NODES
        # ------------------------------------------

        else:

            if node_type not in {
                "(",
                ")",
                "{",
                "}",
                "[",
                "]",
                ",",
                ";",
                ":"
            }:

                tokens.append(
                    node_type.upper()
                )

        # Visit children

        for child in node.children:
            visit(child)

    visit(
        tree.root_node
    )

    return tokens


def get_normalized_structure(
    source_code,
    language
):

    tree = parse_source_code(
        source_code,
        language
    )

    return normalize_tree(
        tree
    )
from difflib import SequenceMatcher
from collections import Counter
import math
import re


from app.services.python_ast import (
    parse_python_code,
    normalize_ast
)


from app.services.winnowing import (
    generate_semantic_fingerprints,
    calculate_jaccard_similarity,
    calculate_containment_similarity
)


from app.services.lexical_similarity import (
    tokenize_code,
    normalize_lexical_tokens,
    calculate_token_similarity,
    calculate_line_ratio,
    calculate_token_ratio
)


from app.services.matching_regions import (
    find_matching_regions
)


from app.services.multi_language_parser import (
    get_parser,
    get_normalized_structure
)


# =========================================================
# BASIC HELPERS
# =========================================================

def safe_ratio(a, b):
    """
    Compare two quantities using a symmetric ratio.

    Example:
        10 vs 10 -> 1.0
        10 vs 5  -> 0.5
        5 vs 10  -> 0.5
    """

    if max(a, b) == 0:
        return 1.0

    return min(a, b) / max(a, b)


# =========================================================
# ORIGINAL PYTHON AST SIMILARITY
# =========================================================

def calculate_python_ast_similarity(
    code_a,
    code_b
):
    """
    Calculate structural AST similarity for Python code.

    Variable names are normalized by python_ast.py,
    so renamed variables do not reduce structural similarity.
    """

    try:

        tree_a = parse_python_code(
            code_a
        )

        tree_b = parse_python_code(
            code_b
        )

        normalized_a = normalize_ast(
            tree_a
        )

        normalized_b = normalize_ast(
            tree_b
        )

        matcher = SequenceMatcher(
            None,
            normalized_a,
            normalized_b
        )

        return matcher.ratio()

    except Exception:

        return 0.0


# =========================================================
# TREE-SITTER AST
# =========================================================

def get_ast_statistics(
    code,
    language
):
    """
    Extract basic AST statistics using Tree-sitter.

    Returns:
        {
            "node_count": int,
            "max_depth": int
        }
    """

    try:

        parser = get_parser(
            language
        )

        tree = parser.parse(
            code.encode("utf-8")
        )

        root = tree.root_node

        node_count = 0
        max_depth = 0

        def walk(
            node,
            depth
        ):

            nonlocal node_count
            nonlocal max_depth

            node_count += 1

            max_depth = max(
                max_depth,
                depth
            )

            for child in node.children:

                walk(
                    child,
                    depth + 1
                )

        walk(
            root,
            0
        )

        return {
            "node_count": node_count,
            "max_depth": max_depth
        }

    except Exception:

        return {
            "node_count": 0,
            "max_depth": 0
        }


# =========================================================
# AST NODE SIMILARITY
# =========================================================

def calculate_ast_node_similarity(
    code_a,
    code_b,
    language_a,
    language_b
):
    """
    Compare the number of AST nodes in both programs.

    Similar programs generally have similar structural
    complexity and therefore similar AST node counts.
    """

    stats_a = get_ast_statistics(
        code_a,
        language_a
    )

    stats_b = get_ast_statistics(
        code_b,
        language_b
    )

    return safe_ratio(
        stats_a["node_count"],
        stats_b["node_count"]
    )


# =========================================================
# AST DEPTH SIMILARITY
# =========================================================

def calculate_ast_depth_similarity(
    code_a,
    code_b,
    language_a,
    language_b
):
    """
    Compare maximum AST depth.

    Similar implementations often have similar
    structural nesting depth.
    """

    stats_a = get_ast_statistics(
        code_a,
        language_a
    )

    stats_b = get_ast_statistics(
        code_b,
        language_b
    )

    return safe_ratio(
        stats_a["max_depth"],
        stats_b["max_depth"]
    )


# =========================================================
# OPERATOR SIMILARITY
# =========================================================

OPERATOR_PATTERN = re.compile(
    r"""
    ===|!==|==|!=|<=|>=|&&|\|\|
    |\+\+|--|\+=|-=|\*=|/=|%=
    |->|<<|>>
    |[+\-*/%<>=!&|^~]
    """,
    re.VERBOSE
)


def get_operator_tokens(
    code
):
    """
    Extract operators from source code.
    """

    return OPERATOR_PATTERN.findall(
        code
    )


def calculate_operator_similarity(
    code_a,
    code_b
):
    """
    Compare operator distributions using
    multiset Jaccard similarity.

    This helps distinguish programs such as:

        a + b

    from:

        a * b
    """

    operators_a = get_operator_tokens(
        code_a
    )

    operators_b = get_operator_tokens(
        code_b
    )

    if not operators_a and not operators_b:

        return 1.0

    if not operators_a or not operators_b:

        return 0.0

    counter_a = Counter(
        operators_a
    )

    counter_b = Counter(
        operators_b
    )

    all_operators = (
        set(counter_a)
        |
        set(counter_b)
    )

    intersection = 0
    union = 0

    for operator in all_operators:

        count_a = counter_a.get(
            operator,
            0
        )

        count_b = counter_b.get(
            operator,
            0
        )

        intersection += min(
            count_a,
            count_b
        )

        union += max(
            count_a,
            count_b
        )

    if union == 0:

        return 1.0

    return intersection / union


# =========================================================
# TF-IDF / COSINE SIMILARITY
# =========================================================

def tokenize_for_tfidf(
    code,
    language
):
    """
    Tokenize code for TF-IDF comparison.

    Comments are removed and identifiers/operators/
    keywords are preserved as textual features.
    """

    # -----------------------------------------------------
    # REMOVE COMMENTS
    # -----------------------------------------------------

    code = re.sub(
        r"//.*",
        " ",
        code
    )

    code = re.sub(
        r"/\*[\s\S]*?\*/",
        " ",
        code
    )

    code = re.sub(
        r"#.*",
        " ",
        code
    )

    # -----------------------------------------------------
    # TOKENIZE
    # -----------------------------------------------------

    tokens = re.findall(
        r"""
        [A-Za-z_][A-Za-z0-9_]*
        |\d+(?:\.\d+)?
        |===|!==|==|!=|<=|>=
        |&&|\|\|
        |\+\+|--
        |\+=|-=|\*=|/=|%=
        |->|<<|>>
        |[+\-*/%<>=!&|^~]
        """,
        code,
        re.VERBOSE
    )

    return [
        token.lower()
        for token in tokens
    ]


def calculate_tfidf_similarity(
    code_a,
    code_b,
    language_a="python",
    language_b="python"
):
    """
    Calculate cosine similarity between TF-IDF vectors
    of two code snippets.

    language_a and language_b are accepted for compatibility
    with the multi-language comparison pipeline.
    """

    tokens_a = tokenize_for_tfidf(code_a, language_a)
    tokens_b = tokenize_for_tfidf(code_b, language_b)

    if not tokens_a or not tokens_b:
        return 0.0

    # Build vocabulary
    vocabulary = sorted(
        set(tokens_a) | set(tokens_b)
    )

    # Term Frequency
    def term_frequency(tokens):
        counts = Counter(tokens)
        total = len(tokens)

        return {
            token: counts[token] / total
            for token in vocabulary
        }

    tf_a = term_frequency(tokens_a)
    tf_b = term_frequency(tokens_b)

    # Document Frequency
    df = {}

    for token in vocabulary:
        df[token] = (
            int(token in tokens_a) +
            int(token in tokens_b)
        )

    # Inverse Document Frequency
    total_documents = 2

    idf = {
        token: math.log(
            (total_documents + 1) /
            (df[token] + 1)
        ) + 1
        for token in vocabulary
    }

    # TF-IDF vectors
    vector_a = [
        tf_a[token] * idf[token]
        for token in vocabulary
    ]

    vector_b = [
        tf_b[token] * idf[token]
        for token in vocabulary
    ]

    # Dot product
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    # Vector magnitudes
    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    # Cosine similarity
    similarity = (
        dot_product /
        (magnitude_a * magnitude_b)
    )

    # Protect against tiny floating-point errors
    return max(0.0, min(1.0, similarity))


# =========================================================
# NORMALIZED TREE STRUCTURE SIMILARITY
# =========================================================

def calculate_normalized_structure_similarity(
    code_a,
    code_b,
    language_a,
    language_b
):
    """
    Compare language-independent Tree-sitter
    structural representations.

    This is not currently used as one of the
    ten ML features, but is useful internally
    and can be used for debugging.
    """

    try:

        structure_a = get_normalized_structure(
            code_a,
            language_a
        )

        structure_b = get_normalized_structure(
            code_b,
            language_b
        )

        if not structure_a and not structure_b:

            return 1.0

        if not structure_a or not structure_b:

            return 0.0

        return SequenceMatcher(
            None,
            structure_a,
            structure_b
        ).ratio()

    except Exception:

        return 0.0


# =========================================================
# MAIN COMPARISON
# =========================================================

def compare_code(
    code_a,
    code_b,
    language_a="python",
    language_b="python"
):
    """
    Compare two source-code programs.

    Features returned:

        1. ast_similarity
        2. winnowing_similarity
        3. token_similarity
        4. line_ratio
        5. token_ratio
        6. matched_fingerprints
        7. fingerprint_containment
        8. ast_node_similarity
        9. ast_depth_similarity
        10. operator_similarity
        11. tfidf_similarity

    Also returns matching source-code regions.
    """

    # =====================================================
    # NORMALIZE LANGUAGE NAMES
    # =====================================================

    language_a = language_a.lower()
    language_b = language_b.lower()

    # =====================================================
    # ORIGINAL AST SIMILARITY
    # =====================================================

    if (
        language_a == "python"
        and
        language_b == "python"
    ):

        ast_score = (
            calculate_python_ast_similarity(
                code_a,
                code_b
            )
        )

    else:

        try:

            structure_a = get_normalized_structure(
                code_a,
                language_a
            )

            structure_b = get_normalized_structure(
                code_b,
                language_b
            )

            if not structure_a and not structure_b:

                ast_score = 1.0

            elif not structure_a or not structure_b:

                ast_score = 0.0

            else:

                ast_score = SequenceMatcher(
                    None,
                    structure_a,
                    structure_b
                ).ratio()

        except Exception:

            ast_score = 0.0

    # =====================================================
    # WINNOWING
    # =====================================================

    fingerprints_a = (
        generate_semantic_fingerprints(
            code_a,
            language_a
        )
    )

    fingerprints_b = (
        generate_semantic_fingerprints(
            code_b,
            language_b
        )
    )

    winnowing_score = (
        calculate_jaccard_similarity(
            fingerprints_a,
            fingerprints_b
        )
    )

    matched_fingerprints = len(
        set(fingerprints_a)
        &
        set(fingerprints_b)
    )

    # =====================================================
    # NEW FEATURE 5
    # FINGERPRINT CONTAINMENT (length-independent)
    # =====================================================
    #
    # matched_fingerprints is a raw, unnormalized count. It
    # correlates strongly with snippet length, which causes the
    # model to under-trust short-but-genuinely-matching snippets
    # (e.g. a 2-line function can only ever produce 1 fingerprint,
    # so "matched_fingerprints=1" looks weak in absolute terms
    # even when it represents 100% overlap). This feature reports
    # that same signal as a 0-1 ratio, scaled to the smaller
    # snippet's fingerprint count, so short and long snippets are
    # judged on the same scale.

    fingerprint_containment_score = (
        calculate_containment_similarity(
            fingerprints_a,
            fingerprints_b
        )
    )

    # =====================================================
    # LEXICAL FEATURES
    # =====================================================

    raw_tokens_a = tokenize_code(
        code_a
    )

    raw_tokens_b = tokenize_code(
        code_b
    )

    normalized_tokens_a = (
        normalize_lexical_tokens(
            raw_tokens_a,
            language_a
        )
    )

    normalized_tokens_b = (
        normalize_lexical_tokens(
            raw_tokens_b,
            language_b
        )
    )

    token_score = (
        calculate_token_similarity(
            normalized_tokens_a,
            normalized_tokens_b
        )
    )

    line_score = (
        calculate_line_ratio(
            code_a,
            code_b
        )
    )

    token_count_ratio = (
        calculate_token_ratio(
            normalized_tokens_a,
            normalized_tokens_b
        )
    )

    # =====================================================
    # NEW FEATURE 1
    # AST NODE SIMILARITY
    # =====================================================

    ast_node_score = (
        calculate_ast_node_similarity(
            code_a,
            code_b,
            language_a,
            language_b
        )
    )

    # =====================================================
    # NEW FEATURE 2
    # AST DEPTH SIMILARITY
    # =====================================================

    ast_depth_score = (
        calculate_ast_depth_similarity(
            code_a,
            code_b,
            language_a,
            language_b
        )
    )

    # =====================================================
    # NEW FEATURE 3
    # OPERATOR SIMILARITY
    # =====================================================

    operator_score = (
        calculate_operator_similarity(
            code_a,
            code_b
        )
    )

    # =====================================================
    # NEW FEATURE 4
    # TF-IDF SIMILARITY
    # =====================================================

    tfidf_score = (
        calculate_tfidf_similarity(
            code_a,
            code_b,
            language_a,
            language_b
        )
    )

    # =====================================================
    # MATCHING REGIONS
    # =====================================================

    matching_regions = (
        find_matching_regions(
            code_a,
            code_b,
            language_a,
            language_b
        )
    )

    # =====================================================
    # RETURN ALL FEATURES
    # =====================================================

    return {

        # Original six features
        "ast_similarity":
            float(ast_score),

        "winnowing_similarity":
            float(winnowing_score),

        "token_similarity":
            float(token_score),

        "line_ratio":
            float(line_score),

        "token_ratio":
            float(token_count_ratio),

        "matched_fingerprints":
            int(matched_fingerprints),

        "fingerprint_containment":
            float(fingerprint_containment_score),

        # New four features
        "ast_node_similarity":
            float(ast_node_score),

        "ast_depth_similarity":
            float(ast_depth_score),

        "operator_similarity":
            float(operator_score),

        "tfidf_similarity":
            float(tfidf_score),

        # Explainable matching regions
        "matching_regions":
            matching_regions
    }
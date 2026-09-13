from difflib import SequenceMatcher


def calculate_ast_similarity(tokens_a, tokens_b):
    """
    Calculate similarity between two normalized AST token sequences.

    Returns:
        float: Similarity score between 0 and 1.
    """

    # If either code has no tokens, similarity is 0
    if not tokens_a or not tokens_b:
        return 0.0

    similarity = SequenceMatcher(
        None,
        tokens_a,
        tokens_b
    ).ratio()

    return similarity
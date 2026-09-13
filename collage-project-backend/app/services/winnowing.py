import hashlib

from app.services.semantic_tokens import get_semantic_tokens


def generate_kgrams(tokens, k=5):
    """
    Generate consecutive k-grams from a token sequence.
    """

    if k <= 0:
        raise ValueError("k must be greater than 0")

    if len(tokens) < k:
        return []

    return [
        tuple(tokens[i:i + k])
        for i in range(len(tokens) - k + 1)
    ]


def hash_kgram(kgram):
    """
    Convert a k-gram into a deterministic integer hash.
    """

    text = "|".join(kgram)

    digest = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    return int(digest, 16)


def generate_hashes(kgrams):
    """
    Generate a hash value for every k-gram.
    """

    return [
        hash_kgram(kgram)
        for kgram in kgrams
    ]


def winnow(hashes, window_size=4):
    """
    Select representative fingerprints using
    the Winnowing algorithm.
    """

    if window_size <= 0:
        raise ValueError(
            "window_size must be greater than 0"
        )

    if not hashes:
        return set()

    if len(hashes) <= window_size:
        return {min(hashes)}

    fingerprints = set()

    for i in range(
        len(hashes) - window_size + 1
    ):

        window = hashes[
            i:i + window_size
        ]

        minimum_hash = min(window)

        fingerprints.add(minimum_hash)

    return fingerprints


def calculate_containment_similarity(
    fingerprints_a,
    fingerprints_b
):
    """
    Calculate containment similarity between two fingerprint sets:

        |A ∩ B| / min(|A|, |B|)

    Unlike Jaccard similarity (which divides by the UNION and
    therefore penalizes pairs where one snippet is much larger
    or much smaller than the other), containment measures what
    fraction of the SMALLER snippet's fingerprints also appear
    in the larger one. This makes it far less sensitive to
    absolute code length, which matters a lot for very short
    snippets where only 1-2 fingerprints can ever exist -- with
    Jaccard/raw-count style features, such snippets look weak
    even when they fully match, purely because the counts are
    small in absolute terms.
    """

    if not fingerprints_a and not fingerprints_b:
        return 1.0

    if not fingerprints_a or not fingerprints_b:
        return 0.0

    intersection = fingerprints_a.intersection(
        fingerprints_b
    )

    smaller_size = min(
        len(fingerprints_a),
        len(fingerprints_b)
    )

    if smaller_size == 0:
        return 0.0

    return len(intersection) / smaller_size


def calculate_jaccard_similarity(
    fingerprints_a,
    fingerprints_b
):
    """
    Calculate Jaccard similarity between
    two fingerprint sets.
    """

    if not fingerprints_a and not fingerprints_b:
        return 1.0

    if not fingerprints_a or not fingerprints_b:
        return 0.0

    intersection = fingerprints_a.intersection(
        fingerprints_b
    )

    union = fingerprints_a.union(
        fingerprints_b
    )

    return len(intersection) / len(union)


def generate_fingerprints(
    tokens,
    k=5,
    window_size=4
):
    """
    Complete Winnowing pipeline:

    tokens
        ↓
    k-grams
        ↓
    hashes
        ↓
    winnowing
        ↓
    fingerprints
    """

    kgrams = generate_kgrams(
        tokens,
        k
    )

    hashes = generate_hashes(
        kgrams
    )

    fingerprints = winnow(
        hashes,
        window_size
    )

    return fingerprints


def generate_semantic_fingerprints(
    code: str,
    language: str,
    k: int = 5,
    window_size: int = 4
):
    """
    Generate Winnowing fingerprints from
    language-independent semantic tokens.

    Pipeline:

    source code
        ↓
    semantic normalization
        ↓
    k-grams
        ↓
    hashes
        ↓
    Winnowing fingerprints
    """

    tokens = get_semantic_tokens(
        code,
        language
    )

    return generate_fingerprints(
        tokens,
        k=k,
        window_size=window_size
    )
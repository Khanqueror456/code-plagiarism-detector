from app.services.semantic_tokens import (
    get_semantic_tokens
)

from app.services.winnowing import (
    generate_kgrams,
    hash_kgram,
    winnow
)


def get_semantic_tokens_with_lines(
    code,
    language
):
    """
    Generate semantic tokens while keeping
    the source line number of every token.
    """

    tokens = []
    token_lines = []

    for line_number, line in enumerate(
        code.splitlines(),
        start=1
    ):

        line_tokens = get_semantic_tokens(
            line,
            language
        )

        for token in line_tokens:
            tokens.append(token)
            token_lines.append(line_number)

    return tokens, token_lines


def get_fingerprint_positions(
    tokens,
    k=5,
    window_size=4
):
    """
    Find the positions of Winnowing fingerprints.

    Returns:

        {
            fingerprint_hash: [
                token_start_index,
                ...
            ]
        }
    """

    kgrams = generate_kgrams(
        tokens,
        k
    )

    if not kgrams:
        return {}

    hashes = [
        hash_kgram(kgram)
        for kgram in kgrams
    ]

    fingerprints = winnow(
        hashes,
        window_size
    )

    positions = {}

    for i, fingerprint_hash in enumerate(hashes):

        if fingerprint_hash in fingerprints:

            if fingerprint_hash not in positions:
                positions[fingerprint_hash] = []

            positions[fingerprint_hash].append(i)

    return positions


def merge_matching_regions(regions):
    """
    Merge overlapping or adjacent matching regions.
    """

    if not regions:
        return []

    sorted_regions = sorted(
        regions,
        key=lambda region: (
            region["code_a"]["start_line"],
            region["code_b"]["start_line"]
        )
    )

    merged = []

    for region in sorted_regions:

        current_a_start = region["code_a"]["start_line"]
        current_a_end = region["code_a"]["end_line"]

        current_b_start = region["code_b"]["start_line"]
        current_b_end = region["code_b"]["end_line"]

        if not merged:

            merged.append({
                "code_a": {
                    "start_line": current_a_start,
                    "end_line": current_a_end
                },
                "code_b": {
                    "start_line": current_b_start,
                    "end_line": current_b_end
                }
            })

            continue

        previous = merged[-1]

        previous_a_end = previous["code_a"]["end_line"]
        previous_b_end = previous["code_b"]["end_line"]

        previous_a_start = previous["code_a"]["start_line"]
        previous_b_start = previous["code_b"]["start_line"]

        overlaps_a = (
            current_a_start <= previous_a_end + 1
        )

        overlaps_b = (
            current_b_start <= previous_b_end + 1
        )

        if overlaps_a and overlaps_b:

            previous["code_a"]["start_line"] = min(
                previous_a_start,
                current_a_start
            )

            previous["code_a"]["end_line"] = max(
                previous_a_end,
                current_a_end
            )

            previous["code_b"]["start_line"] = min(
                previous_b_start,
                current_b_start
            )

            previous["code_b"]["end_line"] = max(
                previous_b_end,
                current_b_end
            )

        else:

            merged.append({
                "code_a": {
                    "start_line": current_a_start,
                    "end_line": current_a_end
                },
                "code_b": {
                    "start_line": current_b_start,
                    "end_line": current_b_end
                }
            })

    return merged


def find_matching_regions(
    code_a,
    code_b,
    language_a="python",
    language_b="python",
    k=5,
    window_size=4
):
    """
    Find matching source-code regions using
    semantic Winnowing fingerprints.

    Returns:

        [
            {
                "code_a": {
                    "start_line": 1,
                    "end_line": 2
                },
                "code_b": {
                    "start_line": 1,
                    "end_line": 2
                }
            }
        ]
    """

    # --------------------------------------------------
    # SEMANTIC TOKENIZATION + LINE MAPPING
    # --------------------------------------------------

    tokens_a, lines_a = get_semantic_tokens_with_lines(
        code_a,
        language_a
    )

    tokens_b, lines_b = get_semantic_tokens_with_lines(
        code_b,
        language_b
    )

    # --------------------------------------------------
    # FINGERPRINT POSITIONS
    # --------------------------------------------------

    fingerprints_a = get_fingerprint_positions(
        tokens_a,
        k=k,
        window_size=window_size
    )

    fingerprints_b = get_fingerprint_positions(
        tokens_b,
        k=k,
        window_size=window_size
    )

    # --------------------------------------------------
    # COMMON FINGERPRINTS
    # --------------------------------------------------

    common_fingerprints = (
        set(fingerprints_a.keys())
        .intersection(
            fingerprints_b.keys()
        )
    )

    if not common_fingerprints:
        return []

    regions = []

    # --------------------------------------------------
    # CREATE MATCHING REGIONS
    # --------------------------------------------------

    for fingerprint in common_fingerprints:

        positions_a = fingerprints_a[
            fingerprint
        ]

        positions_b = fingerprints_b[
            fingerprint
        ]

        for position_a in positions_a:

            for position_b in positions_b:

                end_a = position_a + k - 1
                end_b = position_b + k - 1

                # Make sure positions are valid

                if (
                    position_a >= len(lines_a)
                    or end_a >= len(lines_a)
                ):
                    continue

                if (
                    position_b >= len(lines_b)
                    or end_b >= len(lines_b)
                ):
                    continue

                start_line_a = lines_a[
                    position_a
                ]

                end_line_a = lines_a[
                    end_a
                ]

                start_line_b = lines_b[
                    position_b
                ]

                end_line_b = lines_b[
                    end_b
                ]

                regions.append({
                    "code_a": {
                        "start_line": start_line_a,
                        "end_line": end_line_a
                    },
                    "code_b": {
                        "start_line": start_line_b,
                        "end_line": end_line_b
                    }
                })

    # --------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------

    unique_regions = []

    seen = set()

    for region in regions:

        key = (
            region["code_a"]["start_line"],
            region["code_a"]["end_line"],
            region["code_b"]["start_line"],
            region["code_b"]["end_line"]
        )

        if key not in seen:

            seen.add(key)

            unique_regions.append(
                region
            )

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------

    unique_regions.sort(
        key=lambda region: (
            region["code_a"]["start_line"],
            region["code_b"]["start_line"]
        )
    )

    # --------------------------------------------------
    # MERGE
    # --------------------------------------------------

    return merge_matching_regions(
        unique_regions
    )
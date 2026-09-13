from app.services.python_ast import (
    parse_python_code,
    normalize_ast
)

from app.services.winnowing import (
    generate_fingerprints,
    calculate_jaccard_similarity
)


def compare_codes(code_a, code_b):
    """
    Parse, normalize, fingerprint and compare two programs.
    """

    tree_a = parse_python_code(code_a)
    tree_b = parse_python_code(code_b)

    tokens_a = normalize_ast(tree_a)
    tokens_b = normalize_ast(tree_b)

    fingerprints_a = generate_fingerprints(
        tokens_a,
        k=5,
        window_size=4
    )

    fingerprints_b = generate_fingerprints(
        tokens_b,
        k=5,
        window_size=4
    )

    similarity = calculate_jaccard_similarity(
        fingerprints_a,
        fingerprints_b
    )

    return (
        tokens_a,
        tokens_b,
        fingerprints_a,
        fingerprints_b,
        similarity
    )


# ============================================================
# TEST 1: SAME CODE
# ============================================================

code_a = """
def add(a, b):
    result = a + b
    return result
"""

code_b = """
def add(a, b):
    result = a + b
    return result
"""

_, _, fp_a, fp_b, similarity = compare_codes(
    code_a,
    code_b
)

print("=" * 50)
print("TEST 1: SAME CODE")
print("=" * 50)

print("Fingerprints A:", len(fp_a))
print("Fingerprints B:", len(fp_b))
print("Jaccard Similarity:", similarity)
print("Similarity (%):", similarity * 100)


# ============================================================
# TEST 2: SAME LOGIC, RENAMED VARIABLES
# ============================================================

code_a = """
def add(a, b):
    result = a + b
    return result
"""

code_b = """
def calculate(x, y):
    total = x + y
    return total
"""

_, _, fp_a, fp_b, similarity = compare_codes(
    code_a,
    code_b
)

print("\n")
print("=" * 50)
print("TEST 2: SAME LOGIC, RENAMED VARIABLES")
print("=" * 50)

print("Fingerprints A:", len(fp_a))
print("Fingerprints B:", len(fp_b))
print("Jaccard Similarity:", similarity)
print("Similarity (%):", similarity * 100)


# ============================================================
# TEST 3: DIFFERENT LOGIC
# ============================================================

code_a = """
def find_max(numbers):
    maximum = numbers[0]

    for number in numbers:
        if number > maximum:
            maximum = number

    return maximum
"""

code_b = """
def factorial(n):
    if n <= 1:
        return 1

    return n * factorial(n - 1)
"""

_, _, fp_a, fp_b, similarity = compare_codes(
    code_a,
    code_b
)

print("\n")
print("=" * 50)
print("TEST 3: DIFFERENT LOGIC")
print("=" * 50)

print("Fingerprints A:", len(fp_a))
print("Fingerprints B:", len(fp_b))
print("Jaccard Similarity:", similarity)
print("Similarity (%):", similarity * 100)
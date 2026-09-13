from app.services.python_ast import (
    parse_python_code,
    normalize_ast
)

from app.services.ast_similarity import (
    calculate_ast_similarity
)


# ============================================================
# TEST 1: Same code
# ============================================================

code_a = """
def add(a, b):
    return a + b
"""

code_b = """
def add(a, b):
    return a + b
"""


tree_a = parse_python_code(code_a)
tree_b = parse_python_code(code_b)

tokens_a = normalize_ast(tree_a)
tokens_b = normalize_ast(tree_b)

similarity = calculate_ast_similarity(
    tokens_a,
    tokens_b
)

print("=" * 50)
print("TEST 1: SAME CODE")
print("=" * 50)

print("Code A tokens:")
print(tokens_a)

print("\nCode B tokens:")
print(tokens_b)

print("\nAST Similarity:")
print(similarity)

print("\nAST Similarity (%):")
print(similarity * 100)


# ============================================================
# TEST 2: Same logic, different variable/function names
# ============================================================

code_a = """
def add(a, b):
    return a + b
"""

code_b = """
def calculate(x, y):
    return x + y
"""


tree_a = parse_python_code(code_a)
tree_b = parse_python_code(code_b)

tokens_a = normalize_ast(tree_a)
tokens_b = normalize_ast(tree_b)

similarity = calculate_ast_similarity(
    tokens_a,
    tokens_b
)

print("\n")
print("=" * 50)
print("TEST 2: SAME LOGIC, RENAMED VARIABLES")
print("=" * 50)

print("Code A tokens:")
print(tokens_a)

print("\nCode B tokens:")
print(tokens_b)

print("\nAST Similarity:")
print(similarity)

print("\nAST Similarity (%):")
print(similarity * 100)


# ============================================================
# TEST 3: Completely different code
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
def calculate_average(values):
    total = 0

    for value in values:
        total += value

    return total / len(values)
"""


tree_a = parse_python_code(code_a)
tree_b = parse_python_code(code_b)

tokens_a = normalize_ast(tree_a)
tokens_b = normalize_ast(tree_b)

similarity = calculate_ast_similarity(
    tokens_a,
    tokens_b
)

print("\n")
print("=" * 50)
print("TEST 3: DIFFERENT LOGIC")
print("=" * 50)

print("Code A tokens:")
print(tokens_a)

print("\nCode B tokens:")
print(tokens_b)

print("\nAST Similarity:")
print(similarity)

print("\nAST Similarity (%):")
print(similarity * 100)
from app.services.code_comparison import compare_code


code_a = """
def add(a, b):
    result = a + b
    return result
"""

code_b = """
def factorial(n):
    if n <= 1:
        return 1

    return n * factorial(n - 1)
"""


result = compare_code(code_a, code_b)


print("=" * 50)
print("IDENTICAL CODE TEST")
print("=" * 50)

for feature, value in result.items():
    print(f"{feature}: {value}")
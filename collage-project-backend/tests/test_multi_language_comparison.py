from app.services.code_comparison import (
    compare_code
)


python_code = """
def add(a, b):
    result = a + b
    return result
"""


java_code = """
public class Calculator {

    public static int add(int a, int b) {

        int result = a + b;

        return result;
    }
}
"""


javascript_code = """
function add(a, b) {

    let result = a + b;

    return result;
}
"""


cpp_code = """
int add(int a, int b) {

    int result = a + b;

    return result;
}
"""


print("=" * 60)
print("MULTI-LANGUAGE CODE COMPARISON")
print("=" * 60)


# --------------------------------------------------
# PYTHON VS PYTHON
# --------------------------------------------------

print("\nPython vs Python")

result = compare_code(
    python_code,
    python_code,
    "python",
    "python"
)

print(result)


# --------------------------------------------------
# PYTHON VS JAVA
# --------------------------------------------------

print("\nPython vs Java")

result = compare_code(
    python_code,
    java_code,
    "python",
    "java"
)

print(result)


# --------------------------------------------------
# PYTHON VS JAVASCRIPT
# --------------------------------------------------

print("\nPython vs JavaScript")

result = compare_code(
    python_code,
    javascript_code,
    "python",
    "javascript"
)

print(result)


# --------------------------------------------------
# PYTHON VS C++
# --------------------------------------------------

print("\nPython vs C++")

result = compare_code(
    python_code,
    cpp_code,
    "python",
    "cpp"
)

print(result)
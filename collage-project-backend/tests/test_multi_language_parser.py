from app.services.multi_language_parser import (
    parse_source_code,
    normalize_tree,
    get_normalized_structure,
    detect_language_from_extension
)


# --------------------------------------------------
# PYTHON
# --------------------------------------------------

python_code = """
def add(a, b):
    result = a + b
    return result
"""


# --------------------------------------------------
# JAVA
# --------------------------------------------------

java_code = """
public class Calculator {

    public static int add(int a, int b) {
        int result = a + b;
        return result;
    }

}
"""


# --------------------------------------------------
# JAVASCRIPT
# --------------------------------------------------

javascript_code = """
function add(a, b) {
    let result = a + b;
    return result;
}
"""


# --------------------------------------------------
# C++
# --------------------------------------------------

cpp_code = """
int add(int a, int b) {
    int result = a + b;
    return result;
}
"""


print("=" * 60)
print("MULTI-LANGUAGE PARSER TEST")
print("=" * 60)


# Python

python_tree = parse_source_code(
    python_code,
    "python"
)

python_tokens = normalize_tree(
    python_tree
)

print()
print("Python:")
print(python_tokens[:30])


# Java

java_tree = parse_source_code(
    java_code,
    "java"
)

java_tokens = normalize_tree(
    java_tree
)

print()
print("Java:")
print(java_tokens[:30])


# JavaScript

javascript_tree = parse_source_code(
    javascript_code,
    "javascript"
)

javascript_tokens = normalize_tree(
    javascript_tree
)

print()
print("JavaScript:")
print(javascript_tokens[:30])


# C++

cpp_tree = parse_source_code(
    cpp_code,
    "cpp"
)

cpp_tokens = normalize_tree(
    cpp_tree
)

print()
print("C++:")
print(cpp_tokens[:30])


# Extension detection

print()
print("Extension detection:")

print(
    "test.py ->",
    detect_language_from_extension(
        "test.py"
    )
)

print(
    "Main.java ->",
    detect_language_from_extension(
        "Main.java"
    )
)

print(
    "app.js ->",
    detect_language_from_extension(
        "app.js"
    )
)

print(
    "program.cpp ->",
    detect_language_from_extension(
        "program.cpp"
    )
)
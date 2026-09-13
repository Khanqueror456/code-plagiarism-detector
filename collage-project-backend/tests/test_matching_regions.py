from app.services.multi_language_parser import (
    get_normalized_structure
)

from app.services.ast_similarity import (
    calculate_ast_similarity
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


python_tokens = get_normalized_structure(
    python_code,
    "python"
)

java_tokens = get_normalized_structure(
    java_code,
    "java"
)

javascript_tokens = get_normalized_structure(
    javascript_code,
    "javascript"
)

cpp_tokens = get_normalized_structure(
    cpp_code,
    "cpp"
)


print("=" * 60)
print("LANGUAGE-INDEPENDENT STRUCTURAL SIMILARITY")
print("=" * 60)


print("\nPython:")
print(python_tokens)


print("\nJava:")
print(java_tokens)


print("\nJavaScript:")
print(javascript_tokens)


print("\nC++:")
print(cpp_tokens)


print("\nSimilarity:")

print(
    "Python vs Java:",
    calculate_ast_similarity(
        python_tokens,
        java_tokens
    )
)


print(
    "Python vs JavaScript:",
    calculate_ast_similarity(
        python_tokens,
        javascript_tokens
    )
)


print(
    "Python vs C++:",
    calculate_ast_similarity(
        python_tokens,
        cpp_tokens
    )
)
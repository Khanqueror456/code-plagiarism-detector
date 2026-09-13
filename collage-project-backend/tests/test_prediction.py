from app.ml.predict import predict_plagiarism


code_a = """
def add(a, b):
    result = a + b
    return result
"""


code_b = """
def addition(x, y):
    total = x + y
    return total
"""


result = predict_plagiarism(
    code_a,
    code_b
)


print("=" * 60)
print("PLAGIARISM PREDICTION")
print("=" * 60)

print()

print("Prediction:")
print(result["prediction"])

print()

print("Probability:")
print(
    f"{result['probability'] * 100:.2f}%"
)

print()

print("Features:")

for feature, value in result["features"].items():

    print(
        f"{feature}: {value}"
    )
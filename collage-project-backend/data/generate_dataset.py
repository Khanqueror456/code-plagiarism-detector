import os
import random
import pandas as pd

from app.services.code_comparison import compare_code


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# IMPORTANT: this filename is intentionally distinct from
# build_real_dataset.py's output (code_similarity_dataset_real.csv)
# and from the final merged file train_model.py reads
# (code_similarity_dataset.csv). The two dataset scripts used to
# write to the same path, so running this one after
# build_real_dataset.py would silently destroy the ~10,000-row real
# dataset. Run combine_datasets.py to merge the two into the final
# training file.
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__),
    "code_similarity_dataset_synthetic.csv"
)


random.seed(42)


# --------------------------------------------------
# MULTI-LANGUAGE PROGRAMS
# --------------------------------------------------

programs = {

    "addition": {
        "python": """
def add(a, b):
    result = a + b
    return result
""",

        "java": """
public class Calculator {
    public static int add(int a, int b) {
        int result = a + b;
        return result;
    }
}
""",

        "javascript": """
function add(a, b) {
    let result = a + b;
    return result;
}
""",

        "cpp": """
int add(int a, int b) {
    int result = a + b;
    return result;
}
""",

        "c": """
int add(int a, int b) {
    int result = a + b;
    return result;
}
"""
    },


    "factorial": {
        "python": """
def factorial(n):
    if n <= 1:
        return 1

    return n * factorial(n - 1)
""",

        "java": """
public class Calculator {
    public static int factorial(int n) {
        if (n <= 1) {
            return 1;
        }

        return n * factorial(n - 1);
    }
}
""",

        "javascript": """
function factorial(n) {
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}
""",

        "cpp": """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}
""",

        "c": """
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}
"""
    },


    "maximum": {
        "python": """
def find_max(numbers):
    maximum = numbers[0]

    for number in numbers:
        if number > maximum:
            maximum = number

    return maximum
""",

        "java": """
public class Calculator {
    public static int findMax(int[] numbers) {
        int maximum = numbers[0];

        for (int number : numbers) {
            if (number > maximum) {
                maximum = number;
            }
        }

        return maximum;
    }
}
""",

        "javascript": """
function findMax(numbers) {
    let maximum = numbers[0];

    for (let number of numbers) {
        if (number > maximum) {
            maximum = number;
        }
    }

    return maximum;
}
""",

        "cpp": """
int findMax(int numbers[], int size) {
    int maximum = numbers[0];

    for (int i = 0; i < size; i++) {
        if (numbers[i] > maximum) {
            maximum = numbers[i];
        }
    }

    return maximum;
}
""",

        "c": """
int findMax(int numbers[], int size) {
    int maximum = numbers[0];

    for (int i = 0; i < size; i++) {
        if (numbers[i] > maximum) {
            maximum = numbers[i];
        }
    }

    return maximum;
}
"""
    },


    "average": {
        "python": """
def calculate_average(numbers):
    total = 0

    for number in numbers:
        total += number

    return total / len(numbers)
""",

        "java": """
public class Calculator {
    public static double calculateAverage(int[] numbers) {
        int total = 0;

        for (int number : numbers) {
            total += number;
        }

        return (double) total / numbers.length;
    }
}
""",

        "javascript": """
function calculateAverage(numbers) {
    let total = 0;

    for (let number of numbers) {
        total += number;
    }

    return total / numbers.length;
}
""",

        "cpp": """
double calculateAverage(int numbers[], int size) {
    int total = 0;

    for (int i = 0; i < size; i++) {
        total += numbers[i];
    }

    return (double) total / size;
}
""",

        "c": """
double calculateAverage(int numbers[], int size) {
    int total = 0;

    for (int i = 0; i < size; i++) {
        total += numbers[i];
    }

    return (double) total / size;
}
"""
    },


    "reverse_string": {
        "python": """
def reverse_string(text):
    result = ""

    for character in text:
        result = character + result

    return result
""",

        "java": """
public class StringUtil {
    public static String reverseString(String text) {
        String result = "";

        for (int i = text.length() - 1; i >= 0; i--) {
            result += text.charAt(i);
        }

        return result;
    }
}
""",

        "javascript": """
function reverseString(text) {
    let result = "";

    for (let i = text.length - 1; i >= 0; i--) {
        result += text[i];
    }

    return result;
}
""",

        "cpp": """
string reverseString(string text) {
    string result = "";

    for (int i = text.length() - 1; i >= 0; i--) {
        result += text[i];
    }

    return result;
}
""",

        "c": """
void reverseString(char text[], char result[]) {
    int length = strlen(text);

    for (int i = 0; i < length; i++) {
        result[i] = text[length - i - 1];
    }

    result[length] = '\\0';
}
"""
    },


    "sum_list": {
        "python": """
def sum_list(numbers):
    total = 0

    for number in numbers:
        total += number

    return total
""",

        "java": """
public class Calculator {
    public static int sumList(int[] numbers) {
        int total = 0;

        for (int number : numbers) {
            total += number;
        }

        return total;
    }
}
""",

        "javascript": """
function sumList(numbers) {
    let total = 0;

    for (let number of numbers) {
        total += number;
    }

    return total;
}
""",

        "cpp": """
int sumList(int numbers[], int size) {
    int total = 0;

    for (int i = 0; i < size; i++) {
        total += numbers[i];
    }

    return total;
}
""",

        "c": """
int sumList(int numbers[], int size) {
    int total = 0;

    for (int i = 0; i < size; i++) {
        total += numbers[i];
    }

    return total;
}
"""
    },


    "search_element": {
        "python": """
def search_element(numbers, target):
    for number in numbers:
        if number == target:
            return True

    return False
""",

        "java": """
public class Search {
    public static boolean searchElement(int[] numbers, int target) {
        for (int number : numbers) {
            if (number == target) {
                return true;
            }
        }

        return false;
    }
}
""",

        "javascript": """
function searchElement(numbers, target) {
    for (let number of numbers) {
        if (number === target) {
            return true;
        }
    }

    return false;
}
""",

        "cpp": """
bool searchElement(int numbers[], int size, int target) {
    for (int i = 0; i < size; i++) {
        if (numbers[i] == target) {
            return true;
        }
    }

    return false;
}
""",

        "c": """
int searchElement(int numbers[], int size, int target) {
    for (int i = 0; i < size; i++) {
        if (numbers[i] == target) {
            return 1;
        }
    }

    return 0;
}
"""
    },


    "count_positive": {
        "python": """
def count_positive(numbers):
    count = 0

    for number in numbers:
        if number > 0:
            count += 1

    return count
""",

        "java": """
public class Counter {
    public static int countPositive(int[] numbers) {
        int count = 0;

        for (int number : numbers) {
            if (number > 0) {
                count++;
            }
        }

        return count;
    }
}
""",

        "javascript": """
function countPositive(numbers) {
    let count = 0;

    for (let number of numbers) {
        if (number > 0) {
            count++;
        }
    }

    return count;
}
""",

        "cpp": """
int countPositive(int numbers[], int size) {
    int count = 0;

    for (int i = 0; i < size; i++) {
        if (numbers[i] > 0) {
            count++;
        }
    }

    return count;
}
""",

        "c": """
int countPositive(int numbers[], int size) {
    int count = 0;

    for (int i = 0; i < size; i++) {
        if (numbers[i] > 0) {
            count++;
        }
    }

    return count;
}
"""
    }
}


# --------------------------------------------------
# RENAMED-IDENTIFIER VARIANTS
# --------------------------------------------------
#
# These are the SAME programs with identifiers renamed but logic
# unchanged -- the single most common real-world plagiarism pattern.
# Investigation showed the model, trained only on BigCloneBench
# (real, comparatively long Java methods), learned to distrust short
# snippets because raw fingerprint counts are naturally tiny for
# short code, regardless of how completely they match. Pairing each
# short program here against a renamed variant gives the model
# direct, correctly-labeled examples of exactly that scenario, in
# multiple languages, instead of only ever seeing it in long-form
# Java.

renamed_variants = {

    "addition": {
        "python": """
def sum_two(x, y):
    total = x + y
    return total
""",
        "java": """
public class MathHelper {
    public static int sumTwo(int x, int y) {
        int total = x + y;
        return total;
    }
}
""",
        "javascript": """
function sumTwo(x, y) {
    let total = x + y;
    return total;
}
""",
    },

    "factorial": {
        "python": """
def fact(num):
    if num <= 1:
        return 1

    return num * fact(num - 1)
""",
        "java": """
public class MathHelper {
    public static int fact(int num) {
        if (num <= 1) {
            return 1;
        }

        return num * fact(num - 1);
    }
}
""",
        "javascript": """
function fact(num) {
    if (num <= 1) {
        return 1;
    }

    return num * fact(num - 1);
}
""",
    },

    "maximum": {
        "python": """
def get_largest(values):
    largest = values[0]

    for value in values:
        if value > largest:
            largest = value

    return largest
""",
        "java": """
public class MathHelper {
    public static int getLargest(int[] values) {
        int largest = values[0];

        for (int value : values) {
            if (value > largest) {
                largest = value;
            }
        }

        return largest;
    }
}
""",
        "javascript": """
function getLargest(values) {
    let largest = values[0];

    for (let value of values) {
        if (value > largest) {
            largest = value;
        }
    }

    return largest;
}
""",
    },

    "average": {
        "python": """
def get_mean(values):
    running_total = 0

    for value in values:
        running_total += value

    return running_total / len(values)
""",
        "java": """
public class MathHelper {
    public static double getMean(int[] values) {
        int runningTotal = 0;

        for (int value : values) {
            runningTotal += value;
        }

        return (double) runningTotal / values.length;
    }
}
""",
        "javascript": """
function getMean(values) {
    let runningTotal = 0;

    for (let value of values) {
        runningTotal += value;
    }

    return runningTotal / values.length;
}
""",
    },

    "sum_list": {
        "python": """
def add_all(values):
    accumulator = 0

    for value in values:
        accumulator += value

    return accumulator
""",
        "java": """
public class MathHelper {
    public static int addAll(int[] values) {
        int accumulator = 0;

        for (int value : values) {
            accumulator += value;
        }

        return accumulator;
    }
}
""",
        "javascript": """
function addAll(values) {
    let accumulator = 0;

    for (let value of values) {
        accumulator += value;
    }

    return accumulator;
}
""",
    },

    "search_element": {
        "python": """
def contains_value(items, needle):
    for item in items:
        if item == needle:
            return True

    return False
""",
        "java": """
public class SearchHelper {
    public static boolean containsValue(int[] items, int needle) {
        for (int item : items) {
            if (item == needle) {
                return true;
            }
        }

        return false;
    }
}
""",
        "javascript": """
function containsValue(items, needle) {
    for (let item of items) {
        if (item === needle) {
            return true;
        }
    }

    return false;
}
""",
    },

    "count_positive": {
        "python": """
def tally_positives(values):
    tally = 0

    for value in values:
        if value > 0:
            tally += 1

    return tally
""",
        "java": """
public class CountHelper {
    public static int tallyPositives(int[] values) {
        int tally = 0;

        for (int value : values) {
            if (value > 0) {
                tally++;
            }
        }

        return tally;
    }
}
""",
        "javascript": """
function tallyPositives(values) {
    let tally = 0;

    for (let value of values) {
        if (value > 0) {
            tally++;
        }
    }

    return tally;
}
""",
    },

    "reverse_string": {
        "python": """
def flip_text(input_text):
    output_text = ""

    for ch in input_text:
        output_text = ch + output_text

    return output_text
""",
        "java": """
public class StringHelper {
    public static String flipText(String inputText) {
        String outputText = "";

        for (int i = inputText.length() - 1; i >= 0; i--) {
            outputText += inputText.charAt(i);
        }

        return outputText;
    }
}
""",
        "javascript": """
function flipText(inputText) {
    let outputText = "";

    for (let i = inputText.length - 1; i >= 0; i--) {
        outputText += inputText[i];
    }

    return outputText;
}
""",
    },
}


# --------------------------------------------------
# UNRELATED PROGRAMS
# --------------------------------------------------

unrelated_programs = {

    "is_prime": {
        "python": """
def is_prime(number):
    if number < 2:
        return False

    for divisor in range(2, number):
        if number % divisor == 0:
            return False

    return True
""",

        "java": """
public class Prime {
    public static boolean isPrime(int number) {
        if (number < 2) {
            return false;
        }

        for (int divisor = 2; divisor < number; divisor++) {
            if (number % divisor == 0) {
                return false;
            }
        }

        return true;
    }
}
""",

        "javascript": """
function isPrime(number) {
    if (number < 2) {
        return false;
    }

    for (let divisor = 2; divisor < number; divisor++) {
        if (number % divisor === 0) {
            return false;
        }
    }

    return true;
}
""",

        "cpp": """
bool isPrime(int number) {
    if (number < 2) {
        return false;
    }

    for (int divisor = 2; divisor < number; divisor++) {
        if (number % divisor == 0) {
            return false;
        }
    }

    return true;
}
"""
    },


    "calculate_area": {
        "python": """
def calculate_area(length, width):
    area = length * width
    return area
""",

        "java": """
public class Geometry {
    public static int calculateArea(int length, int width) {
        int area = length * width;
        return area;
    }
}
""",

        "javascript": """
function calculateArea(length, width) {
    let area = length * width;
    return area;
}
""",

        "cpp": """
int calculateArea(int length, int width) {
    int area = length * width;
    return area;
}
"""
    },


    "count_words": {
        "python": """
def count_words(text):
    words = text.split()
    return len(words)
""",

        "java": """
public class TextUtil {
    public static int countWords(String text) {
        String[] words = text.split(" ");
        return words.length;
    }
}
""",

        "javascript": """
function countWords(text) {
    let words = text.split(" ");
    return words.length;
}
""",

        "cpp": """
int countWords(string text) {
    int count = 0;

    for (char character : text) {
        if (character == ' ') {
            count++;
        }
    }

    return count + 1;
}
"""
    },


    "is_even": {
        "python": """
def is_even(number):
    return number % 2 == 0
""",

        "java": """
public class NumberUtil {
    public static boolean isEven(int number) {
        return number % 2 == 0;
    }
}
""",

        "javascript": """
function isEven(number) {
    return number % 2 === 0;
}
""",

        "cpp": """
bool isEven(int number) {
    return number % 2 == 0;
}
"""
    },


    "power": {
        "python": """
def power(base, exponent):
    result = 1

    for _ in range(exponent):
        result *= base

    return result
""",

        "java": """
public class MathUtil {
    public static int power(int base, int exponent) {
        int result = 1;

        for (int i = 0; i < exponent; i++) {
            result *= base;
        }

        return result;
    }
}
""",

        "javascript": """
function power(base, exponent) {
    let result = 1;

    for (let i = 0; i < exponent; i++) {
        result *= base;
    }

    return result;
}
""",

        "cpp": """
int power(int base, int exponent) {
    int result = 1;

    for (int i = 0; i < exponent; i++) {
        result *= base;
    }

    return result;
}
"""
    }
}


# --------------------------------------------------
# FEATURE COLUMNS
# --------------------------------------------------
#
# Must stay in sync with app/ml/train_model.py and app/ml/predict.py.
# Previously this list only had 6 of the 10 (now 11) features that
# compare_code() actually returns, which meant any attempt to train
# directly off this script's output would crash with a KeyError.

FEATURE_COLUMNS = [
    "ast_similarity",
    "winnowing_similarity",
    "token_similarity",
    "line_ratio",
    "token_ratio",
    "matched_fingerprints",
    "fingerprint_containment",
    "ast_node_similarity",
    "ast_depth_similarity",
    "operator_similarity",
    "tfidf_similarity",
]


# --------------------------------------------------
# CREATE DATASET ROW
# --------------------------------------------------

def create_row(
    code_a,
    code_b,
    language_a,
    language_b,
    label,
    group_id
):

    features = compare_code(
        code_a,
        code_b,
        language_a,
        language_b
    )

    row = {
        # Column names match build_real_dataset.py's schema
        # (func1/func2) so the two files can be concatenated
        # directly by combine_datasets.py.
        "func1": code_a,
        "func2": code_b,
        "language_a": language_a,
        "language_b": language_b,
    }

    for column in FEATURE_COLUMNS:
        row[column] = features[column]

    row["label"] = label
    # Namespaced so these ids can never collide with
    # build_real_dataset.py's "real_<n>" group ids once merged.
    row["group_id"] = f"synthetic_{group_id}"

    return row


# --------------------------------------------------
# GENERATE DATASET
# --------------------------------------------------

rows = []


# --------------------------------------------------
# SIMILAR / CROSS-LANGUAGE SAMPLES
# --------------------------------------------------

print("Generating similar samples...")

for program_name, language_versions in programs.items():

    languages = list(
        language_versions.keys()
    )

    # Same-language comparisons

    for language in languages:

        code = language_versions[language]

        rows.append(
            create_row(
                code,
                code,
                language,
                language,
                1,
                program_name
            )
        )

    # Cross-language comparisons

    for i in range(len(languages)):

        for j in range(
            i + 1,
            len(languages)
        ):

            language_a = languages[i]
            language_b = languages[j]

            code_a = language_versions[
                language_a
            ]

            code_b = language_versions[
                language_b
            ]

            rows.append(
                create_row(
                    code_a,
                    code_b,
                    language_a,
                    language_b,
                    1,
                    program_name
                )
            )

    # Renamed-identifier variant comparisons (same language, same
    # logic, different names) -- the classic short-snippet
    # plagiarism pattern the trained model was previously never
    # shown in this form.

    variant_versions = renamed_variants.get(program_name, {})

    for language, variant_code in variant_versions.items():

        original_code = language_versions.get(language)

        if original_code is None:
            continue

        rows.append(
            create_row(
                original_code,
                variant_code,
                language,
                language,
                1,
                program_name
            )
        )


# --------------------------------------------------
# UNRELATED SAMPLES
# --------------------------------------------------

print("Generating unrelated samples...")

all_programs = []

for name, languages in programs.items():

    for language, code in languages.items():

        all_programs.append(
            (
                name,
                language,
                code
            )
        )


all_unrelated = []

for name, languages in unrelated_programs.items():

    for language, code in languages.items():

        all_unrelated.append(
            (
                name,
                language,
                code
            )
        )


negative_pairs = []

for name_a, language_a, code_a in all_programs:

    for name_b, language_b, code_b in all_unrelated:

        negative_pairs.append(
            (
                name_a,
                language_a,
                code_a,
                name_b,
                language_b,
                code_b
            )
        )


random.shuffle(
    negative_pairs
)


# Keep dataset balanced enough for prototype

negative_pairs = negative_pairs[:120]


for index, (
    name_a,
    language_a,
    code_a,
    name_b,
    language_b,
    code_b
) in enumerate(
    negative_pairs
):

    rows.append(
        create_row(
            code_a,
            code_b,
            language_a,
            language_b,
            0,
            f"unrelated_{index}"
        )
    )


# --------------------------------------------------
# DATAFRAME
# --------------------------------------------------

df = pd.DataFrame(
    rows
)


# --------------------------------------------------
# SHUFFLE
# --------------------------------------------------

df = df.sample(
    frac=1,
    random_state=42
).reset_index(
    drop=True
)


# --------------------------------------------------
# SAVE
# --------------------------------------------------

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# --------------------------------------------------
# INFORMATION
# --------------------------------------------------

print()
print("=" * 60)
print("MULTI-LANGUAGE DATASET GENERATED")
print("=" * 60)

print()

print(
    "Total samples:",
    len(df)
)

print(
    "Similar samples:",
    int((df["label"] == 1).sum())
)

print(
    "Unrelated samples:",
    int((df["label"] == 0).sum())
)

print(
    "Number of groups:",
    df["group_id"].nunique()
)

print()

print("Feature columns:")

for column in FEATURE_COLUMNS:

    print(
        f"- {column}"
    )

print()

print("Dataset columns:")

print(
    df.columns.tolist()
)

print()

print("Saved to:")

print(
    OUTPUT_PATH
)

print()
print("NOTE: this covers Python/Java/JS/C/C++, same-language,")
print("cross-language, and renamed-identifier pairs. Run")
print("build_real_dataset.py separately for real Java clone data,")
print("then combine_datasets.py to merge both into the final")
print("code_similarity_dataset.csv used by train_model.py.")
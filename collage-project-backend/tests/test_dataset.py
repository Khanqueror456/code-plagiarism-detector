import csv
import os


DATASET_PATH = os.path.join(
    "data",
    "code_similarity_dataset.csv"
)


with open(
    DATASET_PATH,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    rows = list(reader)


print("=" * 60)
print("DATASET INSPECTION")
print("=" * 60)

print(f"Total rows: {len(rows)}")

print()
print("Columns:")
print(reader.fieldnames)

print()
print("First 5 rows:")

for row in rows[:5]:
    print(row)


print()
print("Class distribution:")

similar = sum(
    1
    for row in rows
    if row["label"] == "1"
)

unrelated = sum(
    1
    for row in rows
    if row["label"] == "0"
)

print(f"Similar:   {similar}")
print(f"Unrelated: {unrelated}")
import os
import pandas as pd

# =========================================================
# PATHS
# =========================================================

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

REAL_PATH = os.path.join(DATA_DIR, "code_similarity_dataset_real.csv")
SYNTHETIC_PATH = os.path.join(DATA_DIR, "code_similarity_dataset_synthetic.csv")

# This is the file train_model.py actually reads.
FINAL_PATH = os.path.join(DATA_DIR, "code_similarity_dataset.csv")

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

KEEP_COLUMNS = FEATURE_COLUMNS + ["label", "group_id"]


def load_source(path, source_name):

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing {source_name} dataset at {path}. "
            f"Run build_real_dataset.py and generate_dataset.py first."
        )

    dataframe = pd.read_csv(path)

    missing = [c for c in KEEP_COLUMNS if c not in dataframe.columns]

    if missing:
        raise ValueError(
            f"{source_name} dataset at {path} is missing columns {missing}. "
            f"Its FEATURE_COLUMNS list is out of sync with train_model.py."
        )

    # NOTE: group_id values are EXPECTED to repeat within a dataset --
    # every row belonging to the same clone family (or, for
    # generate_dataset.py, the same synthetic program) intentionally
    # shares one group_id, which is what makes GroupKFold /
    # GroupShuffleSplit in train_model.py work correctly. The only
    # thing that must never happen is a group_id from one SOURCE
    # colliding with a group_id from the OTHER source -- that's
    # checked separately in main() via the "real_"/"synthetic_"
    # prefixes each generator script applies.

    return dataframe[KEEP_COLUMNS]


def main():

    real_df = load_source(REAL_PATH, "real")
    synthetic_df = load_source(SYNTHETIC_PATH, "synthetic")

    overlap = set(real_df["group_id"]) & set(synthetic_df["group_id"])

    if overlap:
        raise ValueError(
            f"group_id collision between real and synthetic datasets: {overlap}"
        )

    combined = pd.concat([real_df, synthetic_df], ignore_index=True)

    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    combined.to_csv(FINAL_PATH, index=False)

    print("=" * 60)
    print("COMBINED DATASET")
    print("=" * 60)
    print(f"Real (Java, BigCloneBench) rows: {len(real_df)}")
    print(f"Synthetic (multi-language)  rows: {len(synthetic_df)}")
    print(f"Total rows: {len(combined)}")
    print(f"Similar (label=1): {(combined['label'] == 1).sum()}")
    print(f"Unrelated (label=0): {(combined['label'] == 0).sum()}")
    print(f"Unique groups: {combined['group_id'].nunique()}")
    print()
    print("Saved to:", FINAL_PATH)


if __name__ == "__main__":
    main()
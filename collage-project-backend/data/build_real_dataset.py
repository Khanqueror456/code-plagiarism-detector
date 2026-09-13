import os
import sys
from collections import defaultdict

import pandas as pd
from datasets import load_dataset

# =========================================================
# PROJECT PATH
# =========================================================

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.code_comparison import compare_code

# =========================================================
# CONFIGURATION
# =========================================================

TARGET_SIMILAR = 5000
TARGET_UNRELATED = 5000

# BigCloneBench (code_x_glue_cc_clone_detection_big_clone_bench) only
# contains Java functions. This script can therefore only produce
# Java-Java pairs. Non-Java and cross-language coverage must come
# from generate_dataset.py's synthetic multi-language corpus and be
# merged in afterwards with combine_datasets.py -- do NOT rename
# this constant to make it look configurable, since the underlying
# dataset genuinely has no other languages.
LANGUAGE = "java"

# IMPORTANT: this filename is intentionally distinct from
# generate_dataset.py's output and from the final merged training
# file (code_similarity_dataset.csv). Previously both dataset
# scripts wrote to the same "code_similarity_dataset.csv" path --
# running generate_dataset.py after this script would silently
# overwrite the full ~10,000-row, 11-feature real dataset with a
# ~240-row, 6-feature synthetic one, and the next train_model.py
# run would then crash with a KeyError on the missing columns.
# Run combine_datasets.py after both generators to produce the
# actual file train_model.py reads.
OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__), "code_similarity_dataset_real.csv"
)


# =========================================================
# UNION-FIND
# =========================================================


class UnionFind:

    def __init__(self):
        self.parent = {}
        self.rank = {}

    def add(self, x):

        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x):

        # Make sure the item exists.
        if x not in self.parent:
            self.add(x)

        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])

        return self.parent[x]

    def union(self, a, b):

        self.add(a)
        self.add(b)

        root_a = self.find(a)
        root_b = self.find(b)

        if root_a == root_b:
            return

        if self.rank[root_a] < self.rank[root_b]:

            self.parent[root_a] = root_b

        elif self.rank[root_a] > self.rank[root_b]:

            self.parent[root_b] = root_a

        else:

            self.parent[root_b] = root_a
            self.rank[root_a] += 1


# =========================================================
# BUILD DATASET
# =========================================================


def build_dataset():

    print("=" * 60)
    print("LOADING BIGCLONEBENCH")
    print("=" * 60)

    print("Using streaming mode...")
    print("This avoids downloading the entire dataset.")
    print()

    dataset = load_dataset(
        "google/code_x_glue_cc_clone_detection_big_clone_bench",
        split="train",
        streaming=True,
    )

    similar_count = 0
    unrelated_count = 0

    rows = []

    used_pairs = set()

    print("=" * 60)
    print("COLLECTING SAMPLES")
    print("=" * 60)
    print()

    # =====================================================
    # COLLECT 5000 SIMILAR + 5000 UNRELATED
    # =====================================================

    for sample in dataset:

        id1 = int(sample["id1"])
        id2 = int(sample["id2"])

        func1 = sample["func1"]
        func2 = sample["func2"]

        original_label = bool(sample["label"])

        # Actual behavior observed from the loaded
        # BigCloneBench samples:
        #
        # True  -> Similar / clone
        # False -> Unrelated / non-clone
        #
        # Our project:
        #
        # 1 -> Similar
        # 0 -> Unrelated

        project_label = 1 if original_label else 0

        # Avoid duplicate pairs.

        pair_key = tuple(sorted((id1, id2)))

        if pair_key in used_pairs:
            continue

        # =================================================
        # CHECK CLASS LIMITS
        # =================================================

        if project_label == 1:

            if similar_count >= TARGET_SIMILAR:
                continue

        else:

            if unrelated_count >= TARGET_UNRELATED:
                continue

        # =================================================
        # FEATURE EXTRACTION
        # =================================================

        try:

            features = compare_code(
                func1, func2, language_a=LANGUAGE, language_b=LANGUAGE
            )

        except Exception as e:

            print(f"Skipping pair " f"{id1}-{id2}: {e}")

            continue

        # =================================================
        # STORE ROW
        # =================================================

        rows.append(
            {
                # Keep IDs temporarily.
                # They will be removed before saving.
                "id1": id1,
                "id2": id2,
                # Raw source is retained (unlike the original version
                # of this script) so that future feature-engineering
                # changes -- like fingerprint_containment below --
                # don't require re-streaming BigCloneBench from
                # scratch. Column names match generate_dataset.py's
                # schema (func1/func2) so the two datasets can be
                # concatenated directly by combine_datasets.py.
                "func1": func1,
                "func2": func2,
                "language_a": LANGUAGE,
                "language_b": LANGUAGE,
                "ast_similarity": features["ast_similarity"],
                "winnowing_similarity": features["winnowing_similarity"],
                "token_similarity": features["token_similarity"],
                "line_ratio": features["line_ratio"],
                "token_ratio": features["token_ratio"],
                "matched_fingerprints": features["matched_fingerprints"],
                "fingerprint_containment": features["fingerprint_containment"],
                "ast_node_similarity": features["ast_node_similarity"],
                "ast_depth_similarity": features["ast_depth_similarity"],
                "operator_similarity": features["operator_similarity"],
                "tfidf_similarity": features["tfidf_similarity"],
                "label": project_label,
            }
        )

        used_pairs.add(pair_key)

        # =================================================
        # UPDATE COUNTERS
        # =================================================

        if project_label == 1:

            similar_count += 1

        else:

            unrelated_count += 1

        total = similar_count + unrelated_count

        if total % 100 == 0:

            print(
                f"Processed: {total:5d} | "
                f"Similar: {similar_count:5d} | "
                f"Unrelated: {unrelated_count:5d}"
            )

        # =================================================
        # STOP WHEN BALANCED DATASET IS COMPLETE
        # =================================================

        if similar_count >= TARGET_SIMILAR and unrelated_count >= TARGET_UNRELATED:

            break

    # =====================================================
    # CHECK DATASET
    # =====================================================

    if similar_count < TARGET_SIMILAR:

        raise RuntimeError(
            f"Could not collect enough similar pairs. " f"Collected {similar_count}."
        )

    if unrelated_count < TARGET_UNRELATED:

        raise RuntimeError(
            f"Could not collect enough unrelated pairs. "
            f"Collected {unrelated_count}."
        )

    # =====================================================
    # DATAFRAME
    # =====================================================

    dataframe = pd.DataFrame(rows)

    # =====================================================
    # BUILD CLONE FAMILIES
    # =====================================================

    print()
    print("=" * 60)
    print("BUILDING CLONE-FAMILY GROUPS")
    print("=" * 60)

    union_find = UnionFind()

    # IMPORTANT:
    #
    # ONLY SIMILAR PAIRS are used to construct
    # clone-family connections.
    #
    # Unrelated pairs are NOT connected.

    for row in rows:

        if row["label"] == 1:

            union_find.union(row["id1"], row["id2"])

    # =====================================================
    # CREATE GROUP IDs
    # =====================================================

    group_map = {}

    next_group_id = 0

    group_ids = []

    for row in rows:

        # -------------------------------------------------
        # SIMILAR PAIR
        # -------------------------------------------------

        if row["label"] == 1:

            root = union_find.find(row["id1"])

            if root not in group_map:

                group_map[root] = next_group_id

                next_group_id += 1

            group_ids.append(group_map[root])

        # -------------------------------------------------
        # UNRELATED PAIR
        # -------------------------------------------------
        #
        # Each unrelated pair receives its own group.
        #
        # This prevents an unrelated pair from accidentally
        # connecting two clone families.

        else:

            group_ids.append(next_group_id)

            next_group_id += 1

    # Group ids are namespaced with a source prefix so that, once
    # combine_datasets.py merges this file with generate_dataset.py's
    # synthetic output, an integer group id from one source can never
    # collide with an integer group id from the other.
    dataframe["group_id"] = [f"real_{g}" for g in group_ids]

    # =====================================================
    # REMOVE IDS
    # =====================================================

    dataframe = dataframe.drop(columns=["id1", "id2"])

    # =====================================================
    # SHUFFLE
    # =====================================================

    dataframe = dataframe.sample(frac=1, random_state=42).reset_index(drop=True)

    # =====================================================
    # SAVE
    # =====================================================

    dataframe.to_csv(OUTPUT_FILE, index=False)

    # =====================================================
    # FINAL REPORT
    # =====================================================

    print()
    print("=" * 60)
    print("DATASET GENERATED")
    print("=" * 60)

    print(f"Total samples: " f"{len(dataframe)}")

    print(f"Similar samples: " f"{(dataframe['label'] == 1).sum()}")

    print(f"Unrelated samples: " f"{(dataframe['label'] == 0).sum()}")

    print(f"Unique clone-family groups: " f"{dataframe['group_id'].nunique()}")

    print()

    print(
        f"Average samples per group: "
        f"{len(dataframe) / dataframe['group_id'].nunique():.2f}"
    )

    print()

    print("Columns:")

    print(list(dataframe.columns))

    # =====================================================
    # FEATURE STATISTICS
    # =====================================================

    feature_columns = [
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

    print()
    print("Feature means by label:")

    print(dataframe.groupby("label")[feature_columns].mean())

    print()
    print("Feature medians by label:")

    print(dataframe.groupby("label")[feature_columns].median())

    # =====================================================
    # GROUP STATISTICS
    # =====================================================

    print()
    print("Group-size statistics:")

    print(dataframe.groupby("group_id").size().describe())

    print()
    print("Saved to:")

    print(OUTPUT_FILE)

    print()
    print("NOTE: this file only contains Java-Java pairs (BigCloneBench")
    print("has no other languages). Run generate_dataset.py for")
    print("non-Java / cross-language coverage, then combine_datasets.py")
    print("to produce the final code_similarity_dataset.csv used by")
    print("train_model.py.")


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    build_dataset()
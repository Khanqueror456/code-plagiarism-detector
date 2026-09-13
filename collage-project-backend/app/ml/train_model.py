import os
import sys

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split, GroupShuffleSplit, GroupKFold

# =========================================================
# PROJECT PATH
# =========================================================

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)


# =========================================================
# PATHS
# =========================================================

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "code_similarity_dataset.csv",
)

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "plagiarism_model.joblib"
)


# =========================================================
# FEATURES
# =========================================================

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

TARGET_COLUMN = "label"

GROUP_COLUMN = "group_id"


# =========================================================
# MODEL
# =========================================================


def create_model():

    return RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
        max_features="sqrt",
    )


# =========================================================
# METRICS
# =========================================================


def calculate_metrics(y_true, y_pred):

    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
    }


# =========================================================
# PRINT METRICS
# =========================================================


def print_metrics(metrics):

    print(f"Accuracy:  " f"{metrics['accuracy']:.4f}")

    print(f"Precision: " f"{metrics['precision']:.4f}")

    print(f"Recall:    " f"{metrics['recall']:.4f}")

    print(f"F1 Score:  " f"{metrics['f1']:.4f}")


# =========================================================
# MAIN
# =========================================================


def main():

    # =====================================================
    # LOAD DATASET
    # =====================================================

    print("=" * 60)
    print("LOADING DATASET")
    print("=" * 60)

    dataframe = pd.read_csv(DATASET_PATH)

    print(f"Dataset size: " f"{len(dataframe)}")

    print()
    print("Columns:")
    print(list(dataframe.columns))

    print()
    print("Features:")
    print(FEATURE_COLUMNS)

    X = dataframe[FEATURE_COLUMNS]

    y = dataframe[TARGET_COLUMN]

    groups = dataframe[GROUP_COLUMN]

    print()
    print(f"X shape: {X.shape}")

    print(f"y shape: {y.shape}")

    print(f"Number of groups: " f"{groups.nunique()}")

    # =====================================================
    # CLASS DISTRIBUTION
    # =====================================================

    print()
    print("=" * 60)
    print("CLASS DISTRIBUTION")
    print("=" * 60)

    print(y.value_counts().sort_index())

    # =====================================================
    # STRATIFIED EVALUATION
    # =====================================================

    print()
    print("=" * 60)
    print("STRATIFIED TRAIN / TEST EVALUATION")
    print("=" * 60)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training samples: " f"{len(X_train)}")

    print(f"Testing samples: " f"{len(X_test)}")

    print()

    stratified_model = create_model()

    stratified_model.fit(X_train, y_train)

    stratified_predictions = stratified_model.predict(X_test)

    stratified_metrics = calculate_metrics(y_test, stratified_predictions)

    print("STRATIFIED TEST RESULTS")

    print("-" * 60)

    print_metrics(stratified_metrics)

    print()
    print("Classification Report:")

    print(
        classification_report(
            y_test,
            stratified_predictions,
            target_names=["Unrelated", "Similar"],
            zero_division=0,
        )
    )

    print("Confusion Matrix:")

    print(confusion_matrix(y_test, stratified_predictions))

    # =====================================================
    # GROUP-AWARE HOLDOUT
    # =====================================================

    print()
    print("=" * 60)
    print("GROUP-AWARE HOLDOUT EVALUATION")
    print("=" * 60)

    group_splitter = GroupShuffleSplit(n_splits=1, test_size=0.20, random_state=42)

    train_indices, test_indices = next(group_splitter.split(X, y, groups))

    X_group_train = X.iloc[train_indices]

    X_group_test = X.iloc[test_indices]

    y_group_train = y.iloc[train_indices]

    y_group_test = y.iloc[test_indices]

    print(f"Training samples: " f"{len(X_group_train)}")

    print(f"Testing samples: " f"{len(X_group_test)}")

    print()

    print("Training class distribution:")

    print(y_group_train.value_counts().sort_index())

    print()

    print("Testing class distribution:")

    print(y_group_test.value_counts().sort_index())

    group_model = create_model()

    group_model.fit(X_group_train, y_group_train)

    group_predictions = group_model.predict(X_group_test)

    group_metrics = calculate_metrics(y_group_test, group_predictions)

    print()
    print("GROUP-AWARE TEST RESULTS")

    print("-" * 60)

    print_metrics(group_metrics)

    print()
    print("Classification Report:")

    print(
        classification_report(
            y_group_test,
            group_predictions,
            target_names=["Unrelated", "Similar"],
            zero_division=0,
        )
    )

    print("Confusion Matrix:")

    print(confusion_matrix(y_group_test, group_predictions))

    # =====================================================
    # GROUP-AWARE 5-FOLD CV
    # =====================================================

    print()
    print("=" * 60)
    print("5-FOLD GROUP-AWARE CROSS-VALIDATION")
    print("=" * 60)

    group_kfold = GroupKFold(n_splits=5)

    cv_results = []

    for fold, (train_idx, validation_idx) in enumerate(
        group_kfold.split(X, y, groups), start=1
    ):

        print()
        print(f"Fold {fold}")

        X_fold_train = X.iloc[train_idx]

        X_fold_validation = X.iloc[validation_idx]

        y_fold_train = y.iloc[train_idx]

        y_fold_validation = y.iloc[validation_idx]

        fold_model = create_model()

        fold_model.fit(X_fold_train, y_fold_train)

        fold_predictions = fold_model.predict(X_fold_validation)

        fold_metrics = calculate_metrics(y_fold_validation, fold_predictions)

        cv_results.append(fold_metrics)

        print_metrics(fold_metrics)

    # =====================================================
    # CV AVERAGES
    # =====================================================

    cv_dataframe = pd.DataFrame(cv_results)

    cv_means = cv_dataframe.mean()

    print()
    print("-" * 60)
    print("GROUP-AWARE CV AVERAGES")
    print("-" * 60)

    print(f"Mean Accuracy:  " f"{cv_means['accuracy']:.4f}")

    print(f"Mean Precision: " f"{cv_means['precision']:.4f}")

    print(f"Mean Recall:    " f"{cv_means['recall']:.4f}")

    print(f"Mean F1 Score:  " f"{cv_means['f1']:.4f}")

    # =====================================================
    # TRAIN FINAL PRODUCTION MODEL
    # =====================================================

    print()
    print("=" * 60)
    print("TRAINING FINAL PRODUCTION MODEL")
    print("=" * 60)

    final_model = create_model()

    final_model.fit(X, y)

    print("Final model training complete.")

    # =====================================================
    # FEATURE IMPORTANCE
    # =====================================================

    print()
    print("=" * 60)
    print("FEATURE IMPORTANCE")
    print("=" * 60)

    feature_importances = final_model.feature_importances_

    importance_dataframe = pd.DataFrame(
        {"feature": FEATURE_COLUMNS, "importance": feature_importances}
    ).sort_values("importance", ascending=False)

    for _, row in importance_dataframe.iterrows():

        print(f"{row['feature']}: " f"{row['importance']:.4f}")

    # =====================================================
    # SAVE MODEL
    # =====================================================

    joblib.dump(final_model, MODEL_PATH)

    print()
    print("=" * 60)
    print("MODEL SAVED")
    print("=" * 60)

    print(MODEL_PATH)


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    main()
import os

import joblib
import pandas as pd

from app.services.code_comparison import compare_code


# =========================================================
# MODEL PATH
# =========================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "plagiarism_model.joblib"
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
    "tfidf_similarity"
]


# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load(
    MODEL_PATH
)


# =========================================================
# PREDICTION
# =========================================================

def predict_plagiarism(
    code_a,
    code_b,
    language_a="python",
    language_b="python"
):

    # -----------------------------------------------------
    # COMPARE CODE
    # -----------------------------------------------------

    features = compare_code(
        code_a,
        code_b,
        language_a,
        language_b
    )


    # -----------------------------------------------------
    # EXTRACT MODEL FEATURES
    # -----------------------------------------------------

    feature_data = {
        column: features[column]
        for column in FEATURE_COLUMNS
    }


    # -----------------------------------------------------
    # CREATE DATAFRAME
    # -----------------------------------------------------

    X = pd.DataFrame(
        [feature_data],
        columns=FEATURE_COLUMNS
    )


    # -----------------------------------------------------
    # MODEL PREDICTION
    # -----------------------------------------------------

    prediction = model.predict(
        X
    )[0]


    probabilities = model.predict_proba(
        X
    )[0]


    probability = float(
        probabilities[1]
    )


    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "prediction":
            int(prediction),

        "probability":
            probability,

        "features":
            feature_data,

        "matching_regions":
            features[
                "matching_regions"
            ]
    }
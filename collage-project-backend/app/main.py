from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ml.predict import predict_plagiarism
from app.services.multi_language_parser import (
    SUPPORTED_LANGUAGES,
    validate_language
)


app = FastAPI(
    title="Code Plagiarism Detection API",
    description="API for detecting similarity between source code",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeComparisonRequest(BaseModel):

    code_a: str
    code_b: str

    language_a: str = "python"
    language_b: str = "python"


@app.get("/")
def root():

    return {
        "message": "Code Plagiarism Detection API is running",
        "supported_languages": SUPPORTED_LANGUAGES
    }


@app.post("/compare")
def compare_code_endpoint(
    request: CodeComparisonRequest
):

    try:

        validate_language(
            request.language_a
        )

        validate_language(
            request.language_b
        )

        result = predict_plagiarism(
            request.code_a,
            request.code_b,
            request.language_a,
            request.language_b
        )

        return {
            "prediction": result["prediction"],

            "similarity_probability":
                result["probability"],

            "features":
                result["features"],

            "matching_regions":
                result["matching_regions"],

            "languages": {
                "code_a": request.language_a,
                "code_b": request.language_b
            }
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        print("Comparison error:", e)

        raise HTTPException(
            status_code=500,
            detail="An error occurred while comparing the code."
        )
const API_URL = "http://127.0.0.1:8000";

export const compareCode = async (
    codeA,
    codeB,
    languageA = "python",
    languageB = "python"
) => {
    const response = await fetch(`${API_URL}/compare`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            code_a: codeA,
            code_b: codeB,
            language_a: languageA,
            language_b: languageB,
        }),
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.detail || "Failed to compare code"
        );
    }

    return data;
};
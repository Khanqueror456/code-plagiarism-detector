import { useState } from "react";
import { compareCode } from "./services/plagiarismService";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import "./App.css";

function App() {
    const [codeA, setCodeA] = useState("");
    const [codeB, setCodeB] = useState("");

    const [fileA, setFileA] = useState("");
    const [fileB, setFileB] = useState("");

    const [languageA, setLanguageA] = useState("python");
    const [languageB, setLanguageB] = useState("python");

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // --------------------------------------------------
    // LANGUAGE CONFIGURATION
    // --------------------------------------------------

    const languageOptions = [
        {
            value: "python",
            label: "Python",
            extensions: [".py"],
        },
        {
            value: "java",
            label: "Java",
            extensions: [".java"],
        },
        {
            value: "javascript",
            label: "JavaScript",
            extensions: [".js", ".jsx"],
        },
        {
            value: "cpp",
            label: "C++",
            extensions: [".cpp", ".cc", ".cxx", ".hpp", ".h"],
        },
        {
            value: "c",
            label: "C",
            extensions: [".c"],
        },
    ];

    // --------------------------------------------------
    // GET LANGUAGE FROM FILE
    // --------------------------------------------------

    const getLanguageFromFile = (fileName) => {
        const extension =
            "." + fileName.split(".").pop().toLowerCase();

        for (const language of languageOptions) {
            if (language.extensions.includes(extension)) {
                return language.value;
            }
        }

        return null;
    };

    // --------------------------------------------------
    // FILE UPLOAD
    // --------------------------------------------------

    const handleFileUpload = (
        event,
        setCode,
        setFile,
        setLanguage
    ) => {
        const file = event.target.files[0];

        if (!file) {
            return;
        }

        const detectedLanguage =
            getLanguageFromFile(file.name);

        if (!detectedLanguage) {
            setError(
                "Unsupported file type. Please upload Python, Java, JavaScript, C++ or C source code."
            );

            event.target.value = "";
            return;
        }

        const reader = new FileReader();

        reader.onload = (e) => {
            const content = e.target.result;

            setCode(content);
            setFile(file.name);
            setLanguage(detectedLanguage);
            setError("");
        };

        reader.onerror = () => {
            setError(
                `Unable to read ${file.name}.`
            );
        };

        reader.readAsText(file);
    };

    // --------------------------------------------------
    // COMPARE
    // --------------------------------------------------

    const handleCompare = async () => {
        if (!codeA.trim() || !codeB.trim()) {
            setError(
                "Please enter or upload code in both editors."
            );

            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        try {
            const data = await compareCode(
                codeA,
                codeB,
                languageA,
                languageB
            );

            setResult(data);
        } catch (err) {
            setError(
                err.message || "Failed to compare code."
            );
        } finally {
            setLoading(false);
        }
    };

    // --------------------------------------------------
    // FORMAT PERCENTAGE
    // --------------------------------------------------

    const formatPercentage = (value) => {
        return `${(value * 100).toFixed(2)}%`;
    };

    // --------------------------------------------------
    // NORMALIZE PREDICTION
    // --------------------------------------------------

    const isSimilar =
        result &&
        (
            result.prediction === 1 ||
            result.prediction === "1" ||
            result.prediction === "Similar"
        );

    const predictionLabel = isSimilar
        ? "Similar"
        : "Unrelated";

    return (
        <div className="app">

            {/* ========================================== */}
            {/* HEADER */}
            {/* ========================================== */}

            <header className="header">
                <div>
                    <h1>
                        Code Plagiarism Detector
                    </h1>

                    <p>
                        Compare two source codes using
                        AST, Winnowing and Machine Learning.
                    </p>
                </div>
            </header>

            <main className="container">

                {/* ========================================== */}
                {/* CODE INPUT */}
                {/* ========================================== */}

                <section className="code-section">

                    {/* -------------------------------------- */}
                    {/* CODE A */}
                    {/* -------------------------------------- */}

                    <div className="code-card">

                        <div className="card-header">

                            <div>
                                <h2>
                                    Code A
                                </h2>

                                {fileA && (
                                    <span className="file-name">
                                        {fileA}
                                    </span>
                                )}
                            </div>

                            <div className="card-actions">

                                <select
                                    className="language-select"
                                    value={languageA}
                                    onChange={(e) => {
                                        setLanguageA(
                                            e.target.value
                                        );
                                        setFileA("");
                                    }}
                                >
                                    {languageOptions.map(
                                        (language) => (
                                            <option
                                                key={language.value}
                                                value={language.value}
                                            >
                                                {language.label}
                                            </option>
                                        )
                                    )}
                                </select>

                                <label className="upload-button">
                                    Upload File

                                    <input
                                        type="file"
                                        accept=".py,.java,.js,.jsx,.cpp,.cc,.cxx,.h,.hpp,.c"
                                        hidden
                                        onChange={(event) =>
                                            handleFileUpload(
                                                event,
                                                setCodeA,
                                                setFileA,
                                                setLanguageA
                                            )
                                        }
                                    />
                                </label>

                            </div>

                        </div>

                        <textarea
                            value={codeA}
                            onChange={(e) => {
                                setCodeA(e.target.value);
                                setFileA("");
                            }}
                            placeholder="Paste the first source code here..."
                            spellCheck="false"
                        />

                    </div>


                    {/* -------------------------------------- */}
                    {/* CODE B */}
                    {/* -------------------------------------- */}

                    <div className="code-card">

                        <div className="card-header">

                            <div>
                                <h2>
                                    Code B
                                </h2>

                                {fileB && (
                                    <span className="file-name">
                                        {fileB}
                                    </span>
                                )}
                            </div>

                            <div className="card-actions">

                                <select
                                    className="language-select"
                                    value={languageB}
                                    onChange={(e) => {
                                        setLanguageB(
                                            e.target.value
                                        );
                                        setFileB("");
                                    }}
                                >
                                    {languageOptions.map(
                                        (language) => (
                                            <option
                                                key={language.value}
                                                value={language.value}
                                            >
                                                {language.label}
                                            </option>
                                        )
                                    )}
                                </select>

                                <label className="upload-button">
                                    Upload File

                                    <input
                                        type="file"
                                        accept=".py,.java,.js,.jsx,.cpp,.cc,.cxx,.h,.hpp,.c"
                                        hidden
                                        onChange={(event) =>
                                            handleFileUpload(
                                                event,
                                                setCodeB,
                                                setFileB,
                                                setLanguageB
                                            )
                                        }
                                    />
                                </label>

                            </div>

                        </div>

                        <textarea
                            value={codeB}
                            onChange={(e) => {
                                setCodeB(e.target.value);
                                setFileB("");
                            }}
                            placeholder="Paste the second source code here..."
                            spellCheck="false"
                        />

                    </div>

                </section>


                {/* ========================================== */}
                {/* COMPARE BUTTON */}
                {/* ========================================== */}

                <button
                    className="compare-button"
                    onClick={handleCompare}
                    disabled={loading}
                >
                    {loading
                        ? "Analyzing..."
                        : "Compare Code"
                    }
                </button>


                {/* ========================================== */}
                {/* ERROR */}
                {/* ========================================== */}

                {error && (
                    <div className="error">
                        {error}
                    </div>
                )}


                {/* ========================================== */}
                {/* RESULTS */}
                {/* ========================================== */}

                {result && (
                    <section className="result-section">

                        {/* ---------------------------------- */}
                        {/* CLASSIFICATION */}
                        {/* ---------------------------------- */}

                        <div className="result-card">

                            <h2>
                                Classification
                            </h2>

                            <div
                                className={`prediction ${
                                    isSimilar
                                        ? "similar"
                                        : "unrelated"
                                }`}
                            >
                                {predictionLabel}
                            </div>


                            <p className="probability">
                                Model Confidence
                            </p>

                            <div className="confidence-value">
                                {formatPercentage(
                                    result.similarity_probability
                                )}
                            </div>


                            <div className="confidence-bar">

                                <div
                                    className={`confidence-fill ${
                                        isSimilar
                                            ? "similar-fill"
                                            : "unrelated-fill"
                                    }`}
                                    style={{
                                        width: `${Math.min(
                                            result.similarity_probability * 100,
                                            100
                                        )}%`,
                                    }}
                                />

                            </div>


                            <p className="confidence-description">

                                {isSimilar
                                    ? "The model classified the submitted programs as similar."
                                    : "The model classified the submitted programs as unrelated."
                                }

                            </p>

                        </div>


                        {/* ---------------------------------- */}
                        {/* FEATURES */}
                        {/* ---------------------------------- */}

                        <div className="features-card">

                            <h2>
                                Analysis Features
                            </h2>

                            <p className="features-description">
                                Similarity measurements extracted
                                from the submitted source code.
                            </p>


                            <div className="features-grid">

                                <Feature
                                    name="AST Similarity"
                                    value={
                                        result.features
                                            .ast_similarity
                                    }
                                />

                                <Feature
                                    name="Winnowing Similarity"
                                    value={
                                        result.features
                                            .winnowing_similarity
                                    }
                                />

                                <Feature
                                    name="Token Similarity"
                                    value={
                                        result.features
                                            .token_similarity
                                    }
                                />

                                <Feature
                                    name="Line Ratio"
                                    value={
                                        result.features
                                            .line_ratio
                                    }
                                />

                                <Feature
                                    name="Token Ratio"
                                    value={
                                        result.features
                                            .token_ratio
                                    }
                                />

                                <div className="feature">

                                    <span>
                                        Matched Fingerprints
                                    </span>

                                    <strong>
                                        {
                                            result.features
                                                .matched_fingerprints
                                        }
                                    </strong>

                                </div>

                            </div>

                        </div>


                        {/* ---------------------------------- */}
                        {/* MATCHING CODE */}
                        {/* ---------------------------------- */}

                        <MatchingCode
                            codeA={codeA}
                            codeB={codeB}
                            languageA={languageA}
                            languageB={languageB}
                            matchingRegions={
                                result.matching_regions || []
                            }
                        />

                    </section>
                )}

            </main>

        </div>
    );
}


/* ==================================================
   FEATURE
   ================================================== */

function Feature({
    name,
    value
}) {
    return (
        <div className="feature">

            <span>
                {name}
            </span>

            <strong>
                {(value * 100).toFixed(2)}%
            </strong>

        </div>
    );
}


/* ==================================================
   MATCHING CODE
   ================================================== */

function MatchingCode({
    codeA,
    codeB,
    languageA,
    languageB,
    matchingRegions
}) {

    const matchingLinesA = new Set();
    const matchingLinesB = new Set();


    matchingRegions.forEach((region) => {

        const startA =
            region.code_a.start_line;

        const endA =
            region.code_a.end_line;


        for (
            let line = startA;
            line <= endA;
            line++
        ) {
            matchingLinesA.add(line);
        }


        const startB =
            region.code_b.start_line;

        const endB =
            region.code_b.end_line;


        for (
            let line = startB;
            line <= endB;
            line++
        ) {
            matchingLinesB.add(line);
        }

    });


    return (
        <div className="matching-section">

            {/* ---------------------------------------- */}
            {/* HEADER */}
            {/* ---------------------------------------- */}

            <div className="matching-header">

                <div>

                    <h2>
                        Matching Source Code
                    </h2>

                    <p>
                        Highlighted lines contain code
                        patterns identified as matching.
                    </p>

                </div>


                <div className="match-count">

                    {matchingRegions.length}
                    {" "}
                    {matchingRegions.length === 1
                        ? "matching region"
                        : "matching regions"
                    }

                </div>

            </div>


            {/* ---------------------------------------- */}
            {/* NO MATCHES */}
            {/* ---------------------------------------- */}

            {matchingRegions.length === 0 ? (

                <div className="no-matches">
                    No matching source-code regions
                    were found.
                </div>

            ) : (

                <div className="comparison-view">

                    {/* ================================== */}
                    {/* CODE A */}
                    {/* ================================== */}

                    <div className="comparison-card">

                        <div className="comparison-title">
                            Code A
                        </div>


                        <SyntaxHighlighter
                            language={languageA}
                            style={vscDarkPlus}
                            showLineNumbers
                            wrapLines={true}
                            wrapLongLines={false}
                            startingLineNumber={1}

                            customStyle={{
                                margin: 0,
                                borderRadius: 0,
                                minHeight: "180px",
                                maxHeight: "500px",
                                overflow: "auto",
                                fontSize: "14px",
                                lineHeight: "1.6"
                            }}

                            lineNumberStyle={{
                                minWidth: "40px",
                                paddingRight: "12px",
                                userSelect: "none"
                            }}

                            lineProps={(lineNumber) => {

                                const isMatching =
                                    matchingLinesA.has(
                                        lineNumber
                                    );

                                return {
                                    style: {

                                        display: "block",

                                        backgroundColor:
                                            isMatching
                                                ? "rgba(79, 70, 229, 0.45)"
                                                : "transparent",

                                        borderLeft:
                                            isMatching
                                                ? "4px solid #818cf8"
                                                : "4px solid transparent",

                                        paddingLeft: "8px"

                                    }
                                };
                            }}
                        >
                            {codeA}
                        </SyntaxHighlighter>

                    </div>


                    {/* ================================== */}
                    {/* CODE B */}
                    {/* ================================== */}

                    <div className="comparison-card">

                        <div className="comparison-title">
                            Code B
                        </div>


                        <SyntaxHighlighter
                            language={languageB}
                            style={vscDarkPlus}
                            showLineNumbers
                            wrapLines={true}
                            wrapLongLines={false}
                            startingLineNumber={1}

                            customStyle={{
                                margin: 0,
                                borderRadius: 0,
                                minHeight: "180px",
                                maxHeight: "500px",
                                overflow: "auto",
                                fontSize: "14px",
                                lineHeight: "1.6"
                            }}

                            lineNumberStyle={{
                                minWidth: "40px",
                                paddingRight: "12px",
                                userSelect: "none"
                            }}

                            lineProps={(lineNumber) => {

                                const isMatching =
                                    matchingLinesB.has(
                                        lineNumber
                                    );

                                return {
                                    style: {

                                        display: "block",

                                        backgroundColor:
                                            isMatching
                                                ? "rgba(79, 70, 229, 0.45)"
                                                : "transparent",

                                        borderLeft:
                                            isMatching
                                                ? "4px solid #818cf8"
                                                : "4px solid transparent",

                                        paddingLeft: "8px"

                                    }
                                };
                            }}
                        >
                            {codeB}
                        </SyntaxHighlighter>

                    </div>

                </div>

            )}

        </div>
    );
}


export default App;
/* =========================================================
   BOND V2.0
   FRONTEND CONTROLLER
   FINAL STABLE BUILD
   =========================================================

   Responsibilities:
   - Prototype interaction
   - Flask /api/chat connection
   - Baseline response rendering
   - AHI response rendering
   - BOND score rendering
   - Five-factor diagnostic rendering
   - Comparison rendering
   - Server status
   - Mobile navigation
   - Debug / API test
   - Robust API response extraction

   IMPORTANT API CONTRACT

   POST /api/chat

   {
       "success": true,

       "baseline": {
           "response": "..."
       },

       "ahi_response": {
           "response": "..."
       },

       "evaluation": {
           "baseline": {...},
           "ahi": {...},
           "comparison": {...}
       }
   }

   ========================================================= */


/* =========================================================
   CONFIGURATION
   ========================================================= */

const BOND_CONFIG = {

    apiBase: "",

    chatEndpoint: "/api/chat",

    statusEndpoint: "/api/status",

    requestTimeout: 120000,

    version: "BOND-V2.0",

    ahiVersion: "AHI-V2"

};


/* =========================================================
   DOM ELEMENTS
   ========================================================= */

const promptInput =
    document.getElementById("promptInput");

const runBtn =
    document.getElementById("runBtn");

const serverStatus =
    document.getElementById("serverStatus");

const baselineAnswer =
    document.getElementById("baselineAnswer");

const ahiAnswer =
    document.getElementById("ahiAnswer");

const baselineScore =
    document.getElementById("baselineScore");

const ahiScore =
    document.getElementById("ahiScore");

const baselineConstraint =
    document.getElementById("baselineConstraint");

const ahiConstraint =
    document.getElementById("ahiConstraint");

const baselineQuality =
    document.getElementById("baselineQuality");

const ahiQuality =
    document.getElementById("ahiQuality");

const difference =
    document.getElementById("difference");

const improvement =
    document.getElementById("improvement");

const winner =
    document.getElementById("winner");

const profileBaseline =
    document.getElementById("profileBaseline");

const profileAhi =
    document.getElementById("profileAhi");

const toast =
    document.getElementById("toast");

const menuBtn =
    document.getElementById("menuBtn");

const navLinks =
    document.getElementById("navLinks");


/* =========================================================
   INTERNAL STATE
   ========================================================= */

let interactionCount = 0;

let interactionRunning = false;

let lastAPIResponse = null;

let lastPrompt = "";


/* =========================================================
   BASIC SAFETY
   ========================================================= */

function safeString(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }

    return String(value);

}


/* =========================================================
   HTML ESCAPE
   ========================================================= */

function escapeHtml(value) {

    return safeString(value)

        .replaceAll("&", "&amp;")

        .replaceAll("<", "&lt;")

        .replaceAll(">", "&gt;")

        .replaceAll('"', "&quot;")

        .replaceAll("'", "&#039;");

}


/* =========================================================
   RESPONSE TEXT NORMALIZATION
   ========================================================= */

function normalizeText(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    if (
        typeof value === "string"
    ) {

        return value.trim();

    }


    if (
        typeof value === "number" ||
        typeof value === "boolean"
    ) {

        return String(value);

    }


    if (
        typeof value === "object"
    ) {

        const candidates = [

            value.response,

            value.content,

            value.text,

            value.answer,

            value.message

        ];


        for (
            const candidate of candidates
        ) {

            if (
                typeof candidate === "string" &&
                candidate.trim()
            ) {

                return candidate.trim();

            }

        }

    }


    return "";

}


/* =========================================================
   SCORE FORMAT
   ========================================================= */

function formatScore(value) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }


    const safe =
        Math.max(
            0,
            Math.min(
                1,
                number
            )
        );


    return safe.toFixed(3);

}


/* =========================================================
   PERCENT FORMAT
   ========================================================= */

function formatPercent(value) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return "—";

    }


    return number.toFixed(2) + "%";

}


/* =========================================================
   SCORE NUMBER
   ========================================================= */

function numericScore(value) {

    const number =
        Number(value);


    if (
        !Number.isFinite(number)
    ) {

        return 0;

    }


    return Math.max(
        0,
        Math.min(
            1,
            number
        )
    );

}


/* =========================================================
   TOAST
   ========================================================= */

function showToast(message) {

    if (!toast) {

        console.warn(
            "BOND toast:",
            message
        );

        return;

    }


    toast.textContent =
        safeString(message);


    toast.classList.add(
        "show"
    );


    clearTimeout(
        showToast.timer
    );


    showToast.timer =
        setTimeout(
            function () {

                toast.classList.remove(
                    "show"
                );

            },
            3000
        );

}


/* =========================================================
   SET ANSWER
   ========================================================= */

function setAnswer(
    element,
    text,
    emptyMessage
) {

    if (!element) {

        return;

    }


    const normalized =
        normalizeText(text);


    element.classList.remove(
        "empty"
    );


    if (normalized) {

        element.textContent =
            normalized;

        return;

    }


    element.textContent =
        emptyMessage ||
        "No response returned.";

    element.classList.add(
        "empty"
    );

}


/* =========================================================
   SET METRIC
   ========================================================= */

function setMetric(
    element,
    value
) {

    if (!element) {

        return;

    }


    element.textContent =
        formatScore(value);

}


/* =========================================================
   PANEL RESET
   ========================================================= */

function resetPrototypeUI() {

    setAnswer(
        baselineAnswer,
        "",
        "Generating baseline response…"
    );


    setAnswer(
        ahiAnswer,
        "",
        "Generating AHI response…"
    );


    if (baselineScore) {

        baselineScore.textContent =
            "—";

    }


    if (ahiScore) {

        ahiScore.textContent =
            "—";

    }


    if (baselineConstraint) {

        baselineConstraint.textContent =
            "—";

    }


    if (ahiConstraint) {

        ahiConstraint.textContent =
            "—";

    }


    if (baselineQuality) {

        baselineQuality.textContent =
            "—";

    }


    if (ahiQuality) {

        ahiQuality.textContent =
            "—";

    }


    if (difference) {

        difference.textContent =
            "—";

    }


    if (improvement) {

        improvement.textContent =
            "—";

    }


    if (winner) {

        winner.textContent =
            "—";

    }


    if (profileBaseline) {

        profileBaseline.innerHTML =
            "";

    }


    if (profileAhi) {

        profileAhi.innerHTML =
            "";

    }

}


/* =========================================================
   WORD EXTRACTION
   ========================================================= */

function words(text) {

    const normalized =
        safeString(text)
            .toLowerCase();


    const matches =
        normalized.match(
            /\b[a-zA-Z]{3,}\b/g
        );


    return matches || [];

}


/* =========================================================
   SENTENCE COUNT
   ========================================================= */

function sentenceCount(text) {

    const clean =
        safeString(text)
            .trim();


    if (!clean) {

        return 0;

    }


    const matches =
        clean.match(
            /[^.!?]+[.!?]+(?=\s|$)|[^.!?]+$/g
        );


    return matches
        ? matches.length
        : 1;

}


/* =========================================================
   REQUESTED SENTENCE COUNT
   ========================================================= */

function requestedSentences(prompt) {

    const text =
        safeString(prompt);


    const patterns = [

        /(\d+)\s+short\s+sentences?/i,

        /(\d+)\s+sentences?/i,

        /in\s+(\d+)\s+sentences?/i

    ];


    for (
        const pattern of patterns
    ) {

        const match =
            text.match(pattern);


        if (match) {

            return Number(
                match[1]
            );

        }

    }


    return null;

}


/* =========================================================
   LONG WORD PENALTY
   ========================================================= */

function longWordPenalty(response) {

    const ws =
        safeString(response)
            .match(
                /\b[a-zA-Z]+\b/g
            ) || [];


    if (!ws.length) {

        return 0;

    }


    const longWords =
        ws.filter(
            word =>
                word.length >= 13
        ).length;


    const ratio =
        longWords / ws.length;


    if (ratio <= 0.05) {

        return 1;

    }


    if (ratio <= 0.10) {

        return 0.85;

    }


    if (ratio <= 0.18) {

        return 0.65;

    }


    return 0.40;

}


/* =========================================================
   PROMPT / RESPONSE OVERLAP
   ========================================================= */

function overlapScore(
    prompt,
    response
) {

    const promptWords =
        new Set(
            words(prompt)
        );


    const responseWords =
        new Set(
            words(response)
        );


    if (
        !promptWords.size
    ) {

        return 0;

    }


    let hit = 0;


    for (
        const word of promptWords
    ) {

        if (
            responseWords.has(
                word
            )
        ) {

            hit++;

        }

    }


    return numericScore(
        hit /
        promptWords.size
    );

}


/* =========================================================
   LOCAL CONSTRAINT SCORE
   ========================================================= */

function localConstraintScore(
    prompt,
    response
) {

    const p =
        safeString(prompt)
            .toLowerCase();


    const r =
        safeString(response);


    const checks = [];


    const required =
        requestedSentences(
            prompt
        );


    if (
        required !== null
    ) {

        checks.push(
            sentenceCount(r) ===
            required
                ? 1
                : 0
        );

    }


    if (
        p.includes("simple language") ||
        p.includes("beginner") ||
        p.includes("easy to understand") ||
        p.includes("for a beginner")
    ) {

        checks.push(
            longWordPenalty(r)
        );

    }


    if (
        p.includes(
            "no technical terminology"
        ) ||
        p.includes(
            "do not use technical terminology"
        ) ||
        p.includes(
            "without technical terminology"
        ) ||
        p.includes(
            "non technical"
        )
    ) {

        const technicalTerms = [

            "algorithm",

            "neural network",

            "machine learning",

            "deep learning",

            "backpropagation",

            "gradient descent",

            "transformer",

            "embedding",

            "tokenization",

            "inference",

            "dataset",

            "parameters",

            "classification",

            "regression",

            "optimization",

            "architecture",

            "natural language processing",

            "computer vision",

            "reinforcement learning",

            "quantization",

            "latent space",

            "attention mechanism",

            "api",

            "gpu",

            "cpu"

        ];


        const lower =
            r.toLowerCase();


        const containsTechnical =
            technicalTerms.some(
                term =>
                    lower.includes(
                        term
                    )
            );


        checks.push(
            containsTechnical
                ? 0
                : 1
        );

    }


    if (!checks.length) {

        return 1;

    }


    return numericScore(

        checks.reduce(
            (
                total,
                value
            ) =>
                total + value,
            0
        ) / checks.length

    );

}


/* =========================================================
   LOCAL QUALITY SCORE
   ========================================================= */

function localQualityScore(
    prompt,
    response
) {

    const clean =
        safeString(response)
            .trim();


    if (!clean) {

        return 0;

    }


    let score =
        0.25;


    const overlap =
        overlapScore(
            prompt,
            response
        );


    if (
        overlap >= 0.50
    ) {

        score += 0.35;

    } else if (
        overlap >= 0.25
    ) {

        score += 0.25;

    } else if (
        overlap > 0
    ) {

        score += 0.15;

    }


    const count =
        words(response)
            .length;


    if (
        count >= 8
    ) {

        score += 0.20;

    } else if (
        count >= 4
    ) {

        score += 0.12;

    } else {

        score += 0.05;

    }


    if (
        sentenceCount(response) >= 1
    ) {

        score += 0.20;

    }


    return numericScore(
        score
    );

}


/* =========================================================
   FACTOR PROFILE
   ========================================================= */

function deriveFactorProfile(
    prompt,
    response,
    evaluation
) {

    const constraint =
        Number(
            evaluation?.constraint_score ??
            localConstraintScore(
                prompt,
                response
            )
        );


    const quality =
        Number(
            evaluation?.quality_score ??
            localQualityScore(
                prompt,
                response
            )
        );


    const overlap =
        overlapScore(
            prompt,
            response
        );


    const clarity =
        longWordPenalty(
            response
        );


    const hasContextCue =
        /\b(my|me|i|user|beginner|student|goal|prefer|preference|earlier|previous|context)\b/i
            .test(
                safeString(prompt)
            );


    const personalization =
        hasContextCue

            ? numericScore(
                0.45 * overlap +
                0.55 * constraint
            )

            : numericScore(
                0.50 +
                0.25 * quality
            );


    const reliability =
        numericScore(
            0.70 * constraint +
            0.30 * quality
        );


    const engagement =
        numericScore(
            0.35 * quality +
            0.35 * constraint +
            0.30 * overlap
        );


    const understanding =
        numericScore(
            0.55 * overlap +
            0.45 * quality
        );


    return {

        U: understanding,

        C: clarity,

        P: personalization,

        R: reliability,

        ER: engagement

    };

}


/* =========================================================
   PROFILE RENDER
   ========================================================= */

function renderProfile(
    target,
    profile
) {

    if (!target) {

        return;

    }


    const labels = [

        [
            "U",
            "Understanding"
        ],

        [
            "C",
            "Clarity"
        ],

        [
            "P",
            "Personalization"
        ],

        [
            "R",
            "Reliability"
        ],

        [
            "ER",
            "Engagement & Responsiveness"
        ]

    ];


    target.innerHTML =
        labels
            .map(
                function (
                    item
                ) {

                    const code =
                        item[0];

                    const name =
                        item[1];


                    return `

                        <div class="profile-item">

                            <span class="v">
                                ${formatScore(
                                    profile?.[code]
                                )}
                            </span>

                            <span class="n">
                                ${escapeHtml(
                                    name
                                )}
                            </span>

                            <span class="w">
                                diagnostic
                            </span>

                        </div>

                    `;

                }
            )
            .join("");

}


/* =========================================================
   BASELINE RESPONSE EXTRACTION
   ========================================================= */

function extractBaselineResponse(
    data
) {

    if (!data) {

        return "";

    }


    const candidates = [

        /*
         * CURRENT BOND FLASK CONTRACT
         */

        data?.baseline?.response,


        /*
         * ALTERNATIVE CONTRACT
         */

        data?.baseline_response,


        /*
         * Direct baseline value
         */

        data?.baseline,


        /*
         * OpenAI-compatible structure
         */

        data
            ?.baseline
            ?.choices
            ?.[0]
            ?.message
            ?.content

    ];


    for (
        const candidate of candidates
    ) {

        const value =
            normalizeText(
                candidate
            );


        if (value) {

            return value;

        }

    }


    return "";

}


/* =========================================================
   AHI RESPONSE EXTRACTION
   ========================================================= */

function extractAHIResponse(
    data
) {

    if (!data) {

        return "";

    }


    /*
     * MOST IMPORTANT FIX
     *
     * Flask currently returns:
     *
     * data.ahi_response.response
     */

    const candidates = [

        data
            ?.ahi_response
            ?.response,


        /*
         * Alternative older structure
         */

        data
            ?.ahi
            ?.response,


        /*
         * Direct object/string
         */

        data
            ?.ahi_response,


        data
            ?.ahi,


        /*
         * OpenAI-style fallback
         */

        data
            ?.ahi_response
            ?.choices
            ?.[0]
            ?.message
            ?.content,


        data
            ?.ahi
            ?.choices
            ?.[0]
            ?.message
            ?.content

    ];


    for (
        const candidate of candidates
    ) {

        const value =
            normalizeText(
                candidate
            );


        if (value) {

            return value;

        }

    }


    return "";

}


/* =========================================================
   FINAL BASELINE
   ========================================================= */

function getFinalBaselineResponse(
    data
) {

    const value =
        extractBaselineResponse(
            data
        );


    return value ||
        "No baseline response returned.";

}


/* =========================================================
   FINAL AHI
   ========================================================= */

function getFinalAHIResponse(
    data
) {

    const value =
        extractAHIResponse(
            data
        );


    return value ||
        "No AHI response returned.";

}


/* =========================================================
   RENDER BASELINE
   ========================================================= */

function renderBaselineResponse(
    text
) {

    setAnswer(
        baselineAnswer,
        text,
        "No baseline response returned."
    );

}


/* =========================================================
   RENDER AHI
   ========================================================= */

function renderAHIResponse(
    text
) {

    setAnswer(
        ahiAnswer,
        text,
        "No AHI response returned."
    );

}


/* =========================================================
   UPDATE SCORES
   ========================================================= */

function updateScores(
    evaluation
) {

    if (
        !evaluation ||
        typeof evaluation !== "object"
    ) {

        console.warn(
            "BOND: evaluation object missing."
        );

        return;

    }


    const baseline =
        evaluation.baseline ||
        {};


    const ahi =
        evaluation.ahi ||
        {};


    setMetric(
        baselineScore,
        baseline.score
    );


    setMetric(
        ahiScore,
        ahi.score
    );


    setMetric(
        baselineConstraint,
        baseline.constraint_score
    );


    setMetric(
        ahiConstraint,
        ahi.constraint_score
    );


    setMetric(
        baselineQuality,
        baseline.quality_score
    );


    setMetric(
        ahiQuality,
        ahi.quality_score
    );


    const comparison =
        evaluation.comparison ||
        {};


    const baselineNumber =
        Number(
            baseline.score
        );


    const ahiNumber =
        Number(
            ahi.score
        );


    if (
        difference
    ) {

        if (
            Number.isFinite(
                baselineNumber
            ) &&
            Number.isFinite(
                ahiNumber
            )
        ) {

            difference.textContent =
                (
                    ahiNumber -
                    baselineNumber
                ).toFixed(3);

        } else {

            difference.textContent =
                "—";

        }

    }


    if (improvement) {

        improvement.textContent =
            Number.isFinite(
                Number(
                    comparison.improvement_percent
                )
            )

                ? formatPercent(
                    comparison.improvement_percent
                )

                : "—";

    }


    if (winner) {

        winner.textContent =
            comparison.winner ||
            "—";

    }


    updateFactorProfiles(
        evaluation
    );

}


/* =========================================================
   UPDATE FACTOR PROFILES
   ========================================================= */

function updateFactorProfiles(
    evaluation
) {

    if (!lastPrompt) {

        return;

    }


    const baseline =
        evaluation?.baseline ||
        {};


    const ahi =
        evaluation?.ahi ||
        {};


    const baselineText =
        extractBaselineResponse(
            lastAPIResponse
        );


    const ahiText =
        extractAHIResponse(
            lastAPIResponse
        );


    const baselineProfile =
        deriveFactorProfile(
            lastPrompt,
            baselineText,
            baseline
        );


    const ahiProfile =
        deriveFactorProfile(
            lastPrompt,
            ahiText,
            ahi
        );


    renderProfile(
        profileBaseline,
        baselineProfile
    );


    renderProfile(
        profileAhi,
        ahiProfile
    );

}


/* =========================================================
   SERVER STATUS
   ========================================================= */

async function checkStatus() {

    if (!serverStatus) {

        return false;

    }


    try {

        const response =
            await fetch(
                BOND_CONFIG.apiBase +
                BOND_CONFIG.statusEndpoint,
                {
                    method: "GET",
                    cache: "no-store",
                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );

        }


        const data =
            await response.json();


        console.log(
            "BOND STATUS:",
            data
        );


        if (
            data &&
            data.ai_server
        ) {

            serverStatus.textContent =
                "AI server online";

            serverStatus.className =
                "status-pill online";

            return true;

        }


        serverStatus.textContent =
            "AI server offline";

        serverStatus.className =
            "status-pill error";


        return false;

    } catch (error) {

        console.warn(
            "BOND status check failed:",
            error
        );


        serverStatus.textContent =
            "Backend unavailable";

        serverStatus.className =
            "status-pill error";


        return false;

    }

}


/* =========================================================
   FETCH WITH TIMEOUT
   ========================================================= */

async function fetchWithTimeout(
    url,
    options,
    timeout
) {

    const controller =
        new AbortController();


    const timer =
        setTimeout(
            function () {

                controller.abort();

            },
            timeout
        );


    try {

        return await fetch(
            url,
            {
                ...options,
                signal:
                    controller.signal
            }
        );

    } finally {

        clearTimeout(
            timer
        );

    }

}


/* =========================================================
   MAIN INTERACTION
   ========================================================= */

async function runInteraction() {

    if (
        interactionRunning
    ) {

        return;

    }


    if (!promptInput) {

        console.error(
            "BOND: promptInput not found."
        );

        return;

    }


    if (!runBtn) {

        console.error(
            "BOND: runBtn not found."
        );

        return;

    }


    const prompt =
        safeString(
            promptInput.value
        ).trim();


    if (!prompt) {

        showToast(
            "Please enter a prompt."
        );


        promptInput.focus();


        return;

    }


    interactionRunning =
        true;


    interactionCount++;


    lastPrompt =
        prompt;


    lastAPIResponse =
        null;


    runBtn.disabled =
        true;


    runBtn.textContent =
        "Running…";


    if (serverStatus) {

        serverStatus.textContent =
            "Evaluating interaction…";

        serverStatus.className =
            "status-pill";

    }


    resetPrototypeUI();


    try {

        console.log(
            "================================"
        );


        console.log(
            "BOND INTERACTION",
            interactionCount
        );


        console.log(
            "Prompt:",
            prompt
        );


        console.log(
            "POST:",
            BOND_CONFIG.chatEndpoint
        );


        const response =
            await fetchWithTimeout(

                BOND_CONFIG.apiBase +
                BOND_CONFIG.chatEndpoint,

                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"

                    },

                    body:
                        JSON.stringify({
                            prompt:
                                prompt
                        })

                },

                BOND_CONFIG.requestTimeout

            );


        console.log(
            "HTTP STATUS:",
            response.status
        );


        let data;


        try {

            data =
                await response.json();

        } catch (jsonError) {

            throw new Error(
                "Server returned invalid JSON."
            );

        }


        console.log(
            "BOND API DATA:",
            data
        );


        if (
            !response.ok
        ) {

            throw new Error(
                data?.error ||
                "Server returned HTTP " +
                response.status
            );

        }


        if (
            !data ||
            data.success !== true
        ) {

            throw new Error(
                data?.error ||
                "BOND request failed."
            );

        }


        lastAPIResponse =
            data;


        /* =================================================
           BASELINE
           ================================================= */

        const baselineText =
            getFinalBaselineResponse(
                data
            );


        console.log(
            "BASELINE:",
            baselineText
        );


        renderBaselineResponse(
            baselineText
        );


        /* =================================================
           AHI
           ================================================= */

        const ahiText =
            getFinalAHIResponse(
                data
            );


        console.log(
            "AHI:",
            ahiText
        );


        renderAHIResponse(
            ahiText
        );


        /* =================================================
           EVALUATION
           ================================================= */

        if (
            data.evaluation &&
            typeof data.evaluation === "object"
        ) {

            updateScores(
                data.evaluation
            );

        } else {

            console.warn(
                "BOND: No evaluation object."
            );

        }


        /* =================================================
           DIAGNOSTIC
           ================================================= */

        console.log(
            "Baseline score:",
            data
                ?.evaluation
                ?.baseline
                ?.score
        );


        console.log(
            "AHI score:",
            data
                ?.evaluation
                ?.ahi
                ?.score
        );


        console.log(
            "Winner:",
            data
                ?.evaluation
                ?.comparison
                ?.winner
        );


        console.log(
            "================================"
        );


        if (serverStatus) {

            serverStatus.textContent =
                "Evaluation complete";

            serverStatus.className =
                "status-pill online";

        }


        showToast(
            "Interaction evaluated."
        );


    } catch (error) {

        console.error(
            "BOND INTERACTION ERROR:",
            error
        );


        setAnswer(
            baselineAnswer,
            "",
            "Unable to generate baseline response."
        );


        setAnswer(
            ahiAnswer,
            "",
            "Unable to generate AHI response."
        );


        if (serverStatus) {

            serverStatus.textContent =
                "Evaluation error";

            serverStatus.className =
                "status-pill error";

        }


        let message =
            "Interaction failed.";


        if (
            error?.name ===
            "AbortError"
        ) {

            message =
                "Request timed out.";

        } else if (
            error?.message
        ) {

            message =
                error.message;

        }


        showToast(
            message
        );

    } finally {

        interactionRunning =
            false;


        runBtn.disabled =
            false;


        runBtn.textContent =
            "Run Interaction";

    }

}


/* =========================================================
   API TEST
   ========================================================= */

async function testBondAPI() {

    console.log(
        "BOND: testing /api/chat..."
    );


    try {

        const response =
            await fetch(
                BOND_CONFIG.apiBase +
                BOND_CONFIG.chatEndpoint,
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            prompt:
                                "Explain gravity in one short sentence."

                        })

                }
            );


        console.log(
            "HTTP:",
            response.status
        );


        const data =
            await response.json();


        console.log(
            "FULL API:",
            data
        );


        const baseline =
            getFinalBaselineResponse(
                data
            );


        const ahi =
            getFinalAHIResponse(
                data
            );


        console.log(
            "BASELINE:",
            baseline
        );


        console.log(
            "AHI:",
            ahi
        );


        console.log(
            "BASELINE SCORE:",
            data
                ?.evaluation
                ?.baseline
                ?.score
        );


        console.log(
            "AHI SCORE:",
            data
                ?.evaluation
                ?.ahi
                ?.score
        );


        if (
            ahi ===
            "No AHI response returned."
        ) {

            console.error(
                "BOND: AHI extraction failed."
            );


            return false;

        }


        console.log(
            "BOND: AHI API connection is working."
        );


        return true;

    } catch (error) {

        console.error(
            "BOND API TEST FAILED:",
            error
        );


        return false;

    }

}


/* =========================================================
   DEBUG API DATA
   ========================================================= */

function debugBondData(
    data
) {

    console.group(
        "BOND DEBUG"
    );


    console.log(
        "Full response:",
        data
    );


    console.log(
        "Success:",
        data?.success
    );


    console.log(
        "BOND:",
        data?.bond
    );


    console.log(
        "AHI:",
        data?.ahi
    );


    console.log(
        "Baseline object:",
        data?.baseline
    );


    console.log(
        "AHI object:",
        data?.ahi_response
    );


    console.log(
        "Baseline response:",
        getFinalBaselineResponse(
            data
        )
    );


    console.log(
        "AHI response:",
        getFinalAHIResponse(
            data
        )
    );


    console.log(
        "Evaluation:",
        data?.evaluation
    );


    console.groupEnd();

}


/* =========================================================
   MOBILE MENU
   ========================================================= */

function initializeMenu() {

    if (
        !menuBtn ||
        !navLinks
    ) {

        return;

    }


    menuBtn.addEventListener(
        "click",
        function () {

            navLinks.classList.toggle(
                "show"
            );

        }
    );


    document
        .querySelectorAll(
            ".navlinks a"
        )
        .forEach(
            function (link) {

                link.addEventListener(
                    "click",
                    function () {

                        navLinks.classList.remove(
                            "show"
                        );

                    }
                );

            }
        );

}


/* =========================================================
   ACTIVE NAVIGATION
   ========================================================= */

function initializeSectionObserver() {

    const sections =
        [
            ...document.querySelectorAll(
                "main section[id]"
            )
        ];


    const navItems =
        [
            ...document.querySelectorAll(
                ".navlinks a"
            )
        ];


    if (
        !sections.length ||
        !navItems.length ||
        !("IntersectionObserver" in window)
    ) {

        return;

    }


    const observer =
        new IntersectionObserver(

            function (
                entries
            ) {

                entries.forEach(
                    function (
                        entry
                    ) {

                        if (
                            !entry.isIntersecting
                        ) {

                            return;

                        }


                        navItems.forEach(
                            function (
                                item
                            ) {

                                const target =
                                    item.getAttribute(
                                        "href"
                                    );


                                item.classList.toggle(

                                    "active",

                                    target ===
                                    "#" +
                                    entry.target.id

                                );

                            }
                        );

                    }
                );

            },

            {

                rootMargin:
                    "-35% 0px -55% 0px",

                threshold:
                    0

            }

        );


    sections.forEach(
        function (
            section
        ) {

            observer.observe(
                section
            );

        }
    );

}


/* =========================================================
   EVENT BINDING
   ========================================================= */

function bindEvents() {

    if (runBtn) {

        runBtn.addEventListener(
            "click",
            runInteraction
        );

    }


    if (promptInput) {

        promptInput.addEventListener(

            "keydown",

            function (
                event
            ) {

                if (

                    (
                        event.ctrlKey ||
                        event.metaKey
                    ) &&

                    event.key ===
                    "Enter"

                ) {

                    event.preventDefault();

                    runInteraction();

                }

            }

        );

    }

}


/* =========================================================
   INITIALIZATION
   ========================================================= */

async function initializeBOND() {

    console.log(
        "================================"
    );


    console.log(
        "BOND FRONTEND INITIALIZED"
    );


    console.log(
        BOND_CONFIG.version
    );


    console.log(
        "AHI:",
        BOND_CONFIG.ahiVersion
    );


    console.log(
        "================================"
    );


    console.log(
        "Prompt input:",
        promptInput
    );


    console.log(
        "Run button:",
        runBtn
    );


    console.log(
        "Baseline answer:",
        baselineAnswer
    );


    console.log(
        "AHI answer:",
        ahiAnswer
    );


    bindEvents();


    initializeMenu();


    initializeSectionObserver();


    await checkStatus();


    console.log(
        "BOND frontend ready."
    );

}


/* =========================================================
   GLOBAL BOND DEBUG API
   ========================================================= */

window.BOND =
    window.BOND || {};


window.BOND.version =
    BOND_CONFIG.version;


window.BOND.ahiVersion =
    BOND_CONFIG.ahiVersion;


window.BOND.runInteraction =
    runInteraction;


window.BOND.testAPI =
    testBondAPI;


window.BOND.checkStatus =
    checkStatus;


window.BOND.debug =
    debugBondData;


window.BOND.extractAHI =
    getFinalAHIResponse;


window.BOND.extractBaseline =
    getFinalBaselineResponse;


window.BOND.getLastResponse =
    function () {

        return lastAPIResponse;

    };


/* =========================================================
   DOM READY
   ========================================================= */

if (
    document.readyState ===
    "loading"
) {

    document.addEventListener(
        "DOMContentLoaded",
        initializeBOND,
        {
            once: true
        }
    );

} else {

    initializeBOND();

}


/* =========================================================
   FINAL LOG
   ========================================================= */

console.log(
    "BOND V2.0 frontend loaded."
);


console.log(
    "AHI primary path:",
    "data.ahi_response.response"
);


console.log(
    "API endpoint:",
    "/api/chat"
);


console.log(
    "Ready for interaction."
);


/* =========================================================
   END
   ========================================================= */

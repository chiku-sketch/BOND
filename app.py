from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import re
import json
import math
from collections import Counter


# =========================================================
# BOND V2
# Human-AI Interaction Research Prototype
#
# BASELINE + AHI V2
# Five-Factor Interaction Architecture
# Transparent Provisional Evaluation
#
# AHI PIPELINE
# ---------------------------------------------------------
# Request Analysis
#       ↓
# Constraint Extraction
#       ↓
# Response Planning
#       ↓
# Five-Factor Optimization
#       ↓
# Response Generation
#       ↓
# Self Check
#       ↓
# One Revision Pass
#       ↓
# Final Response
#
# IMPORTANT:
# AHI generation and BOND evaluation are kept separate.
# =========================================================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)


# =========================================================
# CONFIGURATION
# =========================================================

LLAMA_SERVER = "http://127.0.0.1:8080"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

MODEL_NAME = (
    GEMINI_MODEL
    if GEMINI_API_KEY
    else "Qwen2.5-0.5B"
)

BOND_VERSION = "BOND-V2.0"

AHI_VERSION = "AHI-V2"

MAX_TOKENS = 256

DEFAULT_TEMPERATURE = 0.7

REVISION_TEMPERATURE = 0.45

REQUEST_TIMEOUT = 300


# =========================================================
# FIVE CORE FACTORS
# =========================================================

FACTORS = {
    "U": {
        "name": "Understanding",
        "subfactors": {
            "UR": "Requirement Recognition",
            "UI": "Intent Interpretation",
            "UC": "Context Integration",
            "UCR": "Constraint Recognition",
            "UU": "Clarification & Update Handling"
        }
    },

    "C": {
        "name": "Clarity",
        "subfactors": {
            "CC": "Comprehensibility",
            "CS": "Structural Organization",
            "CP": "Precision",
            "CR": "Relevance & Focus",
            "CE": "Explanatory Sufficiency"
        }
    },

    "P": {
        "name": "Personalization",
        "subfactors": {
            "PCR": "Relevant Context Recognition",
            "PLA": "User-Level Adaptation",
            "PPA": "Preference Adaptation",
            "PGS": "Goal & Situation Adaptation",
            "PSC": "Selective Context Use"
        }
    },

    "R": {
        "name": "Reliability",
        "subfactors": {
            "RBC": "Behavioral Consistency",
            "RCC": "Contextual Continuity",
            "RCP": "Constraint Persistence",
            "RUC": "Uncertainty Calibration",
            "RER": "Error Recovery"
        }
    },

    "ER": {
        "name": "Engagement & Responsiveness",
        "subfactors": {
            "ERS": "Interaction Signal Recognition",
            "ERF": "Feedback Responsiveness",
            "ERP": "Progression Awareness",
            "ERA": "Adaptive Continuation",
            "ERG": "Goal-Oriented Engagement"
        }
    }
}


# =========================================================
# TECHNICAL TERMS
# =========================================================

TECHNICAL_TERMS = {
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
    "model parameters",
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
}


# =========================================================
# COMMON STOP WORDS
# =========================================================

STOP_WORDS = {
    "what",
    "when",
    "where",
    "which",
    "whose",
    "whom",
    "this",
    "that",
    "these",
    "those",
    "with",
    "from",
    "into",
    "about",
    "have",
    "has",
    "will",
    "would",
    "could",
    "should",
    "there",
    "their",
    "they",
    "them",
    "your",
    "you",
    "please",
    "explain",
    "tell",
    "give",
    "make",
    "write",
    "show",
    "using",
    "used",
    "than",
    "then",
    "also",
    "just",
    "very",
    "more",
    "some",
    "only",
    "like",
    "need",
    "want",
    "does",
    "how",
    "why"
}


# =========================================================
# WEBSITE
# =========================================================

@app.route("/")
def home():

    return send_from_directory(
        BASE_DIR,
        "index.html"
    )


@app.route("/style.css")
def style():

    return send_from_directory(
        BASE_DIR,
        "style.css"
    )


@app.route("/script.js")
def script():

    return send_from_directory(
        BASE_DIR,
        "script.js"
    )


@app.route("/factor.html")
def factor():

    return send_from_directory(
        BASE_DIR,
        "factor.html"
    )


# =========================================================
# STATUS
# =========================================================

@app.route("/api/status")
def status():

    if GEMINI_API_KEY:
        ai_online = True
    else:
        try:
            response = requests.get(
                f"{LLAMA_SERVER}/health",
                timeout=5
            )

            ai_online = response.status_code == 200

        except requests.RequestException:
            ai_online = False

    return jsonify({
        "status": "online",
        "system": "BOND",
        "model": MODEL_NAME,
        "bond": BOND_VERSION,
        "ahi": AHI_VERSION,
        "factors": 5,
        "ai_server": ai_online
    })

# =========================================================
# BASIC TEXT UTILITIES
# =========================================================

def tokenize(text):

    return re.findall(
        r"\b[a-zA-Z0-9']+\b",
        text.lower()
    )


def content_words(text):

    words = tokenize(text)

    return [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) >= 4
    ]


def unique_ratio(words):

    if not words:
        return 0.0

    return len(set(words)) / len(words)


def count_sentences(text):

    text = text.strip()

    if not text:
        return 0

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    return len([
        s for s in sentences
        if s.strip()
    ])


def count_words(text):

    return len(
        re.findall(
            r"\b[a-zA-Z]+\b",
            text
        )
    )


# =========================================================
# SENTENCE CONSTRAINT
# =========================================================

def extract_sentence_constraint(prompt):

    patterns = [

        r'(\d+)\s+short\s+sentences?',

        r'(\d+)\s+sentences?',

        r'in\s+(\d+)\s+sentences?',

        r'(\d+)\s+sentence\s+answer'

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            prompt.lower()
        )

        if match:

            return int(
                match.group(1)
            )

    return None


# =========================================================
# LENGTH CONSTRAINT
# =========================================================

def extract_word_limit(prompt):

    patterns = [

        r'under\s+(\d+)\s+words?',

        r'less\s+than\s+(\d+)\s+words?',

        r'within\s+(\d+)\s+words?',

        r'(\d+)\s+words?\s+or\s+less',

        r'max(?:imum)?\s+(\d+)\s+words?'

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            prompt.lower()
        )

        if match:

            return int(
                match.group(1)
            )

    return None


# =========================================================
# CONSTRAINT DETECTION
# =========================================================

def detect_constraints(prompt):

    lower = prompt.lower()

    constraints = []

    sentence_limit = extract_sentence_constraint(
        prompt
    )

    if sentence_limit is not None:

        constraints.append({

            "type": "sentence_count",

            "required": sentence_limit

        })


    word_limit = extract_word_limit(
        prompt
    )

    if word_limit is not None:

        constraints.append({

            "type": "word_limit",

            "required": word_limit

        })


    if (
        "simple language" in lower
        or "simple words" in lower
        or "beginner" in lower
        or "easy to understand" in lower
        or "explain simply" in lower
    ):

        constraints.append({

            "type": "simple_language"

        })


    if (
        "no technical terminology" in lower
        or "do not use technical terminology" in lower
        or "without technical terminology" in lower
        or "avoid technical terms" in lower
    ):

        constraints.append({

            "type": "no_technical_terms"

        })


    if (
        "bullet points" in lower
        or "bullet point" in lower
        or "in bullets" in lower
    ):

        constraints.append({

            "type": "bullet_format"

        })


    if (
        "table" in lower
        or "tabular format" in lower
    ):

        constraints.append({

            "type": "table_format"

        })


    if (
        "short answer" in lower
        or "briefly" in lower
        or "brief answer" in lower
    ):

        constraints.append({

            "type": "brief"

        })


    if (
        "detailed" in lower
        or "in detail" in lower
        or "deep explanation" in lower
    ):

        constraints.append({

            "type": "detailed"

        })


    return constraints


# =========================================================
# REQUEST ANALYSIS
# =========================================================

def analyze_request(prompt):

    constraints = detect_constraints(
        prompt
    )

    lower = prompt.lower()

    signals = {

        "question": (
            "?" in prompt
        ),

        "asks_for_explanation": any(
            phrase in lower
            for phrase in [
                "explain",
                "why",
                "how does",
                "what is",
                "describe"
            ]
        ),

        "asks_for_comparison": any(
            phrase in lower
            for phrase in [
                "compare",
                "difference",
                "versus",
                "vs",
                "better than"
            ]
        ),

        "asks_for_steps": any(
            phrase in lower
            for phrase in [
                "steps",
                "step by step",
                "how to"
            ]
        ),

        "asks_for_list": any(
            phrase in lower
            for phrase in [
                "list",
                "examples",
                "points"
            ]
        ),

        "simple_language": any(
            c["type"] == "simple_language"
            for c in constraints
        ),

        "brief": any(
            c["type"] == "brief"
            for c in constraints
        ),

        "detailed": any(
            c["type"] == "detailed"
            for c in constraints
        )

    }


    important_terms = [
        word
        for word in content_words(prompt)
    ]

    return {

        "intent_signals":
            signals,

        "constraints":
            constraints,

        "important_terms":
            important_terms[:40],

        "prompt_word_count":
            count_words(prompt)

    }


# =========================================================
# AHI RESPONSE PLANNING
# =========================================================

def create_response_plan(
    prompt,
    analysis
):

    constraints = analysis[
        "constraints"
    ]

    signals = analysis[
        "intent_signals"
    ]

    plan = {

        "answer_directly": True,

        "use_simple_language":
            signals["simple_language"],

        "be_brief":
            signals["brief"],

        "be_detailed":
            signals["detailed"],

        "sentence_limit":
            None,

        "word_limit":
            None,

        "format":
            "natural",

        "avoid_technical_terms":
            False

    }


    for constraint in constraints:

        ctype = constraint["type"]

        if ctype == "sentence_count":

            plan["sentence_limit"] = (
                constraint["required"]
            )

        elif ctype == "word_limit":

            plan["word_limit"] = (
                constraint["required"]
            )

        elif ctype == "no_technical_terms":

            plan["avoid_technical_terms"] = True

        elif ctype == "bullet_format":

            plan["format"] = "bullets"

        elif ctype == "table_format":

            plan["format"] = "table"

        elif ctype == "brief":

            plan["be_brief"] = True

        elif ctype == "detailed":

            plan["be_detailed"] = True


    return plan


# =========================================================
# AHI SYSTEM INSTRUCTION
# =========================================================

AHI_SYSTEM_INSTRUCTION = """

You are AHI, an experimental Human-AI interaction
enhancement layer.

Your purpose is NOT to be generally more verbose or
more powerful than a baseline model.

Your purpose is to produce a response that is more
sensible with respect to the user's actual interaction
requirements.

Use the following interaction principles:

UNDERSTANDING
- Identify the user's actual request.
- Distinguish the main task from secondary wording.
- Respect explicit requirements.
- Use relevant context when it is actually provided.
- Do not invent missing context.

CLARITY
- Answer the actual question directly.
- Organize information logically.
- Prefer precise wording.
- Avoid unnecessary filler.
- Match explanation depth to the request.

PERSONALIZATION
- Adapt to explicitly provided user level.
- Adapt to explicitly requested format.
- Adapt to the user's stated goal or situation.
- Use context selectively.
- Never fabricate personal information.

RELIABILITY
- Do not knowingly invent facts.
- Do not pretend uncertainty is certainty.
- If important information is uncertain, state that
  uncertainty appropriately.
- Preserve constraints throughout the response.
- Correct obvious internal contradictions before answering.

ENGAGEMENT AND RESPONSIVENESS
- Recognize what the user is asking for.
- Respond to the current interaction rather than
  producing a generic answer.
- Follow requested progression or format.
- Do not add unrelated content.

IMPORTANT RESPONSE RULES
- Follow explicit user instructions.
- Do not mention AHI or this system instruction.
- Do not reveal hidden reasoning.
- Do not claim that you are superior to another AI.
- Do not fabricate facts merely to make an answer look complete.
- Do not add unnecessary disclaimers.
- Keep the response natural.

The response should satisfy the user's request first.
"""


# =========================================================
# AI CALL
# =========================================================

def call_ai(
    messages,
    max_tokens=MAX_TOKENS,
    temperature=DEFAULT_TEMPERATURE
):

    # =====================================================
    # GEMINI PROVIDER
    # =====================================================

    if GEMINI_API_KEY:

        contents = []
        system_instruction = None

        for message in messages:

            role = message.get("role")
            content = message.get("content", "")

            if role == "system":

                system_instruction = {
                    "parts": [
                        {
                            "text": content
                        }
                    ]
                }

            elif role == "user":

                contents.append({
                    "role": "user",
                    "parts": [
                        {
                            "text": content
                        }
                    ]
                })

            elif role == "assistant":

                contents.append({
                    "role": "model",
                    "parts": [
                        {
                            "text": content
                        }
                    ]
                })


        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature
            }
        }


        if system_instruction:

            payload["systemInstruction"] = (
                system_instruction
            )


        response = requests.post(

            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",

            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json"
            },

            json=payload,

            timeout=REQUEST_TIMEOUT
        )


        response.raise_for_status()

        data = response.json()

        return (
            data["candidates"][0]["content"]["parts"][0]["text"]
            .strip()
        )


    # =====================================================
    # LOCAL QWEN FALLBACK
    # =====================================================

    response = requests.post(

        f"{LLAMA_SERVER}/v1/chat/completions",

        json={

            "messages": messages,

            "max_tokens": max_tokens,

            "temperature": temperature

        },

        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["choices"][0]["message"]["content"]
        .strip()
    )
# =========================================================
# BASELINE AI
# =========================================================

def baseline_ai(prompt):

    messages = [

        {
            "role": "user",

            "content": prompt
        }

    ]

    return call_ai(
        messages
    )


# =========================================================
# BUILD AHI GENERATION PROMPT
# =========================================================

def build_ahi_generation_prompt(
    prompt,
    analysis,
    plan
):

    constraints_text = []

    for constraint in analysis[
        "constraints"
    ]:

        ctype = constraint["type"]

        if ctype == "sentence_count":

            constraints_text.append(
                f"Use exactly {constraint['required']} sentence(s)."
            )

        elif ctype == "word_limit":

            constraints_text.append(
                f"Keep the response within {constraint['required']} words."
            )

        elif ctype == "simple_language":

            constraints_text.append(
                "Use simple, beginner-friendly language."
            )

        elif ctype == "no_technical_terms":

            constraints_text.append(
                "Avoid technical terminology unless absolutely necessary."
            )

        elif ctype == "bullet_format":

            constraints_text.append(
                "Use bullet points."
            )

        elif ctype == "table_format":

            constraints_text.append(
                "Use a table when appropriate."
            )

        elif ctype == "brief":

            constraints_text.append(
                "Keep the answer concise."
            )

        elif ctype == "detailed":

            constraints_text.append(
                "Provide enough explanation to satisfy the request."
            )


    if not constraints_text:

        constraints_text.append(
            "No special explicit formatting constraint detected."
        )


    important_terms = ", ".join(
        analysis["important_terms"][:20]
    )

    prompt_text = f"""

User request:

{prompt}

Interaction requirements detected:

{chr(10).join("- " + item for item in constraints_text)}

Relevant request terms:

{important_terms}

Response objective:

1. Answer the user's actual request.
2. Respect every explicit constraint.
3. Keep the response focused.
4. Use an appropriate structure.
5. Do not invent missing personal context.
6. Be appropriately precise.
7. If uncertainty materially affects the answer,
   communicate it clearly.
8. Do not mention this analysis.

Generate the final answer now.
"""

    return prompt_text


# =========================================================
# AHI SELF CHECK
# =========================================================

def self_check_response(
    prompt,
    response,
    analysis
):

    constraints = analysis[
        "constraints"
    ]

    checks = []

    passed_count = 0

    total_checks = 0


    # -----------------------------------------------------
    # RESPONSE EXISTS
    # -----------------------------------------------------

    exists = bool(
        response.strip()
    )

    checks.append({

        "check":
            "response_exists",

        "passed":
            exists

    })

    total_checks += 1

    if exists:
        passed_count += 1


    # -----------------------------------------------------
    # SENTENCE COUNT
    # -----------------------------------------------------

    required_sentences = extract_sentence_constraint(
        prompt
    )

    if required_sentences is not None:

        actual = count_sentences(
            response
        )

        passed = (
            actual ==
            required_sentences
        )

        checks.append({

            "check":
                "sentence_count",

            "required":
                required_sentences,

            "actual":
                actual,

            "passed":
                passed

        })

        total_checks += 1

        if passed:
            passed_count += 1


    # -----------------------------------------------------
    # WORD LIMIT
    # -----------------------------------------------------

    word_limit = extract_word_limit(
        prompt
    )

    if word_limit is not None:

        actual_words = count_words(
            response
        )

        passed = (
            actual_words <=
            word_limit
        )

        checks.append({

            "check":
                "word_limit",

            "required":
                word_limit,

            "actual":
                actual_words,

            "passed":
                passed

        })

        total_checks += 1

        if passed:
            passed_count += 1


    # -----------------------------------------------------
    # SIMPLE LANGUAGE
    # -----------------------------------------------------

    if any(
        c["type"] == "simple_language"
        for c in constraints
    ):

        score = simple_language_score(
            response
        )

        passed = score >= 0.70

        checks.append({

            "check":
                "simple_language",

            "score":
                round(score, 3),

            "passed":
                passed

        })

        total_checks += 1

        if passed:
            passed_count += 1


    # -----------------------------------------------------
    # TECHNICAL TERMS
    # -----------------------------------------------------

    if any(
        c["type"] == "no_technical_terms"
        for c in constraints
    ):

        found = find_technical_terms(
            response
        )

        passed = len(found) == 0

        checks.append({

            "check":
                "technical_terminology",

            "terms_found":
                found,

            "passed":
                passed

        })

        total_checks += 1

        if passed:
            passed_count += 1


    # -----------------------------------------------------
    # DIRECTNESS
    # -----------------------------------------------------

    directness = estimate_directness(
        prompt,
        response
    )

    checks.append({

        "check":
            "directness",

        "score":
            round(directness, 3)

    })

    total_checks += 1

    if directness >= 0.45:
        passed_count += 1


    if total_checks:

        score = (
            passed_count /
            total_checks
        )

    else:

        score = 1.0


    return {

        "score":
            round(score, 3),

        "checks":
            checks

    }


# =========================================================
# AHI REVISION DECISION
# =========================================================

def should_revise(
    self_check
):

    score = self_check[
        "score"
    ]

    failed_checks = [

        check
        for check in self_check[
            "checks"
        ]

        if check.get("passed") is False
    ]

    return (
        score < 0.85
        and
        len(failed_checks) > 0
    )


# =========================================================
# AHI REVISION PROMPT
# =========================================================

def build_revision_prompt(
    prompt,
    response,
    self_check
):

    failed = []

    for check in self_check[
        "checks"
    ]:

        if check.get("passed") is False:

            failed.append(
                json.dumps(
                    check,
                    ensure_ascii=False
                )
            )


    failed_text = "\n".join(
        failed
    )

    return f"""

Original user request:

{prompt}

Candidate response:

{response}

The response failed the following interaction checks:

{failed_text}

Revise the candidate response so that it better
satisfies the original request.

Rules:

- Preserve the actual meaning.
- Do not add unrelated information.
- Do not invent facts.
- Follow the original explicit constraints.
- Improve only what needs improvement.
- Return ONLY the revised answer.
"""


# =========================================================
# AHI AI
# =========================================================

def ahi_ai(prompt):

    # -----------------------------------------------------
    # STEP 1 — REQUEST ANALYSIS
    # -----------------------------------------------------

    analysis = analyze_request(
        prompt
    )


    # -----------------------------------------------------
    # STEP 2 — RESPONSE PLAN
    # -----------------------------------------------------

    plan = create_response_plan(
        prompt,
        analysis
    )


    # -----------------------------------------------------
    # STEP 3 — GENERATION
    # -----------------------------------------------------

    generation_prompt = (
        build_ahi_generation_prompt(
            prompt,
            analysis,
            plan
        )
    )


    messages = [

        {
            "role": "system",

            "content":
                AHI_SYSTEM_INSTRUCTION
        },

        {
            "role": "user",

            "content":
                generation_prompt
        }

    ]


    response = call_ai(

        messages,

        max_tokens=MAX_TOKENS,

        temperature=DEFAULT_TEMPERATURE

    )


    # -----------------------------------------------------
    # STEP 4 — SELF CHECK
    # -----------------------------------------------------

    initial_check = self_check_response(

        prompt,

        response,

        analysis

    )


    revision_performed = False

    final_check = initial_check


    # -----------------------------------------------------
    # STEP 5 — ONE REVISION PASS
    # -----------------------------------------------------

    if should_revise(
        initial_check
    ):

        revision_prompt = (
            build_revision_prompt(
                prompt,
                response,
                initial_check
            )
        )


        revision_messages = [

            {
                "role": "system",

                "content":
                    AHI_SYSTEM_INSTRUCTION
            },

            {
                "role": "user",

                "content":
                    revision_prompt
            }

        ]


        revised_response = call_ai(

            revision_messages,

            max_tokens=MAX_TOKENS,

            temperature=REVISION_TEMPERATURE

        )


        revised_check = self_check_response(

            prompt,

            revised_response,

            analysis

        )


        # -------------------------------------------------
        # Keep the better candidate
        # -------------------------------------------------

        if (
            revised_check["score"]
            >=
            initial_check["score"]
        ):

            response = (
                revised_response
            )

            final_check = (
                revised_check
            )

            revision_performed = True


    return {

        "response":
            response,

        "analysis":
            analysis,

        "plan":
            plan,

        "self_check":
            final_check,

        "revision_performed":
            revision_performed

    }


# =========================================================
# TECHNICAL TERM CHECK
# =========================================================

def find_technical_terms(text):

    lower_text = text.lower()

    found = []

    for term in TECHNICAL_TERMS:

        if term in lower_text:

            found.append(term)

    return sorted(
        list(set(found))
    )


# =========================================================
# SIMPLE LANGUAGE SCORE
# =========================================================

def simple_language_score(text):

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    if not words:

        return 0.0


    long_words = [

        word
        for word in words

        if len(word) >= 13
    ]


    ratio = (
        len(long_words)
        /
        len(words)
    )


    if ratio <= 0.05:

        return 1.0

    elif ratio <= 0.10:

        return 0.85

    elif ratio <= 0.18:

        return 0.65

    else:

        return 0.40


# =========================================================
# KEYWORD OVERLAP
# =========================================================

def keyword_overlap(
    prompt,
    response
):

    prompt_words = set(
        content_words(prompt)
    )

    response_words = set(
        content_words(response)
    )

    if not prompt_words:

        return 0.0

    overlap = (
        len(
            prompt_words
            &
            response_words
        )
        /
        len(prompt_words)
    )

    return min(
        overlap,
        1.0
    )


# =========================================================
# DIRECTNESS
# =========================================================

def estimate_directness(
    prompt,
    response
):

    if not response.strip():

        return 0.0


    words = tokenize(
        response
    )

    if not words:

        return 0.0


    response_word_count = len(
        words
    )


    overlap = keyword_overlap(
        prompt,
        response
    )


    filler_phrases = [

        "sure",
        "of course",
        "certainly",
        "as an ai",
        "i hope this helps",
        "let me explain",
        "it is important to note",
        "in today's world"

    ]


    filler_count = sum(

        response.lower().count(
            phrase
        )

        for phrase in filler_phrases
    )


    filler_penalty = min(
        filler_count * 0.08,
        0.30
    )


    if response_word_count <= 15:

        length_score = 0.75

    elif response_word_count <= 80:

        length_score = 1.0

    elif response_word_count <= 180:

        length_score = 0.90

    else:

        length_score = 0.72


    score = (

        overlap * 0.55

        +

        length_score * 0.45

        -

        filler_penalty

    )


    return max(
        0.0,
        min(score, 1.0)
    )


# =========================================================
# CONSTRAINT EVALUATION
# =========================================================

def evaluate_constraints(
    prompt,
    response
):

    constraints = []

    total_possible = 0

    total_score = 0.0


    # -----------------------------------------------------
    # SENTENCE COUNT
    # -----------------------------------------------------

    required_sentences = (
        extract_sentence_constraint(
            prompt
        )
    )


    if required_sentences is not None:

        actual_sentences = (
            count_sentences(
                response
            )
        )

        passed = (
            actual_sentences
            ==
            required_sentences
        )


        constraints.append({

            "constraint":
                f"{required_sentences} sentence(s)",

            "actual":
                actual_sentences,

            "passed":
                passed,

            "score":
                1.0 if passed else 0.0

        })


        total_possible += 1

        if passed:

            total_score += 1


    # -----------------------------------------------------
    # WORD LIMIT
    # -----------------------------------------------------

    word_limit = extract_word_limit(
        prompt
    )


    if word_limit is not None:

        actual_words = count_words(
            response
        )

        passed = (
            actual_words <=
            word_limit
        )


        constraints.append({

            "constraint":
                f"maximum {word_limit} words",

            "actual":
                actual_words,

            "passed":
                passed,

            "score":
                1.0 if passed else 0.0

        })


        total_possible += 1

        if passed:

            total_score += 1


    # -----------------------------------------------------
    # SIMPLE LANGUAGE
    # -----------------------------------------------------

    lower = prompt.lower()


    if (
        "simple language" in lower
        or "simple words" in lower
        or "beginner" in lower
        or "easy to understand" in lower
        or "explain simply" in lower
    ):

        score = simple_language_score(
            response
        )

        passed = score >= 0.70


        constraints.append({

            "constraint":
                "simple language",

            "passed":
                passed,

            "score":
                round(score, 3)

        })


        total_possible += 1

        total_score += score


    # -----------------------------------------------------
    # NO TECHNICAL TERMINOLOGY
    # -----------------------------------------------------

    if (
        "no technical terminology"
        in lower

        or

        "do not use technical terminology"
        in lower

        or

        "without technical terminology"
        in lower

        or

        "avoid technical terms"
        in lower
    ):

        technical_terms = (
            find_technical_terms(
                response
            )
        )


        passed = (
            len(technical_terms)
            == 0
        )


        constraints.append({

            "constraint":
                "no technical terminology",

            "passed":
                passed,

            "technical_terms_found":
                technical_terms,

            "score":
                1.0 if passed else 0.0

        })


        total_possible += 1

        if passed:

            total_score += 1


    # -----------------------------------------------------
    # FINAL
    # -----------------------------------------------------

    if total_possible == 0:

        constraint_score = 1.0

    else:

        constraint_score = (
            total_score
            /
            total_possible
        )


    return {

        "constraint_score":
            round(
                constraint_score,
                3
            ),

        "constraints":
            constraints

    }


# =========================================================
# QUALITY COMPONENTS
# =========================================================

def relevance_score(
    prompt,
    response
):

    overlap = keyword_overlap(
        prompt,
        response
    )

    if overlap >= 0.50:

        return 1.0

    elif overlap >= 0.35:

        return 0.85

    elif overlap >= 0.20:

        return 0.70

    elif overlap > 0:

        return 0.50

    return 0.25


def structure_score(
    response
):

    if not response.strip():

        return 0.0


    sentences = count_sentences(
        response
    )

    words = count_words(
        response
    )


    score = 0.0


    if sentences >= 1:

        score += 0.40


    if words >= 8:

        score += 0.30

    elif words >= 4:

        score += 0.18


    if (
        "\n-" in response
        or
        "\n*" in response
        or
        "\n1." in response
        or
        "\n2." in response
    ):

        score += 0.30

    else:

        score += 0.20


    return min(
        score,
        1.0
    )


def precision_score(
    prompt,
    response
):

    if not response.strip():

        return 0.0


    directness = estimate_directness(
        prompt,
        response
    )


    repetition = repetition_score(
        response
    )


    return max(

        0.0,

        min(

            (
                directness * 0.65
                +
                repetition * 0.35
            ),

            1.0

        )

    )


def repetition_score(
    response
):

    words = content_words(
        response
    )

    if len(words) < 5:

        return 1.0


    counts = Counter(
        words
    )


    repeated = sum(

        count - 1

        for count in counts.values()

        if count > 2
    )


    ratio = (
        repeated
        /
        len(words)
    )


    if ratio <= 0.05:

        return 1.0

    elif ratio <= 0.10:

        return 0.85

    elif ratio <= 0.20:

        return 0.65

    return 0.40


def completeness_score(
    prompt,
    response
):

    if not response.strip():

        return 0.0


    words = count_words(
        response
    )


    overlap = keyword_overlap(
        prompt,
        response
    )


    if words < 4:

        length = 0.30

    elif words < 8:

        length = 0.55

    elif words < 20:

        length = 0.75

    else:

        length = 1.0


    score = (

        length * 0.45

        +

        overlap * 0.55

    )


    return min(
        score,
        1.0
    )


# =========================================================
# QUALITY EVALUATION
# =========================================================

def evaluate_quality(
    prompt,
    response
):

    if not response.strip():

        return 0.0


    relevance = relevance_score(
        prompt,
        response
    )


    structure = structure_score(
        response
    )


    precision = precision_score(
        prompt,
        response
    )


    completeness = completeness_score(
        prompt,
        response
    )


    score = (

        relevance * 0.35

        +

        structure * 0.20

        +

        precision * 0.25

        +

        completeness * 0.20

    )


    return round(
        min(score, 1.0),
        3
    )


# =========================================================
# FIVE FACTOR HEURISTICS
# =========================================================

def evaluate_understanding(
    prompt,
    response
):

    relevance = relevance_score(
        prompt,
        response
    )

    overlap = keyword_overlap(
        prompt,
        response
    )

    directness = estimate_directness(
        prompt,
        response
    )


    score = (

        relevance * 0.45

        +

        overlap * 0.25

        +

        directness * 0.30

    )


    return round(
        min(score, 1.0),
        3
    )


def evaluate_clarity(
    prompt,
    response
):

    structure = structure_score(
        response
    )

    precision = precision_score(
        prompt,
        response
    )

    completeness = completeness_score(
        prompt,
        response
    )


    score = (

        structure * 0.35

        +

        precision * 0.40

        +

        completeness * 0.25

    )


    return round(
        min(score, 1.0),
        3
    )


def evaluate_personalization(
    prompt,
    response
):

    lower = prompt.lower()


    adaptation_signals = 0

    possible = 0


    # Explicit simplicity requirement
    if (
        "simple language" in lower
        or "beginner" in lower
        or "easy to understand" in lower
    ):

        possible += 1

        if simple_language_score(
            response
        ) >= 0.70:

            adaptation_signals += 1


    # Format requirement
    if (
        "bullet" in lower
        or "table" in lower
    ):

        possible += 1

        if (
            "\n-" in response
            or
            "\n*" in response
            or
            "|" in response
        ):

            adaptation_signals += 1


    # Direct response to user's situation
    if any(
        phrase in lower
        for phrase in [
            "for me",
            "my situation",
            "my case",
            "i need"
        ]
    ):

        possible += 1

        if keyword_overlap(
            prompt,
            response
        ) >= 0.20:

            adaptation_signals += 1


    # No explicit adaptation requirement
    if possible == 0:

        return 0.50


    return round(
        adaptation_signals
        /
        possible,
        3
    )


def evaluate_reliability(
    prompt,
    response
):

    constraint_result = (
        evaluate_constraints(
            prompt,
            response
        )
    )


    constraint_score = (
        constraint_result[
            "constraint_score"
        ]
    )


    repetition = repetition_score(
        response
    )


    uncertainty = uncertainty_calibration_score(
        prompt,
        response
    )


    score = (

        constraint_score * 0.50

        +

        repetition * 0.25

        +

        uncertainty * 0.25

    )


    return round(
        min(score, 1.0),
        3
    )


def evaluate_engagement(
    prompt,
    response
):

    directness = estimate_directness(
        prompt,
        response
    )


    relevance = relevance_score(
        prompt,
        response
    )


    progression = progression_score(
        prompt,
        response
    )


    score = (

        directness * 0.40

        +

        relevance * 0.35

        +

        progression * 0.25

    )


    return round(
        min(score, 1.0),
        3
    )


# =========================================================
# SUPPORTING RELIABILITY HEURISTIC
# =========================================================

def uncertainty_calibration_score(
    prompt,
    response
):

    uncertain_signals = [

        "maybe",

        "possibly",

        "likely",

        "uncertain",

        "not sure",

        "depends",

        "cannot determine",

        "i don't know"

    ]


    factual_question_signals = [

        "when",

        "where",

        "who",

        "which",

        "how many",

        "what year",

        "what is"

    ]


    prompt_lower = prompt.lower()

    response_lower = response.lower()


    appears_factual = any(

        signal in prompt_lower

        for signal
        in factual_question_signals
    )


    if not appears_factual:

        return 0.75


    has_uncertainty = any(

        signal in response_lower

        for signal
        in uncertain_signals
    )


    if has_uncertainty:

        return 0.85


    return 0.70


# =========================================================
# PROGRESSION HEURISTIC
# =========================================================

def progression_score(
    prompt,
    response
):

    lower = prompt.lower()


    if (
        "step by step" in lower
        or
        "steps" in lower
        or
        "process" in lower
    ):

        if (
            "\n1." in response
            or
            "\n2." in response
            or
            "\n-" in response
            or
            "\n*" in response
        ):

            return 1.0

        return 0.55


    return 0.75


# =========================================================
# SUBFACTOR ESTIMATION
# =========================================================

def generate_subfactor_scores(
    prompt,
    response,
    factor_scores
):

    U = factor_scores["U"]
    C = factor_scores["C"]
    P = factor_scores["P"]
    R = factor_scores["R"]
    ER = factor_scores["ER"]


    return {

        "UR": U,
        "UI": U,
        "UC": P,
        "UCR": R,
        "UU": ER,

        "CC": C,
        "CS": structure_score(
            response
        ),
        "CP": precision_score(
            prompt,
            response
        ),
        "CR": relevance_score(
            prompt,
            response
        ),
        "CE": completeness_score(
            prompt,
            response
        ),

        "PCR": P,
        "PLA": P,
        "PPA": P,
        "PGS": P,
        "PSC": P,

        "RBC": R,
        "RCC": R,
        "RCP": R,
        "RUC": R,
        "RER": R,

        "ERS": ER,
        "ERF": ER,
        "ERP": ER,
        "ERA": ER,
        "ERG": ER

    }


# =========================================================
# FIVE FACTOR EVALUATION
# =========================================================

def evaluate_five_factors(
    prompt,
    response
):

    factor_scores = {

        "U":
            evaluate_understanding(
                prompt,
                response
            ),

        "C":
            evaluate_clarity(
                prompt,
                response
            ),

        "P":
            evaluate_personalization(
                prompt,
                response
            ),

        "R":
            evaluate_reliability(
                prompt,
                response
            ),

        "ER":
            evaluate_engagement(
                prompt,
                response
            )

    }


    subfactor_scores = (
        generate_subfactor_scores(
            prompt,
            response,
            factor_scores
        )
    )


    # -----------------------------------------------------
    # Equal-weight BOND formula
    # -----------------------------------------------------

    bond_score = (

        factor_scores["U"]

        +

        factor_scores["C"]

        +

        factor_scores["P"]

        +

        factor_scores["R"]

        +

        factor_scores["ER"]

    ) / 5


    return {

        "factors":
            factor_scores,

        "subfactors":
            subfactor_scores,

        "bond_score":
            round(
                bond_score,
                3
            )

    }


# =========================================================
# FULL RESPONSE EVALUATION
# =========================================================

def evaluate_response(
    prompt,
    response
):

    constraint_result = (
        evaluate_constraints(
            prompt,
            response
        )
    )


    quality_score = (
        evaluate_quality(
            prompt,
            response
        )
    )


    factor_result = (
        evaluate_five_factors(
            prompt,
            response
        )
    )


    bond_score = (
        factor_result[
            "bond_score"
        ]
    )


    return {

        "score":
            round(
                bond_score,
                3
            ),

        "bond_score":
            round(
                bond_score,
                3
            ),

        "constraint_score":
            constraint_result[
                "constraint_score"
            ],

        "quality_score":
            quality_score,

        "factors":
            factor_result[
                "factors"
            ],

        "subfactors":
            factor_result[
                "subfactors"
            ],

        "constraints":
            constraint_result[
                "constraints"
            ]

    }


# =========================================================
# FULL BOND EVALUATION
# =========================================================

def evaluate_bond(
    prompt,
    baseline_response,
    ahi_response
):

    baseline = evaluate_response(
        prompt,
        baseline_response
    )


    ahi = evaluate_response(
        prompt,
        ahi_response
    )


    improvement = round(

        (
            ahi["bond_score"]
            -
            baseline["bond_score"]
        )
        * 100,

        2

    )


    if (
        ahi["bond_score"]
        >
        baseline["bond_score"]
    ):

        winner = "AHI"

    elif (
        ahi["bond_score"]
        <
        baseline["bond_score"]
    ):

        winner = "BASELINE"

    else:

        winner = "TIE"


    return {

        "baseline":
            baseline,

        "ahi":
            ahi,

        "comparison": {

            "improvement_percent":
                improvement,

            "winner":
                winner,

            "score_difference":
                round(
                    ahi["bond_score"]
                    -
                    baseline["bond_score"],
                    3
                )

        },

        "formula": {

            "factor_weight":
                "Equal weight",

            "bond":
                "BOND = (U + C + P + R + ER) / 5"

        },

        "method":
            "BOND-V2.0-FIVE-FACTOR-TRANSPARENT"

    }


# =========================================================
# API CHAT
# =========================================================

@app.route(
    "/api/chat",
    methods=["POST"]
)
def chat():

    data = (
        request
        .get_json(
            silent=True
        )
        or {}
    )


    prompt = (
        data
        .get(
            "prompt",
            ""
        )
        .strip()
    )


    if not prompt:

        return jsonify({

            "success":
                False,

            "error":
                "No prompt provided."

        }), 400


    try:

        # -------------------------------------------------
        # BASELINE
        # -------------------------------------------------

        baseline_response = (
            baseline_ai(
                prompt
            )
        )


        # -------------------------------------------------
        # AHI
        # -------------------------------------------------

        ahi_result = ahi_ai(
            prompt
        )


        ahi_response = (
            ahi_result[
                "response"
            ]
        )


        # -------------------------------------------------
        # EVALUATION
        # -------------------------------------------------

        evaluation = evaluate_bond(

            prompt,

            baseline_response,

            ahi_response

        )


        # -------------------------------------------------
        # RETURN
        # -------------------------------------------------

        return jsonify({

            "success":
                True,

            "bond":
                BOND_VERSION,

            "ahi_version":
                AHI_VERSION,

            "model":
                MODEL_NAME,

            "prompt":
                prompt,


            "baseline": {

                "response":
                    baseline_response

            },


            "ahi": {

                "response":
                    ahi_response

            },


            "ahi_response": {

                "response":
                    ahi_response,

                "analysis":
                    ahi_result[
                        "analysis"
                    ],

                "plan":
                    ahi_result[
                        "plan"
                    ],

                "self_check":
                    ahi_result[
                        "self_check"
                    ],

                "revision_performed":
                    ahi_result[
                        "revision_performed"
                    ]

            },


            "evaluation":
                evaluation

        })


    except requests.exceptions.Timeout:

        return jsonify({

            "success":
                False,

            "error":
                "AI server timed out."

        }), 504


    except requests.exceptions.ConnectionError:

        return jsonify({

            "success":
                False,

            "error":
                "Cannot connect to llama-server on port 8080."

        }), 503


    except requests.exceptions.RequestException as e:

        return jsonify({

            "success":
                False,

            "error":
                "AI server request failed: "
                + str(e)

        }), 500


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# =========================================================
# API — FACTORS
# =========================================================

@app.route(
    "/api/factors"
)
def factors():

    return jsonify({

        "success":
            True,

        "bond":
            BOND_VERSION,

        "factors":
            FACTORS

    })


# =========================================================
# API — ARCHITECTURE
# =========================================================

@app.route(
    "/api/ahi"
)
def ahi_info():

    return jsonify({

        "success":
            True,

        "version":
            AHI_VERSION,

        "architecture": [

            "Request Analysis",

            "Constraint Extraction",

            "Response Planning",

            "Five-Factor Optimization",

            "Response Generation",

            "Self Check",

            "One Revision Pass",

            "Final Response"

        ],

        "factors": {

            "U":
                "Understanding",

            "C":
                "Clarity",

            "P":
                "Personalization",

            "R":
                "Reliability",

            "ER":
                "Engagement & Responsiveness"

        }

    })


# =========================================================
# START BOND
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "========================================"
    )

    print(
        "        BOND RESEARCH PROTOTYPE"
    )

    print(
        "========================================"
    )

    print()

    print(
        "Website   : http://127.0.0.1:5000"
    )

    print(
        "AI        : http://127.0.0.1:8080"
    )

    print(
        "Model     : "
        + MODEL_NAME
    )

    print(
        "BOND      : "
        + BOND_VERSION
    )

    print(
        "AHI       : "
        + AHI_VERSION
    )

    print(
        "Factors   : 5"
    )

    print(
        "Subfactors: 25"
    )

    print(
        "Mode      : Baseline + AHI + Evaluation"
    )

    print(
        "Evaluator : Five-Factor Transparent Heuristic"
    )

    print()

    print(
        "AHI Pipeline:"
    )

    print(
        "  Request Analysis"
    )

    print(
        "  -> Constraint Extraction"
    )

    print(
        "  -> Response Planning"
    )

    print(
        "  -> Five-Factor Optimization"
    )

    print(
        "  -> Response Generation"
    )

    print(
        "  -> Self Check"
    )

    print(
        "  -> One Revision Pass"
    )

    print(
        "  -> Final Response"
    )

    print()

    print(
        "========================================"
    )

    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )

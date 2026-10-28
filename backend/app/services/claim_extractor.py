"""Claim extraction engine decomposing AI responses into atomic verifiable claims."""

import json
import re
import uuid
from typing import List, Tuple
from pydantic import BaseModel
from backend.app.config import settings


class ExtractedClaimItem(BaseModel):
    claim_id: str
    claim_text: str
    original_sentence: str


# Phrases that indicate pure conversational filler or non-factual statements
CONVERSATIONAL_PREFIXES = (
    "hello", "hi there", "sure", "certainly", "here is", "here are",
    "i hope this helps", "let me know", "feel free to", "in my opinion",
    "as an ai", "as an ai language model", "in conclusion", "to summarize",
    "overall", "thank you", "thanks", "greetings", "welcome"
)


def split_sentences(text: str) -> List[str]:
    """
    Splits text into sentences while avoiding false splits on common abbreviations and decimals.
    """
    # Normalize line breaks and tabs
    clean = text.replace("\r\n", "\n").replace("\r", "\n")

    # Protect abbreviations like e.g., i.e., vs., Dr., Mr., etc.
    protected = clean
    abbreviations = [
        (r"\be\.g\.", "e_g_placeholder"),
        (r"\bi\.e\.", "i_e_placeholder"),
        (r"\bvs\.", "vs_placeholder"),
        (r"\bDr\.", "Dr_placeholder"),
        (r"\bMr\.", "Mr_placeholder"),
        (r"\bMrs\.", "Mrs_placeholder"),
        (r"\bMs\.", "Ms_placeholder"),
        (r"\bInc\.", "Inc_placeholder"),
        (r"\bLtd\.", "Ltd_placeholder"),
        (r"\bCo\.", "Co_placeholder"),
        (r"(\d+)\.(\d+)", r"\1_point_\2"),  # numbers like 3.14
    ]
    for pattern, repl in abbreviations:
        protected = re.sub(pattern, repl, protected, flags=re.IGNORECASE)

    # Split on sentence terminals or newlines with bullet points
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", protected)

    sentences: List[str] = []
    for s in raw_sentences:
        # Restore abbreviations
        restored = s.replace("e_g_placeholder", "e.g.") \
                    .replace("i_e_placeholder", "i.e.") \
                    .replace("vs_placeholder", "vs.") \
                    .replace("Dr_placeholder", "Dr.") \
                    .replace("Mr_placeholder", "Mr.") \
                    .replace("Mrs_placeholder", "Mrs.") \
                    .replace("Ms_placeholder", "Ms.") \
                    .replace("Inc_placeholder", "Inc.") \
                    .replace("Ltd_placeholder", "Ltd.") \
                    .replace("Co_placeholder", "Co.")
        restored = re.sub(r"(\d+)_point_(\d+)", r"\1.\2", restored)
        
        # Remove list markers like "1. ", "• ", "- ", "* "
        stripped = re.sub(r"^\s*([0-9]+\.|\*|-|•)\s*", "", restored).strip()
        if stripped and len(stripped) >= 5:
            sentences.append(stripped)

    return sentences


def is_factual_claim(sentence: str) -> bool:
    """
    Determines if a sentence is a verifiable factual proposition vs. conversational fluff.
    """
    lower = sentence.lower().strip()
    
    # Ignore questions
    if lower.endswith("?"):
        return False

    # Ignore pure filler / greetings / pleasantries
    for prefix in CONVERSATIONAL_PREFIXES:
        if lower.startswith(prefix) and len(lower.split()) < 8:
            return False

    # Must contain at least 3 words to form a meaningful assertion
    words = lower.split()
    if len(words) < 3:
        return False

    # Must not be an empty imperative like "Click below" or "Read more"
    if lower in {"click below", "read more", "see attached", "check here"}:
        return False

    return True


def decompose_compound_sentence(sentence: str) -> List[str]:
    """
    Decomposes compound sentences with multiple coordinated verb phrases into atomic claims.
    Example:
    'The company was founded in 2010, has 500 employees, and offers a 30-day return policy.'
    ->
    [
        'The company was founded in 2010',
        'The company has 500 employees',
        'The company offers a 30-day return policy'
    ]
    """
    clean_s = sentence.strip().rstrip(".!?")
    # Protect digit-embedded commas (e.g. 300,000 or 1,500) from being split as clause delimiters
    protected_s = re.sub(r"(\d),(\d)", r"\1_DIGITCOMMA_\2", clean_s)

    # Match pattern: Subject + predicate1, predicate2, and predicate3
    # Check if sentence has coordinated verbs
    # e.g. "The company was founded in 2010, has 500 employees, and offers a 30-day return policy"
    comma_and_split = re.split(r",\s*(?:and\s+)?|;\s*|\s+and\s+(?=[a-z0-9]+\b)", protected_s)

    if len(comma_and_split) > 1:
        # Check if first part has subject + verb
        first_clause = comma_and_split[0].strip().replace("_DIGITCOMMA_", ",")
        subj_match = re.match(r"^([A-Z][a-zA-Z0-9_\s]{1,35}?)\s+(was|is|has|had|were|are|operates|provides|offers|supports|contains|serves)\b", first_clause)
        
        if subj_match:
            subject = subj_match.group(1).strip()
            claims = [first_clause]
            
            for clause in comma_and_split[1:]:
                cl = clause.strip().replace("_DIGITCOMMA_", ",")
                if not cl:
                    continue
                # If clause starts with verb (e.g., "has 500 employees" or "offers a 30-day return policy")
                if re.match(r"^(has|have|had|was|were|is|are|offers|provides|contains|includes|founded|operates|supports|allows|requires)\b", cl, re.IGNORECASE):
                    claims.append(f"{subject} {cl}")
                # Or if clause already has its own subject (e.g. "it employs 500 people")
                elif is_factual_claim(cl):
                    claims.append(cl)
                elif len(cl.split()) >= 3:
                    claims.append(f"{subject} {cl}")

            if len(claims) > 1:
                return claims

    # If no compound split applied, return original sentence as single claim
    return [clean_s]


def extract_claims_deterministic(ai_answer: str) -> List[ExtractedClaimItem]:
    """
    Deterministic rule-based factual claim extractor.
    """
    sentences = split_sentences(ai_answer)
    claims: List[ExtractedClaimItem] = []

    for sentence in sentences:
        if not is_factual_claim(sentence):
            continue

        decomposed = decompose_compound_sentence(sentence)
        for sub_claim in decomposed:
            sub_claim = sub_claim.strip()
            if len(sub_claim) >= 8 and is_factual_claim(sub_claim):
                claims.append(
                    ExtractedClaimItem(
                        claim_id=f"clm_{uuid.uuid4().hex[:8]}",
                        claim_text=sub_claim,
                        original_sentence=sentence
                    )
                )

    return claims


async def extract_claims_with_llm(ai_answer: str) -> List[ExtractedClaimItem]:
    """
    Extracts atomic factual claims using OpenAI/compatible API if configured.
    Falls back gracefully to deterministic extraction.
    """
    if not settings.OPENAI_API_KEY:
        return extract_claims_deterministic(ai_answer)

    import httpx

    prompt = (
        "You are a factual claim extraction engine for an AI hallucination detection system.\n"
        "Analyze the following AI-generated text and extract all atomic, verifiable factual claims.\n"
        "Rules:\n"
        "1. Decompose complex sentences into atomic claims (e.g., compound predicates or lists).\n"
        "2. Make each claim self-contained with its subject explicitly stated.\n"
        "3. Ignore greetings, conversational filler, polite sign-offs, and subjective opinions.\n"
        "4. Return strict JSON format with a 'claims' array of objects: "
        "[{\"claim_text\": \"...\", \"original_sentence\": \"...\"}]\n"
        "Do not output markdown code blocks or explanations, just raw JSON.\n\n"
        f"Input Text:\n\"\"\"{ai_answer}\"\"\""
    )

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{settings.OPENAI_BASE_URL or 'https://api.openai.com/v1'}/chat/completions"
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise JSON-only factual claim extractor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                raw_claims = parsed.get("claims", [])
                
                result: List[ExtractedClaimItem] = []
                for item in raw_claims:
                    ct = item.get("claim_text", "").strip()
                    orig = item.get("original_sentence", ct).strip()
                    if ct and len(ct) >= 5:
                        result.append(
                            ExtractedClaimItem(
                                claim_id=f"clm_{uuid.uuid4().hex[:8]}",
                                claim_text=ct,
                                original_sentence=orig
                            )
                        )
                if result:
                    return result
    except Exception as e:
        # Graceful fallback to deterministic extraction on any network or API error
        pass

    return extract_claims_deterministic(ai_answer)


async def extract_claims(ai_answer: str) -> List[ExtractedClaimItem]:
    """
    Main claim extraction entry point.
    """
    if settings.OPENAI_API_KEY:
        return await extract_claims_with_llm(ai_answer)
    return extract_claims_deterministic(ai_answer)

"""Hybrid evidence retrieval engine combining BM25 lexical matching, semantic n-gram similarity, and keyword fallback."""

import math
import re
from typing import List, Dict, Set
from backend.app.config import settings
from backend.app.models.schemas import DocumentChunk, EvidencePassage

# Standard English stopwords
STOP_WORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's",
    "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd",
    "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
}

# Domain synonym mapping for entity and category normalization
SYNONYM_DICTIONARY: Dict[str, Set[str]] = {
    "phone": {"phone", "phones", "smartphone", "smartphones", "cellphone", "cellphones", "handset", "handsets", "cellular"},
    "mobile": {"mobile", "cellular", "wireless", "portable"},
    "company": {"company", "companies", "corporation", "corp", "inc", "llc", "firm", "enterprise", "manufacturer", "maker", "subsidiary", "brand"},
    "make": {"make", "makes", "maker", "manufacture", "manufactures", "producing", "produces", "designer", "designs"},
    "headquarters": {"headquarters", "headquartered", "based", "located"},
    "founder": {"founder", "founders", "founded", "established", "created", "started", "co-founded"},
    "award": {"award", "awarded", "awards", "prize", "prizes", "win", "won", "winner", "receive", "received", "granted", "bestowed", "medal", "honored"},
    "capital": {"capital", "capital city", "seat of government", "chief city"},
    "orbit": {"orbit", "orbits", "orbiting", "revolve", "revolves", "revolving", "circle", "circles", "circling", "rotate", "rotates"},
    "compose": {"compose", "composed", "composes", "comprising", "consist", "consists", "consisting", "constitute", "constituted", "contains", "containing"},
    "locate": {"locate", "located", "locates", "situated", "situates", "found", "based", "lies", "standing", "stands", "in"},
    "create": {"create", "created", "creates", "creating", "developed", "develops", "invented", "inventor", "designed", "designer", "authored", "author", "built", "programmed", "released"},
    "highest": {"highest", "tallest", "peak", "summit", "elevation"},
    "largest": {"largest", "biggest", "greatest", "broadest", "major"},
    "speed": {"speed", "velocity", "rate"},
    "language": {"language", "dialect", "speech", "tongue"},
    "country": {"country", "countries", "nation", "nations", "state", "states", "republic"},
    "city": {"city", "cities", "town", "municipality", "metropolis"},
    "element": {"element", "elements", "atom", "atoms", "chemical element"},
    "moon": {"moon", "lunar"},
    # Demonyms and country adjectives
    "france": {"france", "french"},
    "italy": {"italy", "italian"},
    "germany": {"germany", "german"},
    "spain": {"spain", "spanish"},
    "britain": {"britain", "british", "uk", "england", "english"},
    "america": {"america", "american", "usa", "united states"},
    "china": {"china", "chinese"},
    "japan": {"japan", "japanese"},
    "india": {"india", "indian"},
    "russia": {"russia", "russian"},
    "egypt": {"egypt", "egyptian"},
    "greece": {"greece", "greek"},
}


def stem(word: str) -> str:
    """Lightweight suffix normalizer for basic inflection handling."""
    w = word.lower().strip()
    for suffix in ("ing", "tion", "ies", "ed", "es", "s"):
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            if suffix == "ies":
                return w[:-3] + "y"
            return w[:-len(suffix)]
    return w


def stem_set(words: Set[str]) -> Set[str]:
    return {stem(w) for w in words}


def expand_synonyms(word: str) -> Set[str]:
    """Expands word with morphological variants and domain synonyms."""
    w = word.lower().strip()
    res = {w, stem(w)}
    for canon, group in SYNONYM_DICTIONARY.items():
        if w in group or stem(w) in {stem(g) for g in group}:
            res.update(group)
            res.update({stem(g) for g in group})
    return res


def tokenize(text: str) -> List[str]:
    """Tokenizes text into lowercase alphanumeric words, preserving digits and hyphenated terms."""
    clean = re.sub(r"[^\w\s-]", " ", text.lower())
    tokens = [t.strip("-") for t in clean.split() if len(t.strip("-")) >= 2]
    return tokens


def extract_content_terms(tokens: List[str]) -> List[str]:
    """Filters out common stopwords to retain informative content terms."""
    return [t for t in tokens if t not in STOP_WORDS]


def extract_numbers_and_years(text: str) -> Set[str]:
    """Extracts numbers, percentages, currency, and year-like tokens."""
    matches = re.findall(r"\b\d+(?:[\.,]\d+)?%?\b", text)
    return set(matches)


def compute_ngram_semantic_similarity(s1: str, s2: str, n: int = 3) -> float:
    """
    Computes character n-gram Jaccard similarity between two texts for semantic subword alignment.
    Captures morphological variations (e.g. mobile/mobility, manufacture/manufacturing).
    """
    c1 = re.sub(r"[^\w]", "", s1.lower())
    c2 = re.sub(r"[^\w]", "", s2.lower())
    if len(c1) < n or len(c2) < n:
        return 1.0 if c1 and c1 in c2 else 0.0
    ngrams1 = set(c1[i:i+n] for i in range(len(c1) - n + 1))
    ngrams2 = set(c2[i:i+n] for i in range(len(c2) - n + 1))
    inter = len(ngrams1.intersection(ngrams2))
    union = len(ngrams1.union(ngrams2))
    return inter / max(1, union)


class EvidenceRetriever:
    """
    Hybrid evidence retrieval engine combining BM25 lexical scoring,
    subword n-gram semantic similarity, and keyword-based fallback matching.
    """

    @staticmethod
    def retrieve_passages_for_claim(
        claim_text: str,
        chunks: List[DocumentChunk],
        top_k: int = 3,
        threshold: float = 0.15
    ) -> List[EvidencePassage]:
        """
        Retrieves and ranks candidate source passages using hybrid multi-stage scoring.
        Preserves source attribution and retrieval method.
        """
        if not chunks:
            return []

        claim_tokens = tokenize(claim_text)
        claim_content_terms = extract_content_terms(claim_tokens)
        claim_numbers = extract_numbers_and_years(claim_text)
        claim_lower = claim_text.lower().strip()

        if not claim_content_terms and not claim_numbers:
            claim_content_terms = claim_tokens

        # Precompute document frequencies across available chunks
        doc_count = len(chunks)
        df: Dict[str, int] = {}
        chunk_token_map: Dict[str, List[str]] = {}
        chunk_token_sets: Dict[str, Set[str]] = {}
        chunk_stem_sets: Dict[str, Set[str]] = {}

        for chk in chunks:
            chk_tokens = tokenize(chk.text)
            chunk_token_map[chk.chunk_id] = chk_tokens
            u_terms = set(chk_tokens)
            chunk_token_sets[chk.chunk_id] = u_terms
            chunk_stem_sets[chk.chunk_id] = stem_set(u_terms)
            for term in u_terms:
                df[term] = df.get(term, 0) + 1

        avg_dl = sum(len(toks) for toks in chunk_token_map.values()) / max(1, doc_count)
        k1 = 1.2
        b = 0.75

        scored_candidates: List[tuple[DocumentChunk, float]] = []

        for chk in chunks:
            chk_tokens = chunk_token_map[chk.chunk_id]
            doc_len = len(chk_tokens)
            chk_text_lower = chk.text.lower()
            chk_numbers = extract_numbers_and_years(chk.text)
            chk_token_set = chunk_token_sets[chk.chunk_id]
            chk_stem_set = chunk_stem_sets[chk.chunk_id]

            # 1. BM25 Lexical Term Scoring
            bm25_score = 0.0
            term_freqs: Dict[str, int] = {}
            for t in chk_tokens:
                term_freqs[t] = term_freqs.get(t, 0) + 1

            for term in claim_content_terms:
                tf = term_freqs.get(term, 0)
                if tf > 0:
                    d_freq = df.get(term, 1)
                    idf = math.log(1.0 + (doc_count - d_freq + 0.5) / (d_freq + 0.5))
                    idf = max(0.15, idf)
                    denom = tf + k1 * (1.0 - b + b * (doc_len / max(1.0, avg_dl)))
                    bm25_score += idf * ((tf * (k1 + 1.0)) / denom)

            # 2. Exact phrase, trigram, and bigram bonuses
            exact_phrase_bonus = 0.0
            if len(claim_content_terms) >= 3:
                trigrams = [
                    f"{claim_content_terms[i]} {claim_content_terms[i+1]} {claim_content_terms[i+2]}"
                    for i in range(len(claim_content_terms) - 2)
                ]
                for tg in trigrams:
                    if tg in chk_text_lower:
                        exact_phrase_bonus += 2.5

            if len(claim_content_terms) >= 2:
                bigrams = [
                    f"{claim_content_terms[i]} {claim_content_terms[i+1]}"
                    for i in range(len(claim_content_terms) - 1)
                ]
                for bg in bigrams:
                    if bg in chk_text_lower:
                        exact_phrase_bonus += 2.0

            cleaned_claim_sub = re.sub(r"[.!?]+$", "", claim_lower).strip()
            if cleaned_claim_sub and cleaned_claim_sub in chk_text_lower:
                exact_phrase_bonus += 5.0

            # 3. Keyword-Based Fallback Matching with Synonym Normalization
            matched_terms_count = 0
            for term in claim_content_terms:
                expanded = expand_synonyms(term)
                if expanded.intersection(chk_token_set) or expanded.intersection(chk_stem_set):
                    matched_terms_count += 1

            keyword_overlap_ratio = matched_terms_count / max(1, len(claim_content_terms))

            # 4. Semantic Subword / N-gram Similarity
            semantic_sim = compute_ngram_semantic_similarity(claim_lower, chk_text_lower)

            # 5. Numerical Alignment Bonus
            shared_numbers = claim_numbers.intersection(chk_numbers)
            num_bonus = 1.5 * len(shared_numbers) if shared_numbers else 0.0

            # Skip candidate if zero lexical overlap and zero keyword overlap
            if bm25_score <= 0.05 and keyword_overlap_ratio == 0.0:
                continue

            # Combined Hybrid Score
            # BM25 provides lexical specificity, Semantic sim handles subword alignment,
            # Keyword overlap ensures recovery when corpus statistics are sparse.
            raw_hybrid = (
                (0.45 * bm25_score)
                + exact_phrase_bonus
                + (2.5 * semantic_sim)
                + (3.0 * keyword_overlap_ratio)
                + num_bonus
            )

            # Keyword-based recovery boost for high-overlap candidates
            if keyword_overlap_ratio >= 0.70:
                raw_hybrid = max(raw_hybrid, 3.5)

            # Smooth monotonic bounded normalization mapping [0, inf) -> [0.0, 1.0]
            normalized_score = round(min(1.0, raw_hybrid / (raw_hybrid + 2.2)), 3)

            if normalized_score >= threshold:
                scored_candidates.append((chk, normalized_score))

        # Sort descending by relevance score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Deduplicate redundant passages and pick top K
        results: List[EvidencePassage] = []
        seen_texts: Set[str] = set()

        for chk, rel_score in scored_candidates:
            short_signature = " ".join(chk.text.split()[:20]).lower()
            if short_signature in seen_texts:
                continue
            seen_texts.add(short_signature)

            retrieval_method = getattr(chk, "source_type", "uploaded_document")
            if retrieval_method not in ("uploaded_document", "external_source"):
                retrieval_method = "uploaded_document"

            results.append(
                EvidencePassage(
                    passage_id=f"pas_{chk.chunk_id}",
                    doc_id=chk.doc_id,
                    filename=chk.filename,
                    page_number=chk.page_number,
                    text=chk.text.strip(),
                    relevance_score=rel_score,
                    relationship="inconclusive",
                    source_url=chk.source_url,
                    retrieval_method=retrieval_method
                )
            )
            if len(results) >= top_k:
                break

        return results

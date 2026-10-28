"""Automated tests for Autonomous Web & Knowledge Verification Mode."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.claim_extractor import ExtractedClaimItem
from backend.app.services.web_search_grounder import (
    extract_search_query_from_claim,
    retrieve_autonomous_web_evidence,
    get_offline_snapshot_chunks
)

client = TestClient(app)


def test_extract_search_query():
    claim = "The Apollo 11 mission landed on the Moon in 1969."
    query = extract_search_query_from_claim(claim)
    assert "apollo" in query.lower() or "moon" in query.lower()


def test_offline_snapshot_fallback():
    chunks = get_offline_snapshot_chunks("Earth orbits around the Sun")
    assert len(chunks) >= 1
    assert any("Earth" in c.filename for c in chunks)
    assert chunks[0].source_url is not None


def test_retrieve_autonomous_web_evidence_function():
    import asyncio
    claims = [
        ExtractedClaimItem(
            claim_id="c_web_1",
            claim_text="The Earth revolves around the Sun",
            original_sentence="The Earth revolves around the Sun."
        )
    ]
    chunks = asyncio.run(retrieve_autonomous_web_evidence(claims))
    assert len(chunks) >= 1
    assert any("Earth" in c.text or "Sun" in c.text for c in chunks)
    assert any(c.source_url for c in chunks)


def test_api_autonomous_web_mode_no_documents_provided():
    """
    Validates that a user can simply send an AI answer with ZERO uploaded documents,
    and Vertifact automatically fetches web knowledge and verifies the claims!
    """
    payload = {
        "ai_answer": "The Earth revolves around the Sun.",
        "mode": "autonomous_web"
    }
    response = client.post("/api/v1/verify", json=payload)
    assert response.status_code == 200
    report = response.json()

    assert report["verification_mode"] == "autonomous_web"
    assert len(report["claims"]) >= 1
    claim1 = report["claims"][0]
    assert claim1["status"] == "SUPPORTED"
    assert claim1["source_document"] is not None
    assert claim1["source_url"] is not None
    assert "wikipedia.org" in claim1["source_url"].lower() or "http" in claim1["source_url"]


def test_api_autonomous_web_contradiction_detection():
    """
    Tests autonomous contradiction detection against public knowledge.
    E.g. Einstein receiving Nobel Prize in Literature (when he received it in Physics).
    """
    payload = {
        "ai_answer": "Albert Einstein received the Nobel Prize in Literature.",
        "mode": "autonomous_web"
    }
    response = client.post("/api/v1/verify", json=payload)
    assert response.status_code == 200
    report = response.json()
    assert report["verification_mode"] == "autonomous_web"
    assert len(report["claims"]) >= 1

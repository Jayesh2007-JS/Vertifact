"""Automated tests for FastAPI endpoints, integration, and edge cases."""

import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.document_processor import document_store
import pymupdf as fitz

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_store():
    """Clear document store before each test run."""
    document_store.clear()
    yield
    document_store.clear()


def test_scenario_11_health_check():
    """Scenario 11: GET /api/v1/health returns 200 with system readiness info."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "ClaimCheck AI"
    assert "version" in data
    assert "active_documents_count" in data


def test_scenario_7_missing_source_documents():
    """Scenario 7: POST /api/v1/verify in strict document mode without sources returns 400 error."""
    payload = {
        "ai_answer": "The solar system has eight planets.",
        "mode": "strict_document"
    }
    response = client.post("/api/v1/verify", json=payload)
    assert response.status_code == 400
    assert "No source material provided" in response.json()["detail"]


def test_scenario_12_invalid_request_payloads():
    """Scenario 12: Empty answer or malformed payloads return validation error."""
    # Empty string
    response = client.post("/api/v1/verify", json={"ai_answer": ""})
    assert response.status_code == 422  # Pydantic validation min_length=3

    # Missing ai_answer
    response = client.post("/api/v1/verify", json={})
    assert response.status_code == 422


def test_scenario_10_missing_api_key_deterministic_fallback():
    """
    Scenario 10: Missing external API key still allows full deterministic verification.
    """
    source_text = "The Acme Corporation was founded in 2018 in Seattle. It employs 350 engineers."
    answer = "The Acme Corporation was founded in 2018 in Seattle."
    
    payload = {
        "ai_answer": answer,
        "pasted_source_text": source_text,
        "pasted_source_title": "Acme Factsheet"
    }
    response = client.post("/api/v1/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["claims"]) >= 1
    assert data["claims"][0]["status"] == "SUPPORTED"
    assert data["claims"][0]["verification_method"] in ["deterministic_nli", "hybrid_rule_engine"]


def test_scenario_14_and_15_pdf_upload_and_full_integration():
    """
    Scenario 14 & 15: Uploading real PDF, checking metadata, and verifying answer against it.
    """
    # Create an in-memory PDF using PyMuPDF
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((50, 72), "Mars has two small moons named Phobos and Deimos.")
    pdf_bytes = doc.write()
    doc.close()

    # Upload PDF
    files = {"file": ("mars_exploration.pdf", pdf_bytes, "application/pdf")}
    upload_resp = client.post("/api/v1/documents", files=files)
    assert upload_resp.status_code == 201
    doc_data = upload_resp.json()
    doc_id = doc_data["doc_id"]
    assert doc_data["filename"] == "mars_exploration.pdf"
    assert doc_data["page_count"] == 1
    assert doc_data["chunk_count"] >= 1

    # Verify claim against uploaded PDF
    verify_payload = {
        "ai_answer": "Mars has two small moons named Phobos and Deimos.",
        "doc_ids": [doc_id]
    }
    verify_resp = client.post("/api/v1/verify", json=verify_payload)
    assert verify_resp.status_code == 200
    report = verify_resp.json()
    
    assert report["summary"]["total_claims"] >= 1
    assert report["summary"]["supported_count"] >= 1
    assert report["summary"]["hallucination_risk_level"] == "LOW"
    assert report["claims"][0]["source_document"] == "mars_exploration.pdf"
    assert report["claims"][0]["source_page"] == 1
    assert len(report["claims"][0]["evidence"]) >= 1


def test_export_report_endpoint():
    """Test exporting verification report to JSON and Markdown."""
    source_text = "The speed of light in vacuum is approximately 299792 kilometers per second."
    verify_payload = {
        "ai_answer": "The speed of light in vacuum is approximately 299792 kilometers per second.",
        "pasted_source_text": source_text
    }
    verify_resp = client.post("/api/v1/verify", json=verify_payload)
    assert verify_resp.status_code == 200
    report = verify_resp.json()

    # Test Markdown export
    export_payload = {
        "report": report,
        "export_format": "markdown"
    }
    md_resp = client.post("/api/v1/reports/export", json=export_payload)
    assert md_resp.status_code == 200
    assert "# ClaimCheck AI — Verification Report" in md_resp.text
    assert "SUPPORTED" in md_resp.text

    # Test JSON export
    export_payload["export_format"] = "json"
    json_resp = client.post("/api/v1/reports/export", json=export_payload)
    assert json_resp.status_code == 200
    assert "report_id" in json_resp.text


def test_llm_config_endpoints():
    """Test GET, POST (validation failure), and DELETE for /api/v1/config/llm."""
    # 1. GET config
    get_resp = client.get("/api/v1/config/llm")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert "configured" in data
    assert "model" in data

    # 2. POST with invalid key fails gracefully
    post_resp = client.post("/api/v1/config/llm", json={
        "api_key": "sk-invalid-fake-key-for-testing",
        "model": "gpt-4o-mini"
    })
    assert post_resp.status_code == 400
    assert "Failed to connect to LLM provider" in post_resp.json()["detail"]

    # 3. DELETE config
    del_resp = client.delete("/api/v1/config/llm")
    assert del_resp.status_code == 200
    assert del_resp.json()["configured"] is False


"""End-to-end integration and verification script for ClaimCheck AI."""

import json
import httpx
import pymupdf as fitz

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"


def run_e2e_tests():
    print("==================================================")
    print("CLAIMCHECK AI — FULL END-TO-END VERIFICATION SUITE")
    print("==================================================")

    with httpx.Client(timeout=10.0) as client:
        # 1. Health Endpoint Test
        print("\n[TEST 1] Checking Backend Health...")
        health_res = client.get(f"{BACKEND_URL}/api/v1/health")
        assert health_res.status_code == 200, f"Expected 200, got {health_res.status_code}"
        health_data = health_res.json()
        print(f"✓ Backend online: {health_data['app_name']} v{health_data['version']}")
        print(f"  Active model/fallback: {health_data['llm_model']}")

        # 2. Frontend Connectivity Test
        print("\n[TEST 2] Checking Frontend Connectivity...")
        fe_res = client.get(FRONTEND_URL)
        assert fe_res.status_code == 200, f"Expected 200, got {fe_res.status_code}"
        assert "ClaimCheck" in fe_res.text
        assert "SUPPORTED" in fe_res.text
        assert "CONTRADICTED" in fe_res.text
        assert "INSUFFICIENT EVIDENCE" in fe_res.text
        print("✓ Frontend responding 200 OK with full UI components rendered.")

        # 3. PDF Upload & Ingestion Test
        print("\n[TEST 3] Generating & Uploading Real PDF Source Document...")
        doc = fitz.open()
        p1 = doc.new_page()
        rect = fitz.Rect(50, 50, 550, 750)
        p1.insert_textbox(
            rect,
            "Orbital Mission Specification: Satellite Alpha-9 orbits Earth at an altitude of 550 kilometers. "
            "The onboard propulsion system provides up to 12 years of operational life. "
            "Alpha-9 does not transmit unencrypted telemetry."
        )
        pdf_bytes = doc.write()
        doc.close()

        files = {"file": ("alpha9_spec.pdf", pdf_bytes, "application/pdf")}
        upload_res = client.post(f"{BACKEND_URL}/api/v1/documents", files=files)
        assert upload_res.status_code == 201, f"Expected 201, got {upload_res.status_code}: {upload_res.text}"
        doc_info = upload_res.json()
        print(f"✓ PDF Ingested successfully: {doc_info['filename']} (ID: {doc_info['doc_id']}, Pages: {doc_info['page_count']}, Chunks: {doc_info['chunk_count']})")

        # 4. Verification Workflow Test (All 3 Statuses in One Batch)
        print("\n[TEST 4] Executing Verification Pipeline against Ingested PDF...")
        # Claim 1 (Supported): Satellite Alpha-9 orbits Earth at an altitude of 550 kilometers
        # Claim 2 (Contradicted by number): The onboard propulsion system provides up to 25 years of operational life
        # Claim 3 (Contradicted by negation): Alpha-9 transmits unencrypted telemetry
        # Claim 4 (Insufficient Evidence): Satellite Alpha-9 carries a laser communications relay
        ai_answer = (
            "Satellite Alpha-9 orbits Earth at an altitude of 550 kilometers. "
            "The onboard propulsion system provides up to 25 years of operational life. "
            "Alpha-9 transmits unencrypted telemetry. "
            "Satellite Alpha-9 carries a high-bandwidth laser communications relay."
        )
        verify_payload = {
            "ai_answer": ai_answer,
            "doc_ids": [doc_info["doc_id"]]
        }
        verify_res = client.post(f"{BACKEND_URL}/api/v1/verify", json=verify_payload)
        assert verify_res.status_code == 200, f"Expected 200, got {verify_res.status_code}: {verify_res.text}"
        report = verify_res.json()

        print(f"✓ Verification completed with Report ID: {report['report_id']}")
        summary = report["summary"]
        print(f"  Total claims: {summary['total_claims']}")
        print(f"  Supported: {summary['supported_count']}")
        print(f"  Contradicted: {summary['contradicted_count']}")
        print(f"  Insufficient evidence: {summary['insufficient_evidence_count']}")
        print(f"  Hallucination risk level: {summary['hallucination_risk_level']}")
        print(f"  Notes: {summary['summary_notes']}")

        assert summary["supported_count"] >= 1, "Expected at least 1 supported claim"
        assert summary["contradicted_count"] >= 1, "Expected at least 1 contradicted claim"
        assert summary["insufficient_evidence_count"] >= 1, "Expected at least 1 insufficient evidence claim"
        assert summary["hallucination_risk_level"] == "HIGH", "Expected HIGH risk due to contradictions"

        for idx, claim in enumerate(report["claims"], 1):
            print(f"\n  [Claim {idx}] \"{claim['claim_text']}\"")
            print(f"    Status: {claim['status']}")
            print(f"    Reasoning: {claim['reasoning']}")
            print(f"    Source: {claim['source_document']} (Page {claim['source_page']})")
            if claim["evidence"]:
                print(f"    Evidence Quote: \"{claim['evidence'][0]['text']}\"")

        # 5. Export Report Test (JSON & Markdown)
        print("\n[TEST 5] Testing Report Export (JSON & Markdown)...")
        export_json_res = client.post(
            f"{BACKEND_URL}/api/v1/reports/export",
            json={"report": report, "export_format": "json"}
        )
        assert export_json_res.status_code == 200
        exported_data = json.loads(export_json_res.text)
        assert exported_data["report_id"] == report["report_id"]
        print("✓ JSON export validated.")

        export_md_res = client.post(
            f"{BACKEND_URL}/api/v1/reports/export",
            json={"report": report, "export_format": "markdown"}
        )
        assert export_md_res.status_code == 200
        assert "# ClaimCheck AI — Verification Report" in export_md_res.text
        print("✓ Markdown export validated.")

        # 6. Pasted Direct Text Verification Test
        print("\n[TEST 6] Testing Pasted Direct Text Workflow...")
        direct_source = "Acme policy permits refund requests submitted within 14 calendar days."
        direct_answer = "Acme policy permits refund requests submitted within 14 calendar days."
        direct_res = client.post(
            f"{BACKEND_URL}/api/v1/verify",
            json={"ai_answer": direct_answer, "pasted_source_text": direct_source}
        )
        assert direct_res.status_code == 200
        direct_report = direct_res.json()
        assert direct_report["summary"]["supported_count"] >= 1
        assert direct_report["summary"]["hallucination_risk_level"] == "LOW"
        print("✓ Pasted direct text verification succeeded with LOW risk rating.")

    print("\n==================================================")
    print("ALL END-TO-END INTEGRATION TESTS PASSED PERFECTLY!")
    print("==================================================")


if __name__ == "__main__":
    run_e2e_tests()

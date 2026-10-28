"""Report formatting and export service."""

import json
from backend.app.models.schemas import VerificationReport


def export_report_to_json(report: VerificationReport) -> str:
    """Exports structured report as indented, standard JSON."""
    return json.dumps(report.model_dump(), indent=2)


def export_report_to_markdown(report: VerificationReport) -> str:
    """Generates an executive, readable Markdown report."""
    md_lines = [
        f"# Vertifact — Verification Report",
        f"**Report ID:** `{report.report_id}`  ",
        f"**Generated at:** {report.timestamp}  ",
        f"**Verification Engine:** {report.verification_engine}  ",
        f"**Source Documents:** {', '.join(report.document_sources) or 'Pasted Text'}  ",
        "",
        "---",
        "",
        "## Executive Summary",
        f"- **Total Claims Evaluated:** {report.summary.total_claims}",
        f"- **Supported Claims:** {report.summary.supported_count} ({int(report.summary.support_ratio * 100)}%)",
        f"- **Contradicted Claims:** {report.summary.contradicted_count}",
        f"- **Insufficient Evidence Claims:** {report.summary.insufficient_evidence_count}",
        f"- **Overall Risk Level:** **{report.summary.hallucination_risk_level}**",
        f"- **Summary Assessment:** {report.summary.summary_notes}",
        "",
        "---",
        "",
        "## Evaluated AI Answer",
        f"> {report.original_answer}",
        "",
        "---",
        "",
        "## Detailed Claim Breakdown",
        ""
    ]

    for idx, claim in enumerate(report.claims, start=1):
        status_badge = f"**[{claim.status.value}]**"
        md_lines.append(f"### Claim {idx}: {status_badge}")
        md_lines.append(f"**Assertion:** \"{claim.claim_text}\"")
        md_lines.append(f"**Original Context:** *\"{claim.original_sentence}\"*")
        md_lines.append(f"**Reasoning:** {claim.reasoning}")
        md_lines.append(f"**Confidence Metric:** `{claim.confidence_metric}` ({int(claim.confidence_score * 100)}%)")
        
        if claim.evidence:
            md_lines.append("\n**Key Evidence Passages:**")
            for p_idx, ev in enumerate(claim.evidence, start=1):
                page_info = f", Page {ev.page_number}" if ev.page_number else ""
                url_info = f" | [Open Source]({ev.source_url})" if ev.source_url else ""
                md_lines.append(f"- *Passage {p_idx} ({ev.filename}{page_info}{url_info} | Rel: {ev.relevance_score:.2f} | Status: {ev.relationship}):*")
                md_lines.append(f"  > \"{ev.text}\"")
        else:
            md_lines.append("\n*No relevant source passages found.*")

        md_lines.append("\n" + ("-" * 30) + "\n")

    return "\n".join(md_lines)

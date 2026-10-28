"use client";

import React, { useState } from "react";
import { Download, Copy, Check, RotateCcw, FileText, Code2 } from "lucide-react";
import { VerificationReport } from "@/lib/types";
import { exportVerificationReport } from "@/lib/api";

interface ReportActionsProps {
  report: VerificationReport;
  onReset: () => void;
}

export const ReportActions: React.FC<ReportActionsProps> = ({ report, onReset }) => {
  const [copiedSummary, setCopiedSummary] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  const copySummaryText = () => {
    const text = [
      `=== VERIFACT VERIFICATION REPORT ===`,
      `Report ID: ${report.report_id}`,
      `Date: ${new Date(report.timestamp).toLocaleString()}`,
      `Overall Assessment: ${report.summary.summary_notes}`,
      `Risk Level: ${report.summary.hallucination_risk_level}`,
      `Total Claims: ${report.summary.total_claims}`,
      `Supported: ${report.summary.supported_count}`,
      `Contradicted: ${report.summary.contradicted_count}`,
      `Sources: ${report.document_sources.join(", ")}`,
      `====================================`,
    ].join("\n");

    navigator.clipboard.writeText(text);
    setCopiedSummary(true);
    setTimeout(() => setCopiedSummary(false), 2000);
  };

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportJson = async () => {
    try {
      setIsExporting(true);
      const jsonContent = await exportVerificationReport(report, "json");
      downloadFile(jsonContent, `verifact_report_${report.report_id}.json`, "application/json");
    } catch (e: any) {
      alert("Failed to export JSON report: " + e.message);
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportMarkdown = async () => {
    try {
      setIsExporting(true);
      const mdContent = await exportVerificationReport(report, "markdown");
      downloadFile(mdContent, `verifact_report_${report.report_id}.md`, "text/markdown");
    } catch (e: any) {
      alert("Failed to export Markdown report: " + e.message);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="rounded-xl border border-[#e6e4dc] bg-white p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-xs">
      <div className="flex items-center space-x-2">
        <button
          onClick={onReset}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-md border border-[#dedcd4] bg-[#f5f4ef] text-xs font-mono font-medium text-[#111215] hover:border-[#111215] transition cursor-pointer"
        >
          <RotateCcw className="h-3.5 w-3.5 text-[#787c85]" />
          <span>New Verification</span>
        </button>
        <button
          onClick={copySummaryText}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-md border border-[#dedcd4] bg-[#f5f4ef] text-xs font-mono font-medium text-[#111215] hover:border-[#111215] transition cursor-pointer"
        >
          {copiedSummary ? (
            <>
              <Check className="h-3.5 w-3.5 text-[#1a4d2e]" />
              <span className="text-[#1a4d2e]">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="h-3.5 w-3.5 text-[#787c85]" />
              <span>Copy Summary</span>
            </>
          )}
        </button>
      </div>

      <div className="flex items-center space-x-2">
        <button
          onClick={handleExportJson}
          disabled={isExporting}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-md border border-[#dedcd4] bg-white text-xs font-mono font-medium text-[#111215] hover:border-[#111215] transition cursor-pointer shadow-xs disabled:opacity-40"
        >
          <Code2 className="h-3.5 w-3.5 text-[#111215]" />
          <span>Export JSON</span>
        </button>
        <button
          onClick={handleExportMarkdown}
          disabled={isExporting}
          className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-md border border-[#dedcd4] bg-white text-xs font-mono font-medium text-[#111215] hover:border-[#111215] transition cursor-pointer shadow-xs disabled:opacity-40"
        >
          <FileText className="h-3.5 w-3.5 text-[#111215]" />
          <span>Export Markdown</span>
        </button>
      </div>
    </div>
  );
};

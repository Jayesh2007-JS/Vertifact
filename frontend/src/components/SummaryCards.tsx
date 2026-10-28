"use client";

import React from "react";
import { CheckCircle2, XCircle, Layers, ShieldCheck, AlertTriangle } from "lucide-react";
import { VerificationSummary } from "@/lib/types";

interface SummaryCardsProps {
  summary: VerificationSummary;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ summary }) => {
  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "LOW":
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold bg-[#f0f5f1] text-[#1a4d2e] border border-[#d2e3d5]">
            <ShieldCheck className="h-4 w-4" />
            <span>LOW RISK // HIGH FIDELITY</span>
          </span>
        );
      case "HIGH":
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold bg-[#fdf2f0] text-[#8b1e1e] border border-[#fad2cb]">
            <AlertTriangle className="h-4 w-4" />
            <span>HIGH RISK // CONFLICTS DETECTED</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-md text-xs font-mono font-bold bg-[#f5f4ef] text-[#111215] border border-[#dedcd4]">
            <ShieldCheck className="h-4 w-4" />
            <span>MODERATE RISK // AUDIT REQUIRED</span>
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* Risk Banner */}
      <div className="rounded-xl border border-[#e6e4dc] bg-white p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xs">
        <div className="space-y-1">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#787c85]">
            Executive Assessment
          </span>
          <h3 className="text-sm font-bold text-[#111215] tracking-tight">Factual Grounding Adjudication</h3>
          <p className="text-xs text-[#484b52] leading-relaxed max-w-2xl font-sans">{summary.summary_notes}</p>
        </div>
        <div className="shrink-0">{getRiskBadge(summary.hallucination_risk_level)}</div>
      </div>

      {/* Numerical Placards - Binary Verification Adjudication */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Total Claims */}
        <div className="rounded-xl border border-[#e6e4dc] bg-white p-5 flex items-center space-x-4 shadow-xs hover:border-[#111215] transition group">
          <div className="h-10 w-10 rounded-md bg-[#f5f4ef] border border-[#dedcd4] text-[#111215] flex items-center justify-center shrink-0">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-mono uppercase tracking-wider text-[#787c85]">Total Claims</p>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#111215] font-mono tracking-tight">{summary.total_claims}</p>
          </div>
        </div>

        {/* Supported */}
        <div className="rounded-xl border border-[#d2e3d5] bg-white p-5 flex items-center space-x-4 shadow-xs hover:border-[#1a4d2e] transition group">
          <div className="h-10 w-10 rounded-md bg-[#f0f5f1] border border-[#d2e3d5] text-[#1a4d2e] flex items-center justify-center shrink-0">
            <CheckCircle2 className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-mono uppercase tracking-wider text-[#1a4d2e]">Supported with Proof</p>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#1a4d2e] font-mono tracking-tight">{summary.supported_count}</p>
          </div>
        </div>

        {/* Contradicted */}
        <div className="rounded-xl border border-[#fad2cb] bg-white p-5 flex items-center space-x-4 shadow-xs hover:border-[#8b1e1e] transition group">
          <div className="h-10 w-10 rounded-md bg-[#fdf2f0] border border-[#fad2cb] text-[#8b1e1e] flex items-center justify-center shrink-0">
            <XCircle className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[11px] font-mono uppercase tracking-wider text-[#8b1e1e]">Contradicted with Proof</p>
            <p className="text-2xl sm:text-3xl font-extrabold text-[#8b1e1e] font-mono tracking-tight">{summary.contradicted_count}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

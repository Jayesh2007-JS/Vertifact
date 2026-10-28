"use client";

import React, { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  FileText,
  Globe,
  ExternalLink,
} from "lucide-react";
import { ClaimResult, EvidencePassage, VerificationStatus } from "@/lib/types";

interface ClaimListProps {
  claims: ClaimResult[];
  onSelectEvidenceForInspection?: (passage: EvidencePassage, claim: ClaimResult) => void;
}

export const ClaimList: React.FC<ClaimListProps> = ({
  claims,
  onSelectEvidenceForInspection,
}) => {
  const [filter, setFilter] = useState<"ALL" | VerificationStatus>("ALL");
  const [expandedClaimIds, setExpandedClaimIds] = useState<Set<string>>(
    new Set(claims.map((c) => c.claim_id))
  );
  const [copiedClaimId, setCopiedClaimId] = useState<string | null>(null);

  const toggleExpand = (claimId: string) => {
    setExpandedClaimIds((prev) => {
      const next = new Set(prev);
      if (next.has(claimId)) next.delete(claimId);
      else next.add(claimId);
      return next;
    });
  };

  const expandAll = () => {
    setExpandedClaimIds(new Set(claims.map((c) => c.claim_id)));
  };

  const collapseAll = () => {
    setExpandedClaimIds(new Set());
  };

  const copyClaimText = (claim: ClaimResult) => {
    const textToCopy = `Claim: ${claim.claim_text}\nStatus: ${claim.status}\nReasoning: ${claim.reasoning}\nSource: ${claim.source_document || "N/A"}${claim.source_page ? ` (Page ${claim.source_page})` : ""}`;
    navigator.clipboard.writeText(textToCopy);
    setCopiedClaimId(claim.claim_id);
    setTimeout(() => setCopiedClaimId(null), 2000);
  };

  const filteredClaims = claims.filter((c) => {
    if (filter === "ALL") return true;
    return c.status === filter;
  });

  const getStatusBadge = (status: VerificationStatus) => {
    switch (status) {
      case "SUPPORTED":
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#f0f5f1] text-[#1a4d2e] border border-[#d2e3d5]">
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>SUPPORTED</span>
          </span>
        );
      case "CONTRADICTED":
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#fdf2f0] text-[#8b1e1e] border border-[#fad2cb]">
            <XCircle className="h-3.5 w-3.5" />
            <span>CONTRADICTED</span>
          </span>
        );
    }
  };

  const getRetrievalMethodBadge = (method?: "uploaded_document" | "external_source" | "none") => {
    switch (method) {
      case "external_source":
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#f5f4ef] text-[#111215] border border-[#dedcd4]">
            <Globe className="h-3 w-3 text-[#111215]" />
            <span>Web Archive</span>
          </span>
        );
      case "uploaded_document":
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#f5f4ef] text-[#111215] border border-[#dedcd4]">
            <FileText className="h-3 w-3 text-[#111215]" />
            <span>Uploaded Doc</span>
          </span>
        );
      case "none":
      default:
        return (
          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[#f5f4ef] text-[#787c85] border border-[#dedcd4]">
            <span>No Reference</span>
          </span>
        );
    }
  };

  const getRelationshipBadge = (relationship: string) => {
    switch (relationship) {
      case "supports":
        return (
          <span className="text-[10px] font-mono font-semibold text-[#1a4d2e] bg-[#f0f5f1] border border-[#d2e3d5] px-2 py-0.5 rounded">
            Supports
          </span>
        );
      case "contradicts":
        return (
          <span className="text-[10px] font-mono font-semibold text-[#8b1e1e] bg-[#fdf2f0] border border-[#fad2cb] px-2 py-0.5 rounded">
            Contradicts
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-mono font-semibold text-[#787c85] bg-[#f5f4ef] border border-[#dedcd4] px-2 py-0.5 rounded">
            Inconclusive
          </span>
        );
    }
  };

  return (
    <div className="rounded-xl border border-[#e6e4dc] bg-white p-6 space-y-5 shadow-xs">
      {/* Header and Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-[#e6e4dc]">
        <div>
          <h2 className="text-base font-bold text-[#111215] tracking-tight flex items-center space-x-2">
            <span>Factual Propositions & Evidence Audit</span>
            <span className="font-mono text-[9px] uppercase px-1.5 py-0.5 bg-[#f5f4ef] text-[#484b52] rounded border border-[#dedcd4]">
              Findings
            </span>
          </h2>
          <p className="text-[11px] font-mono text-[#787c85]">
            Showing {filteredClaims.length} of {claims.length} claims cross-referenced
          </p>
        </div>

        <div className="flex items-center flex-wrap gap-2">
          {/* Status Filter Buttons */}
          <div className="flex items-center space-x-1 bg-[#f5f4ef] p-1 rounded-lg border border-[#e6e4dc] text-xs font-mono">
            <button
              onClick={() => setFilter("ALL")}
              className={`px-3 py-1.5 rounded-md transition-all cursor-pointer ${
                filter === "ALL" ? "bg-[#111215] text-white font-medium shadow-xs" : "text-[#484b52] hover:text-[#111215]"
              }`}
            >
              All ({claims.length})
            </button>
            <button
              onClick={() => setFilter("SUPPORTED")}
              className={`px-3 py-1.5 rounded-md transition-all cursor-pointer ${
                filter === "SUPPORTED" ? "bg-[#f0f5f1] text-[#1a4d2e] border border-[#d2e3d5] font-bold shadow-xs" : "text-[#484b52] hover:text-[#111215]"
              }`}
            >
              Supported ({claims.filter((c) => c.status === "SUPPORTED").length})
            </button>
            <button
              onClick={() => setFilter("CONTRADICTED")}
              className={`px-3 py-1.5 rounded-md transition-all cursor-pointer ${
                filter === "CONTRADICTED" ? "bg-[#fdf2f0] text-[#8b1e1e] border border-[#fad2cb] font-bold shadow-xs" : "text-[#484b52] hover:text-[#111215]"
              }`}
            >
              Contradicted ({claims.filter((c) => c.status === "CONTRADICTED").length})
            </button>
          </div>

          {/* Expand/Collapse Toggle */}
          <div className="flex items-center space-x-2 text-xs font-mono text-[#787c85] pl-1">
            <button
              onClick={expandAll}
              className="px-2 py-1 hover:text-[#111215] transition cursor-pointer"
            >
              Expand All
            </button>
            <span>•</span>
            <button
              onClick={collapseAll}
              className="px-2 py-1 hover:text-[#111215] transition cursor-pointer"
            >
              Collapse All
            </button>
          </div>
        </div>
      </div>

      {/* Claim Cards List */}
      <div className="space-y-3.5">
        {filteredClaims.length === 0 ? (
          <div className="p-10 text-center text-[#787c85] text-xs font-mono border border-dashed border-[#dedcd4] rounded-lg bg-[#faf9f5]">
            No claims match the selected filter.
          </div>
        ) : (
          filteredClaims.map((claim, idx) => {
            const isExpanded = expandedClaimIds.has(claim.claim_id);
            const isSupported = claim.status === "SUPPORTED";

            return (
              <div
                key={claim.claim_id}
                className={`rounded-xl border transition-all duration-200 overflow-hidden ${
                  isSupported
                    ? "border-[#d2e3d5] bg-[#fafcfb]"
                    : "border-[#fad2cb] bg-[#fdfbfa]"
                }`}
              >
                {/* Header Row */}
                <div
                  className="p-4 flex items-start justify-between gap-3 cursor-pointer select-none hover:bg-black/[0.015] transition"
                  onClick={() => toggleExpand(claim.claim_id)}
                >
                  <div className="flex items-start space-x-3.5 min-w-0">
                    <span className="font-mono text-xs font-bold text-[#787c85] mt-0.5">#{idx + 1}</span>
                    <div className="min-w-0 space-y-1.5">
                      <div className="flex items-center flex-wrap gap-2">
                        {getStatusBadge(claim.status)}
                        {getRetrievalMethodBadge(claim.retrieval_method)}
                        {claim.source_url ? (
                          <a
                            href={claim.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="inline-flex items-center space-x-1 text-[11px] font-mono text-[#111215] bg-white hover:bg-[#f5f4ef] border border-[#dedcd4] px-2 py-0.5 rounded transition"
                            title={`Open source: ${claim.source_url}`}
                          >
                            <Globe className="h-3 w-3 text-[#111215]" />
                            <span className="truncate max-w-[220px]">{claim.source_title || claim.source_document || "Source"}</span>
                            <ExternalLink className="h-2.5 w-2.5 text-[#787c85]" />
                          </a>
                        ) : claim.source_document ? (
                          <span className="inline-flex items-center space-x-1 text-[11px] font-mono text-[#484b52] bg-white px-2 py-0.5 rounded border border-[#dedcd4]">
                            <FileText className="h-3 w-3 text-[#787c85]" />
                            <span className="truncate max-w-[200px]">{claim.source_title || claim.source_document}</span>
                            {claim.source_page && <span>(Pg {claim.source_page})</span>}
                          </span>
                        ) : null}
                      </div>
                      <p className="text-sm font-semibold text-[#111215] tracking-tight leading-snug">
                        &ldquo;{claim.claim_text}&rdquo;
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-1.5 shrink-0 pt-0.5">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        copyClaimText(claim);
                      }}
                      title="Copy claim proof"
                      className="p-1.5 text-[#787c85] hover:text-[#111215] hover:bg-[#f5f4ef] rounded-md transition cursor-pointer"
                    >
                      {copiedClaimId === claim.claim_id ? (
                        <Check className="h-4 w-4 text-[#1a4d2e]" />
                      ) : (
                        <Copy className="h-4 w-4" />
                      )}
                    </button>
                    <button
                      type="button"
                      className="p-1.5 text-[#787c85] hover:text-[#111215] hover:bg-[#f5f4ef] rounded-md transition"
                    >
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Expanded Details Body */}
                {isExpanded && (
                  <div className="px-4 pb-5 pt-2 border-t border-[#e6e4dc] space-y-3.5 text-xs">
                    {/* Reasoning Section */}
                    <div>
                      <p className="font-mono text-[10px] uppercase font-bold text-[#787c85] tracking-wider mb-1">
                        Entailment Reasoning:
                      </p>
                      <p className="text-[#111215] bg-white p-3 rounded-lg border border-[#e6e4dc] leading-relaxed font-sans shadow-2xs">
                        {claim.reasoning}
                      </p>
                    </div>

                    {/* Original Sentence Context */}
                    <div>
                      <p className="font-mono text-[10px] uppercase font-bold text-[#787c85] tracking-wider mb-1">
                        Original Proposition in Input:
                      </p>
                      <p className="italic text-[#484b52] bg-[#f5f4ef] p-2.5 rounded-lg border border-[#e6e4dc] font-sans">
                        &ldquo;{claim.original_sentence}&rdquo;
                      </p>
                    </div>

                    {/* Source Overview Banner */}
                    {(claim.source_url || claim.source_title || claim.source_document) && (
                      <div className="bg-[#faf9f5] p-3 rounded-lg border border-[#e6e4dc] flex flex-wrap items-center justify-between gap-2 font-mono text-[11px]">
                        <div className="flex items-center space-x-2">
                          <span className="text-[#787c85]">Primary Archive:</span>
                          <span className="text-[#111215] font-bold">{claim.source_title || claim.source_document}</span>
                          {claim.source_page && <span className="text-[#787c85]">(Page {claim.source_page})</span>}
                        </div>
                        {claim.source_url && (
                          <a
                            href={claim.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 font-semibold text-[#111215] hover:underline transition-colors"
                          >
                            <span>Verify Archive Record</span>
                            <ExternalLink className="h-3 w-3" />
                          </a>
                        )}
                      </div>
                    )}

                    {/* Evidence Passages Accordion */}
                    <div className="space-y-2">
                      <p className="font-mono text-[10px] uppercase font-bold text-[#787c85] tracking-wider">
                        Corroborating Evidence ({claim.evidence.length} {claim.evidence.length === 1 ? "passage" : "passages"}):
                      </p>

                      {claim.evidence.length === 0 ? (
                        <p className="italic text-[#787c85] p-3 bg-white rounded-lg border border-[#e6e4dc] font-mono text-xs">
                          No relevant passages were found in available sources to corroborate or dispute this assertion.
                        </p>
                      ) : (
                        <div className="space-y-2.5">
                          {claim.evidence.map((passage, pIdx) => (
                            <div
                              key={passage.passage_id || pIdx}
                              className="bg-white p-3.5 rounded-lg border border-[#e6e4dc] space-y-2 shadow-2xs"
                            >
                              <div className="flex items-center justify-between text-[11px] font-mono text-[#787c85]">
                                <span className="font-medium flex items-center space-x-1.5 flex-wrap">
                                  {passage.retrieval_method === "external_source" ? (
                                    <Globe className="h-3.5 w-3.5 text-[#111215] shrink-0" />
                                  ) : (
                                    <FileText className="h-3.5 w-3.5 text-[#111215] shrink-0" />
                                  )}
                                  <span className="text-[#111215] font-bold">{passage.filename}</span>
                                  {passage.page_number && <span>(Page {passage.page_number})</span>}
                                </span>
                                <div className="flex items-center space-x-2 shrink-0">
                                  {getRelationshipBadge(passage.relationship)}
                                  <span className="text-[10px] text-[#787c85]">
                                    {(passage.relevance_score * 100).toFixed(0)}% Match
                                  </span>
                                </div>
                              </div>
                              <blockquote className="border-l-2 border-[#111215] bg-[#faf9f5] p-3 rounded-r-md text-[#111215] leading-relaxed font-sans text-xs">
                                &ldquo;{passage.text}&rdquo;
                              </blockquote>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

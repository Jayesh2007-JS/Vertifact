"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Zap,
  Search,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Loader2,
  ArrowRight,
  X,
  FileText,
  Copy,
  Check,
  Globe,
  CornerDownLeft
} from "lucide-react";
import { verifyClaims } from "@/lib/api";
import { VerificationReport, ClaimResult } from "@/lib/types";

interface OmniCheckWidgetProps {
  onTransferToWorkspace?: (claimText: string, report: VerificationReport) => void;
}

const DEMO_CHIPS = [
  {
    label: "Motorola Mobile",
    text: "Motorola is a mobile phone company.",
    type: "supported",
  },
  {
    label: "Eiffel Tower (Paris)",
    text: "The Eiffel Tower is located in Paris, France.",
    type: "supported",
  },
  {
    label: "Earth Revolves Sun",
    text: "The Earth revolves around the Sun.",
    type: "supported",
  },
  {
    label: "Fake: France Capital Rome",
    text: "The capital of France is Rome.",
    type: "contradicted",
  },
  {
    label: "Fake: Einstein Literature",
    text: "Albert Einstein received the Nobel Prize in Literature.",
    type: "contradicted",
  },
];

export const OmniCheckWidget: React.FC<OmniCheckWidgetProps> = ({
  onTransferToWorkspace,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [referenceText, setReferenceText] = useState("");
  const [showReferenceInput, setShowReferenceInput] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [report, setReport] = useState<VerificationReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      } else if (e.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      setTimeout(() => inputRef.current?.focus(), 80);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const handleVerify = async (textToVerify?: string) => {
    const targetQuery = (textToVerify !== undefined ? textToVerify : query).trim();
    if (!targetQuery || targetQuery.length < 3) {
      setError("Please enter a statement to verify.");
      return;
    }

    setError(null);
    setIsLoading(true);
    setReport(null);

    try {
      const mode = referenceText.trim() ? "document" : "autonomous_web";
      const res = await verifyClaims({
        ai_answer: targetQuery,
        mode,
        pasted_source_text: referenceText.trim() || undefined,
        pasted_source_title: referenceText.trim() ? "Inline Reference" : undefined,
      });
      setReport(res);
    } catch (err: any) {
      setError(err.message || "Verification failed. Check backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChipClick = (chipText: string) => {
    setQuery(chipText);
    handleVerify(chipText);
  };

  const handleCopyResult = (claim: ClaimResult) => {
    const textToCopy = `[${claim.status}] ${claim.claim_text}\nReasoning: ${claim.reasoning}\nSource: ${claim.source_title || claim.source_document || "Primary Source"}${claim.source_url ? ` (${claim.source_url})` : ""}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleTransfer = () => {
    if (report && onTransferToWorkspace) {
      onTransferToWorkspace(query, report);
      setIsOpen(false);
    }
  };

  return (
    <div className="relative inline-block" ref={containerRef}>
      {/* Swiss Upper Corner Pill */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className={`group flex items-center space-x-2 px-3 py-1.5 rounded-md border text-xs font-mono transition-all cursor-pointer ${
          isOpen
            ? "bg-[#111215] text-white border-[#111215] shadow-xs"
            : "bg-white text-[#111215] border-[#d8d6ce] hover:bg-[#f5f4ef] hover:border-[#111215]/30 shadow-xs"
        }`}
        title="Instant Omni-Check: Zero tab switching verification (Cmd+K)"
      >
        <Zap className="h-3 w-3" />
        <span className="font-semibold tracking-tight">Instant Omni-Check</span>
        <span className="hidden sm:inline-block text-[9px] uppercase font-bold tracking-widest px-1.5 py-0.2 bg-[#f0eee6] text-[#484b52] rounded border border-[#dedcd4]">
          USP
        </span>
        <kbd className="hidden lg:inline-flex items-center px-1.5 py-0.5 text-[9px] font-mono text-[#787c85] bg-[#f5f4ef] rounded border border-[#e6e4dc]">
          ⌘K
        </kbd>
      </button>

      {/* Popover Modal (Swiss Gallery Card) */}
      {isOpen && (
        <div className="absolute right-0 mt-2.5 w-[92vw] sm:w-[490px] bg-white rounded-xl border border-[#d8d6ce] shadow-[0_20px_50px_rgba(0,0,0,0.1)] p-5 z-50 animate-in fade-in duration-100 space-y-4">
          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-[#e6e4dc]">
            <div className="space-y-0.5">
              <div className="flex items-center space-x-2">
                <span className="font-bold text-xs sm:text-sm text-[#111215]">
                  Instant Omni-Check
                </span>
                <span className="font-mono text-[9px] uppercase px-1.5 py-0.2 rounded bg-[#f0f5f1] text-[#1a4d2e] border border-[#d2e3d5]">
                  Live
                </span>
              </div>
              <p className="text-[11px] text-[#787c85] font-sans">
                Verify factual statements in place without switching tabs
              </p>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="p-1 rounded text-[#787c85] hover:text-[#111215] hover:bg-[#f5f4ef] transition cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Omni Input Box */}
          <div className="space-y-2">
            <div className="relative flex items-center">
              <div className="absolute left-3 text-[#787c85] pointer-events-none">
                <Search className="h-4 w-4" />
              </div>
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !isLoading) {
                    handleVerify();
                  }
                }}
                placeholder="Enter any claim to audit..."
                className="w-full text-xs sm:text-sm pl-9 pr-24 py-2.5 rounded-lg bg-[#fbfbf9] border border-[#d8d6ce] text-[#111215] placeholder:text-[#a0a4ad] focus:outline-none focus:border-[#111215] focus:bg-white transition font-sans"
              />
              <div className="absolute right-1.5 flex items-center space-x-1">
                {query && (
                  <button
                    type="button"
                    onClick={() => {
                      setQuery("");
                      setReport(null);
                      inputRef.current?.focus();
                    }}
                    className="p-1 text-[#787c85] hover:text-[#111215] transition cursor-pointer"
                  >
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
                <button
                  type="button"
                  disabled={isLoading || !query.trim()}
                  onClick={() => handleVerify()}
                  className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-md bg-[#111215] text-white font-semibold text-xs hover:bg-[#282a30] disabled:opacity-40 transition cursor-pointer"
                >
                  {isLoading ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <>
                      <span>Check</span>
                      <CornerDownLeft className="h-3 w-3" />
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Optional Reference Toggle */}
            <div className="flex items-center justify-between text-[11px] font-mono text-[#787c85] px-0.5">
              <button
                type="button"
                onClick={() => setShowReferenceInput((prev) => !prev)}
                className="text-[#111215] hover:underline font-medium inline-flex items-center space-x-1 cursor-pointer"
              >
                <FileText className="h-3 w-3" />
                <span>{showReferenceInput ? "Hide reference snippet" : "+ Attach reference snippet"}</span>
              </button>
              <span className="flex items-center space-x-1">
                <Globe className="h-3 w-3 text-[#1a4d2e]" />
                <span>Auto-grounds via public records</span>
              </span>
            </div>

            {showReferenceInput && (
              <textarea
                rows={2}
                value={referenceText}
                onChange={(e) => setReferenceText(e.target.value)}
                placeholder="Paste reference text if grounding against a custom document snippet..."
                className="w-full text-xs p-2.5 rounded-lg bg-[#fbfbf9] border border-[#d8d6ce] text-[#111215] placeholder:text-[#a0a4ad] focus:outline-none focus:border-[#111215] font-sans"
              />
            )}
          </div>

          {/* Quick Demo Test Chips */}
          <div className="space-y-1.5 pt-0.5">
            <p className="text-[10px] font-mono font-bold text-[#787c85] uppercase tracking-wider">
              Instant Test Assertions:
            </p>
            <div className="flex flex-wrap gap-1.5">
              {DEMO_CHIPS.map((chip, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleChipClick(chip.text)}
                  className={`text-[11px] font-mono px-2 py-0.5 rounded border transition cursor-pointer ${
                    chip.type === "supported"
                      ? "bg-[#f0f5f1] text-[#1a4d2e] border-[#d2e3d5] hover:bg-[#e4efe6]"
                      : "bg-[#fdf2f0] text-[#8b1e1e] border-[#fad2cb] hover:bg-[#fae4e1]"
                  }`}
                >
                  {chip.label}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-lg bg-[#fdf2f0] border border-[#fad2cb] text-[#8b1e1e] text-xs font-mono">
              {error}
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="p-4 rounded-lg bg-[#fbfbf9] border border-[#e6e4dc] flex items-center justify-center space-x-2 text-xs font-mono text-[#484b52]">
              <Loader2 className="h-4 w-4 animate-spin text-[#111215]" />
              <span>Cross-referencing evidence passages...</span>
            </div>
          )}

          {/* Verification Results Card */}
          {report && !isLoading && (
            <div className="space-y-3 pt-2 border-t border-[#e6e4dc]">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="font-bold text-[#111215] uppercase tracking-wider">
                  Audit Findings
                </span>
                <span className="text-[10px] text-[#787c85] bg-[#f5f4ef] px-2 py-0.5 rounded border border-[#e6e4dc]">
                  {report.claims.length} claim(s)
                </span>
              </div>

              <div className="space-y-2.5 max-h-[260px] overflow-y-auto pr-1">
                {report.claims.map((claim) => {
                  const isSupported = claim.status === "SUPPORTED";
                  return (
                    <div
                      key={claim.claim_id}
                      className={`p-3.5 rounded-lg border text-xs space-y-2 ${
                        isSupported
                          ? "bg-[#fbfdfb] border-[#d2e3d5]"
                          : "bg-[#fdfbfb] border-[#fad2cb]"
                      }`}
                    >
                      {/* Verdict Header */}
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center space-x-1.5">
                          {isSupported ? (
                            <CheckCircle2 className="h-4 w-4 text-[#1a4d2e] shrink-0" />
                          ) : (
                            <XCircle className="h-4 w-4 text-[#8b1e1e] shrink-0" />
                          )}
                          <span
                            className={`font-mono font-bold px-2 py-0.5 rounded text-[10px] tracking-wider uppercase ${
                              isSupported
                                ? "bg-[#f0f5f1] text-[#1a4d2e] border border-[#d2e3d5]"
                                : "bg-[#fdf2f0] text-[#8b1e1e] border border-[#fad2cb]"
                            }`}
                          >
                            {claim.status}
                          </span>
                        </div>
                        <span className="text-[10px] font-mono text-[#787c85]">
                          {Math.round(claim.confidence_score * 100)}% ALIGNMENT
                        </span>
                      </div>

                      {/* Claim Text */}
                      <p className="font-semibold text-[#111215] leading-snug">
                        &ldquo;{claim.claim_text}&rdquo;
                      </p>

                      {/* Reasoning */}
                      <p className="text-[11px] text-[#484b52] leading-relaxed font-sans">
                        {claim.reasoning}
                      </p>

                      {/* Evidence Pullquote */}
                      {claim.evidence && claim.evidence.length > 0 && (
                        <div className="p-2.5 rounded bg-[#f7f6f2] border-l-2 border-[#111215] text-[11px] text-[#2b2d31] italic font-sans leading-relaxed">
                          &ldquo;{claim.evidence[0].text.length > 180 ? `${claim.evidence[0].text.slice(0, 180)}...` : claim.evidence[0].text}&rdquo;
                        </div>
                      )}

                      {/* Source Citation */}
                      <div className="flex items-center justify-between pt-1 border-t border-[#e6e4dc] text-[11px] font-mono">
                        <span className="text-[#787c85] truncate max-w-[260px]">
                          Source: <strong className="text-[#111215] font-medium">{claim.source_title || claim.source_document || "Primary Source"}</strong>
                        </span>
                        {claim.source_url && (
                          <a
                            href={claim.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#111215] hover:underline inline-flex items-center space-x-1 font-medium"
                          >
                            <span>Open Source</span>
                            <ExternalLink className="h-2.5 w-2.5" />
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Bottom Actions */}
              <div className="flex items-center justify-between pt-2 border-t border-[#e6e4dc]">
                <button
                  type="button"
                  onClick={() => report.claims[0] && handleCopyResult(report.claims[0])}
                  className="text-xs font-mono text-[#787c85] hover:text-[#111215] inline-flex items-center space-x-1 cursor-pointer"
                >
                  {copied ? (
                    <>
                      <Check className="h-3 w-3 text-[#1a4d2e]" />
                      <span className="text-[#1a4d2e]">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3 w-3" />
                      <span>Copy proof</span>
                    </>
                  )}
                </button>

                {onTransferToWorkspace && (
                  <button
                    type="button"
                    onClick={handleTransfer}
                    className="text-xs font-mono text-[#111215] hover:underline font-semibold inline-flex items-center space-x-1 cursor-pointer"
                  >
                    <span>Open in full workspace</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

"use client";

import React from "react";
import { MessageSquareText, Trash2, Sparkles } from "lucide-react";

interface AnswerEditorProps {
  answerText: string;
  onAnswerChange: (text: string) => void;
  onLoadPreset: (
    presetKey: "moon_landing" | "einstein_nobel" | "eiffel_rome" | "astronomy" | "policy" | "multi_mixed" | "offline"
  ) => void;
  mode: "autonomous_web" | "document";
  maxLength?: number;
}

export const AnswerEditor: React.FC<AnswerEditorProps> = ({
  answerText,
  onAnswerChange,
  onLoadPreset,
  mode,
  maxLength = 15000,
}) => {
  const wordCount = answerText.trim() ? answerText.trim().split(/\s+/).length : 0;
  const charCount = answerText.length;

  return (
    <div className="rounded-xl border border-[#e6e4dc] bg-white p-6 space-y-4 shadow-xs">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-[#e6e4dc]">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-md bg-[#111215] text-white flex items-center justify-center shrink-0 shadow-xs">
            <MessageSquareText className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-[#111215] tracking-tight">
                AI Statement to Audit
              </h2>
              <span className="font-mono text-[9px] uppercase font-semibold px-1.5 py-0.5 bg-[#f5f4ef] text-[#484b52] rounded border border-[#dedcd4]">
                Phase 02
              </span>
            </div>
            <p className="text-[11px] font-mono text-[#787c85]">
              Paste generated text, LLM outputs, or multi-claim factual propositions
            </p>
          </div>
        </div>
        {answerText && (
          <button
            onClick={() => onAnswerChange("")}
            className="text-xs font-mono text-[#787c85] hover:text-[#8b1e1e] flex items-center space-x-1.5 transition-colors cursor-pointer"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Clear</span>
          </button>
        )}
      </div>

      {/* Preset Quick Loader Buttons */}
      <div className="flex items-center flex-wrap gap-1.5 text-xs font-mono">
        <span className="text-[#787c85] flex items-center space-x-1 mr-1 text-[11px]">
          <Sparkles className="h-3 w-3 text-[#111215]" />
          <span>Test Suites:</span>
        </span>

        {mode === "autonomous_web" ? (
          <>
            <button
              type="button"
              onClick={() => onLoadPreset("moon_landing")}
              className="px-2.5 py-1 rounded-md bg-[#f5f4ef] text-[#111215] border border-[#dedcd4] hover:border-[#111215] transition-all cursor-pointer text-[11px]"
            >
              Moon Landing (Apollo 11)
            </button>
            <button
              type="button"
              onClick={() => onLoadPreset("einstein_nobel")}
              className="px-2.5 py-1 rounded-md bg-[#fdf2f0] text-[#8b1e1e] border border-[#fad2cb] hover:border-[#8b1e1e] transition-all cursor-pointer text-[11px]"
            >
              Einstein Literature (Hallucination)
            </button>
            <button
              type="button"
              onClick={() => onLoadPreset("eiffel_rome")}
              className="px-2.5 py-1 rounded-md bg-[#fdf2f0] text-[#8b1e1e] border border-[#fad2cb] hover:border-[#8b1e1e] transition-all cursor-pointer text-[11px]"
            >
              Eiffel Tower Rome (Hallucination)
            </button>
            <button
              type="button"
              onClick={() => onLoadPreset("astronomy")}
              className="px-2.5 py-1 rounded-md bg-[#f5f4ef] text-[#111215] border border-[#dedcd4] hover:border-[#111215] transition-all cursor-pointer text-[11px]"
            >
              Planetary Science
            </button>
          </>
        ) : (
          <>
            <button
              type="button"
              onClick={() => onLoadPreset("policy")}
              className="px-2.5 py-1 rounded-md bg-[#f5f4ef] text-[#111215] border border-[#dedcd4] hover:border-[#111215] transition-all cursor-pointer text-[11px]"
            >
              Policy Warranty (14 vs 30 days)
            </button>
            <button
              type="button"
              onClick={() => onLoadPreset("offline")}
              className="px-2.5 py-1 rounded-md bg-[#fdf2f0] text-[#8b1e1e] border border-[#fad2cb] hover:border-[#8b1e1e] transition-all cursor-pointer text-[11px]"
            >
              Feature Negation Conflict
            </button>
            <button
              type="button"
              onClick={() => onLoadPreset("multi_mixed")}
              className="px-2.5 py-1 rounded-md bg-[#f5f4ef] text-[#111215] border border-[#dedcd4] hover:border-[#111215] transition-all cursor-pointer text-[11px]"
            >
              Multi-Claim Assertion
            </button>
          </>
        )}
      </div>

      {/* Editor Box */}
      <div className="relative">
        <textarea
          rows={6}
          value={answerText}
          onChange={(e) => onAnswerChange(e.target.value.slice(0, maxLength))}
          placeholder="Paste AI response here to detect hallucinations, verify citations, and adjudicate contradictions..."
          className="w-full p-4 rounded-lg bg-white border border-[#dedcd4] text-[#111215] placeholder:text-[#9c9ea6] focus:outline-none focus:border-[#111215] focus:ring-1 focus:ring-[#111215] text-sm font-sans leading-relaxed transition"
        />
      </div>

      {/* Footer / Telemetry Bar */}
      <div className="flex items-center justify-between pt-1 text-[11px] font-mono text-[#787c85]">
        <div className="flex items-center space-x-2">
          <span>{wordCount} words</span>
          <span>•</span>
          <span>{charCount} / {maxLength.toLocaleString()} chars</span>
        </div>
        <span className="hidden sm:inline">
          Auto-decomposes into atomic verifiable propositions
        </span>
      </div>
    </div>
  );
};

"use client";

import React from "react";
import { CheckCheck, Loader2, AlertCircle, ShieldCheck } from "lucide-react";

interface VerificationControlsProps {
  onVerify: () => void;
  isVerifying: boolean;
  verifyingStage: string;
  disabled: boolean;
  errorMessage: string | null;
  onClearError: () => void;
}

export const VerificationControls: React.FC<VerificationControlsProps> = ({
  onVerify,
  isVerifying,
  verifyingStage,
  disabled,
  errorMessage,
  onClearError,
}) => {
  return (
    <div className="space-y-4">
      {errorMessage && (
        <div className="p-4 rounded-lg bg-[#fdf2f0] border border-[#fad2cb] text-[#8b1e1e] text-xs sm:text-sm font-mono flex items-start space-x-3 shadow-xs animate-in fade-in">
          <AlertCircle className="h-5 w-5 shrink-0 text-[#8b1e1e] mt-0.5" />
          <div className="flex-1 leading-relaxed">{errorMessage}</div>
          <button
            onClick={onClearError}
            className="text-[#8b1e1e] hover:text-black font-bold ml-2 cursor-pointer transition-colors"
          >
            ×
          </button>
        </div>
      )}

      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-5 rounded-xl border border-[#e6e4dc] shadow-xs">
        <div className="text-xs space-y-1">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-[#111215]" />
            <p className="font-bold text-[#111215] tracking-tight">Ready for Entailment Adjudication</p>
          </div>
          <p className="text-[#787c85] text-[11px] font-mono">
            Decomposes text into atomic claims, retrieves primary source passages, and evaluates contradictions.
          </p>
        </div>

        <button
          type="button"
          disabled={disabled || isVerifying}
          onClick={onVerify}
          className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-3.5 rounded-lg bg-[#111215] text-white font-semibold text-sm hover:bg-[#282a30] active:scale-98 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer shrink-0 shadow-xs"
        >
          {isVerifying ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-white" />
              <span className="font-mono text-xs">{verifyingStage || "Evaluating Entailment..."}</span>
            </>
          ) : (
            <>
              <CheckCheck className="h-4 w-4 text-white" />
              <span>Verify Claims Protocol</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

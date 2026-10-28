"use client";

import React from "react";
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  ArrowRight,
  Zap,
  Globe,
  Database,
  Cpu,
  Layers
} from "lucide-react";

interface LandingHeroProps {
  onStartVerifying: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onStartVerifying }) => {
  return (
    <section className="relative overflow-hidden border-b border-white/[0.08] py-20 px-4 sm:px-6 lg:px-8 bg-[#07090e]">
      {/* Ambient Radial Spotlight Glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[450px] bg-gradient-to-b from-indigo-600/15 via-purple-600/10 to-transparent blur-3xl pointer-events-none rounded-full" />
      <div className="absolute -top-32 -left-40 w-96 h-96 bg-cyan-500/10 blur-3xl pointer-events-none rounded-full" />
      <div className="absolute top-40 -right-40 w-96 h-96 bg-indigo-500/10 blur-3xl pointer-events-none rounded-full" />

      {/* Cyber Grid Background */}
      <div className="absolute inset-0 bg-grid-cyber radial-mask opacity-40 pointer-events-none" />

      <div className="relative max-w-5xl mx-auto text-center space-y-8">
        {/* Live Telemetry Pill */}
        <div className="inline-flex items-center space-x-2.5 px-4 py-1.5 rounded-full bg-white/[0.03] border border-white/10 text-slate-300 text-xs font-mono tracking-wider uppercase shadow-inner backdrop-blur-xl">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500" />
          </span>
          <span className="text-white font-semibold">VeriFact Protocol</span>
          <span className="text-slate-600">•</span>
          <span className="text-indigo-400">Zero-Hallucination AI Auditing</span>
        </div>

        {/* Hero Headline */}
        <div className="space-y-4">
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-[-0.03em] leading-[1.08]">
            Audit AI Answers With <br />
            <span className="bg-gradient-to-r from-white via-indigo-200 to-cyan-300 bg-clip-text text-transparent">
              Verified Ground-Truth Evidence.
            </span>
          </h1>

          <p className="max-w-2xl mx-auto text-sm sm:text-base text-slate-400 leading-relaxed font-sans">
            AI language models hallucinate plausible-sounding dates, inverted facts, and fabricated claims.
            VeriFact decomposes assertions into atomic propositions, cross-references primary records,
            and delivers definitive, proof-backed verdicts.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <button
            onClick={onStartVerifying}
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-8 py-3.5 rounded-xl bg-white text-slate-950 font-bold text-sm hover:bg-slate-200 active:scale-98 transition shadow-[0_0_25px_rgba(255,255,255,0.25)] cursor-pointer"
          >
            <span>Launch Verification Studio</span>
            <ArrowRight className="h-4 w-4" />
          </button>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 px-6 py-3.5 rounded-xl bg-white/[0.04] text-slate-300 hover:text-white hover:bg-white/[0.08] border border-white/10 font-mono text-xs transition cursor-pointer"
          >
            <Cpu className="h-4 w-4 text-indigo-400" />
            <span>View REST API Specs</span>
          </a>
        </div>

        {/* Awwwards Bento Grid */}
        <div className="pt-12 grid grid-cols-1 md:grid-cols-3 gap-5 text-left">
          {/* Card 1: Autonomous Web Grounding */}
          <div className="p-6 rounded-2xl bg-[#0c101d]/70 backdrop-blur-xl border border-white/[0.08] hover:border-indigo-500/40 transition duration-300 group space-y-3">
            <div className="h-10 w-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Globe className="h-5 w-5" />
            </div>
            <div>
              <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-indigo-400">
                01 // AUTONOMOUS MODE
              </span>
              <h3 className="text-base font-bold text-white mt-0.5">
                Zero-Upload Web Grounding
              </h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Verifies public facts autonomously across 45+ allowlisted primary domains—including official corporate investor sites, government archives, and open encyclopedias.
            </p>
          </div>

          {/* Card 2: Hybrid NLI Engine */}
          <div className="p-6 rounded-2xl bg-[#0c101d]/70 backdrop-blur-xl border border-white/[0.08] hover:border-cyan-500/40 transition duration-300 group space-y-3">
            <div className="h-10 w-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-cyan-400">
                02 // HYBRID RETRIEVAL
              </span>
              <h3 className="text-base font-bold text-white mt-0.5">
                BM25 + Semantic Alignment
              </h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Combines lexical BM25 retrieval, character n-gram matching, domain synonym expansion, and clause-level contrastive polarity parsing to eliminate false contradictions.
            </p>
          </div>

          {/* Card 3: Binary Adjudication with Proof */}
          <div className="p-6 rounded-2xl bg-[#0c101d]/70 backdrop-blur-xl border border-white/[0.08] hover:border-emerald-500/40 transition duration-300 group space-y-3">
            <div className="h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center group-hover:scale-110 transition-transform">
              <CheckCircle2 className="h-5 w-5" />
            </div>
            <div>
              <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-emerald-400">
                03 // DEFINITIVE OUTCOMES
              </span>
              <h3 className="text-base font-bold text-white mt-0.5">
                Binary Verdicts with Proof
              </h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every statement is definitively adjudicated as either <strong className="text-emerald-300">SUPPORTED</strong> or <strong className="text-rose-300">CONTRADICTED</strong> with traceable citations and verbatim source excerpts.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

"use client";

import React, { useState, useEffect, useRef } from "react";
import { Navbar } from "@/components/Navbar";
import { DocumentManager } from "@/components/DocumentManager";
import { AnswerEditor } from "@/components/AnswerEditor";
import { VerificationControls } from "@/components/VerificationControls";
import { SummaryCards } from "@/components/SummaryCards";
import { ClaimList } from "@/components/ClaimList";
import { ReportActions } from "@/components/ReportActions";
import { BackendHealth, DocumentInfo, VerificationReport } from "@/lib/types";
import {
  checkBackendHealth,
  fetchSessionDocuments,
  addPastedSourceDocument,
  verifyClaims,
} from "@/lib/api";

export default function Home() {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Verification mode: "autonomous_web" (zero upload required) vs "document" (custom PDF / text)
  const [sourceMode, setSourceMode] = useState<"autonomous_web" | "document">("autonomous_web");

  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [pastedTextInline, setPastedTextInline] = useState("");
  const [answerText, setAnswerText] = useState("");

  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyingStage, setVerifyingStage] = useState("");
  const [report, setReport] = useState<VerificationReport | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const workspaceRef = useRef<HTMLDivElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // Load backend health and session documents on mount
  useEffect(() => {
    let isMounted = true;
    async function init() {
      try {
        setHealthLoading(true);
        const h = await checkBackendHealth();
        if (isMounted) setHealth(h);
      } catch (err) {
        if (isMounted) setHealth(null);
      } finally {
        if (isMounted) setHealthLoading(false);
      }

      try {
        const docs = await fetchSessionDocuments();
        if (isMounted) setDocuments(docs);
      } catch {
        // Ignored on initial boot
      }
    }
    init();
    return () => {
      isMounted = false;
    };
  }, []);

  const scrollToWorkspace = () => {
    workspaceRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Preset loader
  const handleLoadPreset = async (
    presetKey: "moon_landing" | "einstein_nobel" | "eiffel_rome" | "astronomy" | "policy" | "multi_mixed" | "offline"
  ) => {
    setErrorMessage(null);
    setReport(null);

    // Autonomous Mode Presets (Zero upload needed)
    if (presetKey === "moon_landing") {
      setSourceMode("autonomous_web");
      setAnswerText(
        "The Apollo 11 spacecraft successfully landed on the Moon on July 20, 1969. American astronauts Neil Armstrong and Buzz Aldrin stepped onto the lunar surface."
      );
      scrollToWorkspace();
      return;
    }

    if (presetKey === "einstein_nobel") {
      setSourceMode("autonomous_web");
      setAnswerText(
        "Albert Einstein was awarded the Nobel Prize in Literature in 1921 for his poetry and writings."
      );
      scrollToWorkspace();
      return;
    }

    if (presetKey === "eiffel_rome") {
      setSourceMode("autonomous_web");
      setAnswerText(
        "The Eiffel Tower is a famous wrought-iron monument located in Rome, Italy."
      );
      scrollToWorkspace();
      return;
    }

    // Document Mode Presets (Auto-loads sample source doc into backend)
    let sampleSourceTitle = "";
    let sampleSourceText = "";
    let sampleAnswer = "";

    switch (presetKey) {
      case "astronomy":
        sampleSourceTitle = "Solar System Factsheet";
        sampleSourceText =
          "Scientific consensus confirms that the Earth revolves around the Sun annually at an average distance of approximately 149.6 million kilometers. Mars has two small moons named Phobos and Deimos. Jupiter is the largest planet in our solar system.";
        sampleAnswer =
          "The Earth revolves around the Sun. Furthermore, Mars has five large spherical moons.";
        break;

      case "policy":
        sampleSourceTitle = "Consumer Return Policy 2026";
        sampleSourceText =
          "Consumer Return Policy: All eligible products may be returned within 14 days of purchase for a standard refund. Original receipt and undamaged packaging are required.";
        sampleAnswer =
          "The return policy allows eligible returns within 30 days of purchase for a complete refund.";
        break;

      case "offline":
        sampleSourceTitle = "Product Capabilities Guide";
        sampleSourceText =
          "System Features: The application supports offline access, client-side encryption, and seamless local background synchronization when network re-establishes.";
        sampleAnswer =
          "The application does not support offline access.";
        break;

      case "multi_mixed":
        sampleSourceTitle = "Acme Corp Profile";
        sampleSourceText =
          "Acme Corporation was founded in 2010. The company offers a comprehensive 2-year warranty on all industrial machinery.";
        sampleAnswer =
          "Acme Corporation was founded in 2010, employs 500 engineers in Europe, and offers a comprehensive 2-year warranty.";
        break;
    }

    try {
      setSourceMode("document");
      const newDoc = await addPastedSourceDocument(sampleSourceText, sampleSourceTitle);
      setDocuments((prev) => [...prev.filter((d) => d.filename !== newDoc.filename), newDoc]);
      setAnswerText(sampleAnswer);
      scrollToWorkspace();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load sample preset.");
    }
  };

  const handleVerify = async () => {
    setErrorMessage(null);

    if (!answerText.trim() || answerText.trim().length < 5) {
      setErrorMessage("Please enter an AI-generated answer or statement to verify.");
      return;
    }

    let effectiveMode = sourceMode;
    if (sourceMode === "document" && documents.length === 0 && !pastedTextInline.trim()) {
      setErrorMessage("Custom Document Mode: Please upload a PDF document or paste trusted text into the reference box, or switch to Autonomous Web Mode.");
      return;
    }

    try {
      setIsVerifying(true);
      setVerifyingStage("Extracting atomic factual claims...");

      await new Promise((r) => setTimeout(r, 200));
      if (effectiveMode === "autonomous_web") {
        setVerifyingStage("Searching trusted official sources and web knowledge...");
      } else {
        setVerifyingStage("Retrieving relevant evidence passages...");
      }

      await new Promise((r) => setTimeout(r, 200));
      setVerifyingStage("Evaluating semantic grounding & contradictions...");

      const activeDocIds = documents.map((d) => d.doc_id);

      const res = await verifyClaims({
        ai_answer: answerText.trim(),
        mode: effectiveMode,
        doc_ids: effectiveMode === "document" && activeDocIds.length > 0 ? activeDocIds : undefined,
        pasted_source_text: effectiveMode === "document" && pastedTextInline.trim() ? pastedTextInline.trim() : undefined,
      });

      setReport(res);

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err: any) {
      setErrorMessage(err.message || "Verification failed. Please check backend logs.");
    } finally {
      setIsVerifying(false);
      setVerifyingStage("");
    }
  };

  const handleReset = () => {
    setAnswerText("");
    setReport(null);
    setErrorMessage(null);
    scrollToWorkspace();
  };

  const handleTransferOmniResult = (claimText: string, omniReport: VerificationReport) => {
    setAnswerText(claimText);
    setReport(omniReport);
    setTimeout(() => {
      resultsRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 150);
  };

  return (
    <div className="min-h-screen bg-[#fbfbf9] flex flex-col font-sans text-[#111215] selection:bg-[#111215] selection:text-white">
      <Navbar
        health={health}
        healthLoading={healthLoading}
        onTransferOmniResult={handleTransferOmniResult}
      />

      <main ref={workspaceRef} className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        {/* Editorial Instrument Header */}
        <div className="border-b border-[#e6e4dc] pb-6 space-y-2">
          <div className="flex items-center space-x-2">
            <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-[#787c85]">
              VeriFact Studio
            </span>
            <span className="h-1 w-1 rounded-full bg-[#dedcd4]" />
            <span className="font-mono text-[10px] uppercase text-[#787c85]">
              Protocol v2.4 // Multi-Pass Entailment Engine
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-[#111215]">
            Factual Verification Instrument
          </h1>
          <p className="text-sm text-[#484b52] font-sans max-w-3xl leading-relaxed">
            Deconstruct generated assertions into atomic propositions, cross-examine against ground-truth documentation, and detect hallucinations with verified primary source citations.
          </p>
        </div>

        {/* Dual Input Instrument Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          <DocumentManager
            mode={sourceMode}
            onModeChange={setSourceMode}
            documents={documents}
            onDocumentsChanged={setDocuments}
            pastedTextInline={pastedTextInline}
            onPastedTextInlineChange={setPastedTextInline}
          />

          <AnswerEditor
            answerText={answerText}
            onAnswerChange={setAnswerText}
            onLoadPreset={handleLoadPreset}
            mode={sourceMode}
          />
        </div>

        {/* Action Controls */}
        <VerificationControls
          onVerify={handleVerify}
          isVerifying={isVerifying}
          verifyingStage={verifyingStage}
          disabled={!answerText.trim() || isVerifying}
          errorMessage={errorMessage}
          onClearError={() => setErrorMessage(null)}
        />

        {/* Verification Results Dossier */}
        {report && (
          <div ref={resultsRef} className="space-y-6 pt-6 animate-in fade-in duration-500">
            <div className="flex items-center justify-between border-b border-[#e6e4dc] pb-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-[10px] font-bold uppercase tracking-widest text-[#111215]">
                    Audit Certificate
                  </span>
                  <span className="font-mono text-[10px] text-[#787c85]">
                    Ref: {report.report_id}
                  </span>
                </div>
                <h2 className="text-xl sm:text-2xl font-extrabold text-[#111215] tracking-tight mt-0.5">
                  Factual Audit Findings
                </h2>
                <p className="text-xs font-mono text-[#787c85] mt-1">
                  Mode: <strong className="text-[#111215] uppercase">{report.verification_mode || sourceMode}</strong> • Engine: {report.verification_engine} • Generated {new Date(report.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>

            <SummaryCards summary={report.summary} />

            <ClaimList claims={report.claims} />

            <ReportActions report={report} onReset={handleReset} />
          </div>
        )}
      </main>

      <footer className="mt-auto border-t border-[#e6e4dc] bg-[#faf9f5] py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-[#787c85] gap-3">
          <p>© 2026 VeriFact Protocol. Evidence-Grounded Factual Intelligence.</p>
          <p className="flex items-center space-x-2">
            <span>Engineered with Next.js, React, Tailwind, and FastAPI.</span>
          </p>
        </div>
      </footer>
    </div>
  );
}

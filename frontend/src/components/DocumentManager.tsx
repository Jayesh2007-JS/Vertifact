"use client";

import React, { useState, useRef } from "react";
import {
  Upload,
  FileText,
  FileUp,
  Trash2,
  AlertCircle,
  CheckCircle,
  Loader2,
  BookOpen,
  Plus,
  Globe,
  Sparkles,
  ExternalLink,
  ShieldCheck,
} from "lucide-react";
import { DocumentInfo } from "@/lib/types";
import { uploadPdfDocument, addPastedSourceDocument, removeDocument } from "@/lib/api";

interface DocumentManagerProps {
  mode: "autonomous_web" | "document";
  onModeChange: (mode: "autonomous_web" | "document") => void;
  documents: DocumentInfo[];
  onDocumentsChanged: (docs: DocumentInfo[]) => void;
  pastedTextInline: string;
  onPastedTextInlineChange: (text: string) => void;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({
  mode,
  onModeChange,
  documents,
  onDocumentsChanged,
  pastedTextInline,
  onPastedTextInlineChange,
}) => {
  const [activeTab, setActiveTab] = useState<"upload" | "paste">("paste");
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Paste text modal / input state
  const [pastedTitle, setPastedTitle] = useState("Internal Documentation");
  const [pastedContent, setPastedContent] = useState("");
  const [isSubmittingText, setIsSubmittingText] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const handleFile = async (file: File) => {
    setErrorMessage(null);
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setErrorMessage("Please upload a valid PDF document (.pdf).");
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      setErrorMessage("File exceeds 15 MB limit. Please choose a smaller document.");
      return;
    }

    try {
      setIsUploading(true);
      const newDoc = await uploadPdfDocument(file);
      onDocumentsChanged([...documents, newDoc]);
      onModeChange("document");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to process PDF document.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await removeDocument(docId);
      onDocumentsChanged(documents.filter((d) => d.doc_id !== docId));
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to remove document.");
    }
  };

  const handleAddPastedDocument = async () => {
    const textToSubmit = (pastedTextInline || pastedContent).trim();
    if (!textToSubmit || textToSubmit.length < 10) {
      setErrorMessage("Please enter at least 10 characters of trusted source text.");
      return;
    }

    try {
      setIsSubmittingText(true);
      setErrorMessage(null);
      const newDoc = await addPastedSourceDocument(textToSubmit, pastedTitle.trim() || "Pasted Source");
      onDocumentsChanged([...documents, newDoc]);
      onModeChange("document");
      setPastedContent("");
      onPastedTextInlineChange("");
      setActiveTab("upload");
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to ingest source text.");
    } finally {
      setIsSubmittingText(false);
    }
  };

  return (
    <div className="rounded-xl border border-[#e6e4dc] bg-white p-6 space-y-5 shadow-xs">
      {/* Header with Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#e6e4dc]">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-md bg-[#111215] text-white flex items-center justify-center shrink-0 shadow-xs">
            {mode === "autonomous_web" ? <Globe className="h-4 w-4" /> : <BookOpen className="h-4 w-4" />}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-sm font-bold text-[#111215] tracking-tight">
                Knowledge Reference
              </h2>
              <span className="font-mono text-[9px] uppercase font-semibold px-1.5 py-0.5 bg-[#f5f4ef] text-[#484b52] rounded border border-[#dedcd4]">
                Phase 01
              </span>
            </div>
            <p className="text-[11px] font-mono text-[#787c85]">
              Autonomous global retrieval or private custom documentation
            </p>
          </div>
        </div>

        {/* Mode Selector Pill Buttons */}
        <div className="flex items-center space-x-1 bg-[#f5f4ef] p-1 rounded-lg border border-[#e6e4dc] text-xs font-mono">
          <button
            type="button"
            onClick={() => onModeChange("autonomous_web")}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center space-x-1.5 cursor-pointer ${
              mode === "autonomous_web"
                ? "bg-[#111215] text-white font-medium shadow-xs"
                : "text-[#484b52] hover:text-[#111215]"
            }`}
          >
            <Globe className="h-3.5 w-3.5" />
            <span>Autonomous Web</span>
          </button>
          <button
            type="button"
            onClick={() => onModeChange("document")}
            className={`px-3 py-1.5 rounded-md transition-all flex items-center space-x-1.5 cursor-pointer ${
              mode === "document"
                ? "bg-[#111215] text-white font-medium shadow-xs"
                : "text-[#484b52] hover:text-[#111215]"
            }`}
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Custom Document</span>
          </button>
        </div>
      </div>

      {/* Autonomous Web Mode Display */}
      {mode === "autonomous_web" ? (
        <div className="p-5 rounded-lg bg-[#faf9f5] border border-[#e6e4dc] space-y-4">
          <div className="flex items-start space-x-3.5">
            <div className="h-9 w-9 rounded-md bg-white border border-[#dedcd4] text-[#111215] flex items-center justify-center shrink-0 shadow-xs">
              <Sparkles className="h-4 w-4" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <h3 className="text-xs sm:text-sm font-bold text-[#111215] tracking-tight">
                  Autonomous Web Verification Active
                </h3>
                <span className="font-mono text-[9px] uppercase font-semibold px-2 py-0.5 rounded bg-[#f0f5f1] text-[#1a4d2e] border border-[#d2e3d5]">
                  Zero Upload Required
                </span>
              </div>
              <p className="text-xs text-[#484b52] leading-relaxed font-sans">
                VeriFact autonomously extracts key entities, dates, and predicates from your statement, then retrieves primary source passages from verified encyclopedias and official corporate investor archives.
              </p>
            </div>
          </div>

          {/* Trusted Repositories Chips */}
          <div className="pt-3 border-t border-[#e6e4dc] flex flex-wrap items-center justify-between gap-2 text-xs">
            <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px] text-[#787c85]">
              <span>Curated Primary Sources:</span>
              <span className="px-2 py-0.5 rounded bg-white text-[#484b52] border border-[#dedcd4]">Wikipedia.org</span>
              <span className="px-2 py-0.5 rounded bg-white text-[#484b52] border border-[#dedcd4]">Motorola.in/com</span>
              <span className="px-2 py-0.5 rounded bg-white text-[#484b52] border border-[#dedcd4]">Academic & Govt Archives</span>
            </div>
            <button
              type="button"
              onClick={() => onModeChange("document")}
              className="text-[#111215] hover:underline font-mono text-xs cursor-pointer font-medium"
            >
              Upload private PDF instead →
            </button>
          </div>
        </div>
      ) : (
        /* Custom Document Mode */
        <div className="space-y-4">
          {/* Sub-tabs for Upload vs Paste */}
          <div className="flex space-x-1.5 bg-[#f5f4ef] p-1 rounded-lg border border-[#e6e4dc] font-mono text-xs">
            <button
              type="button"
              onClick={() => setActiveTab("paste")}
              className={`px-3 py-1.5 rounded-md transition-all cursor-pointer ${
                activeTab === "paste"
                  ? "bg-[#111215] text-white font-medium shadow-xs"
                  : "text-[#484b52] hover:text-[#111215]"
              }`}
            >
              Paste Reference Text
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("upload")}
              className={`px-3 py-1.5 rounded-md transition-all cursor-pointer ${
                activeTab === "upload"
                  ? "bg-[#111215] text-white font-medium shadow-xs"
                  : "text-[#484b52] hover:text-[#111215]"
              }`}
            >
              Upload PDF File
            </button>
          </div>

          {/* Error alert */}
          {errorMessage && (
            <div className="p-3.5 rounded-lg bg-[#fdf2f0] border border-[#fad2cb] text-[#8b1e1e] text-xs font-mono flex items-start space-x-2">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              <div className="flex-1">{errorMessage}</div>
              <button
                onClick={() => setErrorMessage(null)}
                className="hover:text-black font-bold ml-2 cursor-pointer"
              >
                ×
              </button>
            </div>
          )}

          {/* Paste Source Text Tab */}
          {activeTab === "paste" && (
            <div className="space-y-3">
              <div>
                <label className="block text-[11px] font-mono font-medium text-[#484b52] mb-1">
                  SOURCE TITLE / REFERENCE NAME
                </label>
                <input
                  type="text"
                  value={pastedTitle}
                  onChange={(e) => setPastedTitle(e.target.value)}
                  placeholder="e.g., Mission Spec 2026, Apollo-11 NASA Record"
                  className="w-full text-xs font-mono px-3.5 py-2.5 rounded-lg bg-white border border-[#dedcd4] text-[#111215] placeholder:text-[#9c9ea6] focus:outline-none focus:border-[#111215] focus:ring-1 focus:ring-[#111215] transition"
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono font-medium text-[#484b52] mb-1">
                  TRUSTED REFERENCE PASSAGES (GROUND TRUTH)
                </label>
                <textarea
                  rows={4}
                  value={pastedTextInline || pastedContent}
                  onChange={(e) => {
                    setPastedContent(e.target.value);
                    onPastedTextInlineChange(e.target.value);
                  }}
                  placeholder="Paste verified company documentation, contracts, or reference passages here..."
                  className="w-full text-xs font-sans p-3.5 rounded-lg bg-white border border-[#dedcd4] text-[#111215] placeholder:text-[#9c9ea6] focus:outline-none focus:border-[#111215] focus:ring-1 focus:ring-[#111215] transition leading-relaxed"
                />
              </div>
              <div className="flex justify-between items-center pt-1 font-mono text-xs">
                <span className="text-[#787c85]">
                  {(pastedTextInline || pastedContent).split(/\s+/).filter(Boolean).length} words parsed
                </span>
                <button
                  type="button"
                  disabled={isSubmittingText || !(pastedTextInline || pastedContent).trim()}
                  onClick={handleAddPastedDocument}
                  className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md bg-[#111215] text-white hover:bg-[#282a30] disabled:opacity-40 transition font-mono font-medium shadow-xs cursor-pointer"
                >
                  {isSubmittingText ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      <span>Indexing...</span>
                    </>
                  ) : (
                    <>
                      <Plus className="h-3.5 w-3.5" />
                      <span>Add to Session Documents</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          )}

          {/* PDF Upload Tab */}
          {activeTab === "upload" && (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition ${
                isDragging
                  ? "border-[#111215] bg-[#f5f4ef]"
                  : "border-[#dedcd4] hover:border-[#111215] bg-[#faf9f5]"
              }`}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                accept=".pdf"
                className="hidden"
              />

              {isUploading ? (
                <div className="flex flex-col items-center justify-center space-y-2">
                  <Loader2 className="h-7 w-7 text-[#111215] animate-spin" />
                  <p className="text-xs font-mono font-bold text-[#111215]">Extracting text & parsing pages...</p>
                  <p className="text-[11px] font-mono text-[#787c85]">Indexing passages into vector space</p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center space-y-2">
                  <div className="h-9 w-9 rounded-md bg-white border border-[#dedcd4] text-[#111215] flex items-center justify-center shadow-xs">
                    <FileUp className="h-4 w-4" />
                  </div>
                  <p className="text-xs font-semibold text-[#111215]">
                    Click to select PDF or drag and drop
                  </p>
                  <p className="text-[11px] font-mono text-[#787c85]">
                    PDF up to 15MB • Preserves page numbers & paragraph bounds
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Active Documents List */}
          {documents.length > 0 && (
            <div className="space-y-2 pt-2">
              <p className="text-[10px] font-mono font-bold text-[#787c85] uppercase tracking-wider">
                Session Grounding Documents ({documents.length})
              </p>
              <div className="divide-y divide-[#e6e4dc] rounded-lg border border-[#e6e4dc] bg-white overflow-hidden">
                {documents.map((doc) => (
                  <div
                    key={doc.doc_id}
                    className="p-3.5 flex items-center justify-between hover:bg-[#faf9f5] transition"
                  >
                    <div className="flex items-center space-x-3 min-w-0">
                      <div className="h-8 w-8 rounded-md bg-[#f5f4ef] border border-[#dedcd4] text-[#111215] flex items-center justify-center shrink-0">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs font-semibold text-[#111215] truncate" title={doc.filename}>
                          {doc.filename}
                        </p>
                        <p className="text-[10px] font-mono text-[#787c85]">
                          {doc.page_count} {doc.page_count === 1 ? "page" : "pages"} • {doc.chunk_count} passages • {formatFileSize(doc.file_size_bytes)}
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => handleDelete(doc.doc_id)}
                      title="Remove document"
                      className="p-1.5 text-[#787c85] hover:text-[#8b1e1e] rounded-md hover:bg-[#fdf2f0] transition cursor-pointer"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

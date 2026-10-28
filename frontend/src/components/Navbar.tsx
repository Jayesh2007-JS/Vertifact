"use client";

import React, { useState, useEffect } from "react";
import { ShieldCheck, ExternalLink, User, Zap } from "lucide-react";
import { BackendHealth, VerificationReport } from "@/lib/types";
import { OmniCheckWidget } from "@/components/OmniCheckWidget";
import { AuthModal } from "@/components/AuthModal";
import { supabase, isSupabaseConfigured, UserProfile } from "@/lib/supabase";

interface NavbarProps {
  health: BackendHealth | null;
  healthLoading: boolean;
  onTransferOmniResult?: (claimText: string, report: VerificationReport) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  health,
  healthLoading,
  onTransferOmniResult,
}) => {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [modalTab, setModalTab] = useState<"auth" | "pricing">("auth");
  const [user, setUser] = useState<any | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);

  useEffect(() => {
    if (!supabase) return;

    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-[#e6e4dc] bg-[#fbfbf9]/95 backdrop-blur-md transition-all">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center space-x-3 cursor-pointer">
            <div className="h-9 w-9 rounded-md bg-[#111215] text-white flex items-center justify-center shadow-xs">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-base tracking-tight text-[#111215]">
                  VeriFact
                </span>
                <span className="font-mono text-[10px] uppercase font-semibold px-1.5 py-0.2 bg-[#f0eee6] text-[#484b52] rounded border border-[#dedcd4]">
                  Protocol
                </span>
              </div>
              <p className="text-[11px] font-mono text-[#787c85] tracking-tight hidden sm:block">
                Evidence-Grounded AI Fact Verification
              </p>
            </div>
          </div>

          {/* Navigation & Widget */}
          <div className="flex items-center space-x-2.5 sm:space-x-3.5">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="hidden lg:inline-flex items-center space-x-1 text-xs font-mono text-[#787c85] hover:text-[#111215] transition-colors"
            >
              <span>API Docs</span>
              <ExternalLink className="h-3 w-3" />
            </a>

            {/* Pricing / Revenue Model Tier Button */}
            <button
              onClick={() => {
                setModalTab("pricing");
                setIsAuthModalOpen(true);
              }}
              className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg border border-[#dedcd4] bg-[#faf9f5] hover:border-[#111215] text-xs font-mono font-medium text-[#111215] transition cursor-pointer shadow-2xs"
            >
              <Zap className="h-3 w-3 text-[#111215]" />
              <span className="hidden sm:inline">Pricing & Tiers</span>
              <span className="sm:hidden">Plans</span>
            </button>

            {/* Account / Sign In Pill */}
            <button
              onClick={() => {
                setModalTab("auth");
                setIsAuthModalOpen(true);
              }}
              className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg border border-[#dedcd4] bg-white hover:border-[#111215] text-xs font-mono font-medium text-[#111215] transition cursor-pointer shadow-2xs"
            >
              <User className="h-3 w-3 text-[#787c85]" />
              <span>{user ? user.email?.split("@")[0] : "Sign In"}</span>
            </button>

            {/* Upper Corner Omni-Check Widget (Swiss Style) */}
            <OmniCheckWidget onTransferToWorkspace={onTransferOmniResult} />

            {/* Engine Status Indicator */}
            <div className="flex items-center space-x-2 pl-2 sm:pl-3 border-l border-[#e6e4dc]">
              {healthLoading ? (
                <span className="flex items-center space-x-1.5 text-[11px] font-mono text-[#787c85] bg-[#f5f4ef] px-2.5 py-1 rounded border border-[#e6e4dc]">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#787c85] animate-pulse" />
                  <span>CONNECTING</span>
                </span>
              ) : health && health.status === "healthy" ? (
                <span
                  title="Engine active: offline NLI and primary domain registry ready"
                  className="flex items-center space-x-1.5 text-[11px] font-mono font-medium text-[#1a4d2e] bg-[#f0f5f1] px-2.5 py-1 rounded border border-[#d2e3d5]"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-[#1a4d2e]" />
                  <span className="hidden sm:inline">ENGINE READY</span>
                  <span className="sm:hidden">READY</span>
                </span>
              ) : (
                <span className="flex items-center space-x-1.5 text-[11px] font-mono font-medium text-[#8b1e1e] bg-[#fdf2f0] px-2.5 py-1 rounded border border-[#fad2cb]">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#8b1e1e]" />
                  <span>OFFLINE</span>
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Auth & Subscription Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        user={user}
        profile={profile}
        initialTab={modalTab}
        onAuthSuccess={() => {
          if (supabase) {
            supabase.auth.getSession().then(({ data: { session } }) => {
              setUser(session?.user ?? null);
            });
          }
        }}
      />
    </>
  );
};

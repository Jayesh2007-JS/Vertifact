"use client";

import React, { useState } from "react";
import {
  X,
  ShieldCheck,
  Check,
  Zap,
  Lock,
  Mail,
  Loader2,
  Sparkles,
  Layers,
  ArrowRight,
  AlertCircle,
  KeyRound,
} from "lucide-react";
import {
  supabase,
  isSupabaseConfigured,
  TIER_LIMITS,
  UserProfile,
} from "@/lib/supabase";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: any | null;
  profile: UserProfile | null;
  onAuthSuccess?: () => void;
  initialTab?: "auth" | "pricing";
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  user,
  profile,
  onAuthSuccess,
  initialTab = "auth",
}) => {
  const [tab, setTab] = useState<"auth" | "pricing">(initialTab);
  const [authMode, setAuthMode] = useState<"signin" | "signup">("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!isSupabaseConfigured || !supabase) {
      setErrorMsg(
        "Supabase is not configured yet. Please provide your Supabase URL and Anon Key to activate authentication."
      );
      return;
    }

    if (!email || !password) {
      setErrorMsg("Please enter both email and password.");
      return;
    }

    try {
      setIsLoading(true);
      if (authMode === "signup") {
        const { error, data } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        setSuccessMsg(
          "Account created successfully! Check your email for verification link or sign in."
        );
      } else {
        const { error, data } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        setSuccessMsg("Welcome back! Successfully authenticated.");
        if (onAuthSuccess) onAuthSuccess();
        setTimeout(onClose, 800);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Authentication failed.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignOut = async () => {
    if (supabase) {
      await supabase.auth.signOut();
      if (onAuthSuccess) onAuthSuccess();
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="relative w-full max-w-2xl bg-white border border-[#e6e4dc] rounded-2xl shadow-xl overflow-hidden text-[#111215]">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-[#e6e4dc] bg-[#faf9f5]">
          <div className="flex items-center space-x-2.5">
            <div className="h-8 w-8 rounded-md bg-[#111215] text-white flex items-center justify-center shadow-xs">
              <ShieldCheck className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-sm tracking-tight text-[#111215]">
                  VeriFact Account & Tiers
                </span>
                <span className="font-mono text-[9px] uppercase px-1.5 py-0.2 bg-[#f0eee6] text-[#484b52] rounded border border-[#dedcd4]">
                  SaaS Model
                </span>
              </div>
              <p className="text-[11px] font-mono text-[#787c85]">
                Evidence-grounded subscription tiers & API credit controls
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setTab(tab === "auth" ? "pricing" : "auth")}
              className="text-xs font-mono font-medium text-[#111215] hover:underline px-2 py-1 rounded cursor-pointer"
            >
              {tab === "auth" ? "View Pricing Plans →" : "← Account Sign In"}
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#787c85] hover:text-[#111215] hover:bg-[#f5f4ef] transition cursor-pointer"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Informational Config Banner if Supabase keys not set yet */}
        {!isSupabaseConfigured && (
          <div className="p-3.5 bg-[#fdf2f0] border-b border-[#fad2cb] text-xs font-mono text-[#8b1e1e] flex items-start space-x-2.5">
            <KeyRound className="h-4 w-4 shrink-0 mt-0.5" />
            <div className="flex-1 leading-relaxed">
              <strong>Supabase Setup Pending:</strong> Add your{" "}
              <code>NEXT_PUBLIC_SUPABASE_URL</code> and{" "}
              <code>NEXT_PUBLIC_SUPABASE_ANON_KEY</code> in{" "}
              <code>frontend/.env.local</code> to activate live user signups and
              PostgreSQL credit meters.
            </div>
          </div>
        )}

        {/* Tab 1: Auth (Sign In / Sign Up) */}
        {tab === "auth" && (
          <div className="p-6 space-y-6">
            {user ? (
              /* Logged In State */
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-[#faf9f5] border border-[#e6e4dc] space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-mono uppercase text-[#787c85]">
                        Logged in as
                      </p>
                      <p className="text-sm font-bold text-[#111215]">
                        {user.email}
                      </p>
                    </div>
                    <span className="px-2.5 py-1 rounded text-xs font-mono font-bold bg-[#f0f5f1] text-[#1a4d2e] border border-[#d2e3d5] uppercase">
                      {profile?.subscription_tier || "Free"} Tier
                    </span>
                  </div>

                  {/* Usage Meter */}
                  <div className="space-y-1.5 pt-2 border-t border-[#e6e4dc]">
                    <div className="flex justify-between text-xs font-mono text-[#787c85]">
                      <span>Monthly Verification Quota</span>
                      <span>
                        {profile?.claims_used_this_month || 0} /{" "}
                        {profile?.monthly_claim_limit || 50} claims
                      </span>
                    </div>
                    <div className="w-full h-2 bg-[#e6e4dc] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-[#111215] transition-all"
                        style={{
                          width: `${Math.min(
                            100,
                            ((profile?.claims_used_this_month || 0) /
                              (profile?.monthly_claim_limit || 50)) *
                              100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-2">
                  <button
                    onClick={() => setTab("pricing")}
                    className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-[#111215] text-white text-xs font-mono font-medium hover:bg-[#282a30] transition cursor-pointer shadow-xs"
                  >
                    <Zap className="h-3.5 w-3.5" />
                    <span>Upgrade to Pro Plan</span>
                  </button>
                  <button
                    onClick={handleSignOut}
                    className="text-xs font-mono text-[#8b1e1e] hover:underline cursor-pointer"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            ) : (
              /* Form State */
              <form onSubmit={handleAuth} className="space-y-4">
                <div className="flex space-x-1 bg-[#f5f4ef] p-1 rounded-lg border border-[#e6e4dc] font-mono text-xs max-w-xs mx-auto">
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("signup");
                      setErrorMsg(null);
                    }}
                    className={`flex-1 py-1.5 rounded-md transition text-center cursor-pointer ${
                      authMode === "signup"
                        ? "bg-[#111215] text-white font-medium shadow-xs"
                        : "text-[#787c85] hover:text-[#111215]"
                    }`}
                  >
                    Create Account
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode("signin");
                      setErrorMsg(null);
                    }}
                    className={`flex-1 py-1.5 rounded-md transition text-center cursor-pointer ${
                      authMode === "signin"
                        ? "bg-[#111215] text-white font-medium shadow-xs"
                        : "text-[#787c85] hover:text-[#111215]"
                    }`}
                  >
                    Sign In
                  </button>
                </div>

                {errorMsg && (
                  <div className="p-3 rounded-lg bg-[#fdf2f0] border border-[#fad2cb] text-[#8b1e1e] text-xs font-mono flex items-start space-x-2">
                    <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                {successMsg && (
                  <div className="p-3 rounded-lg bg-[#f0f5f1] border border-[#d2e3d5] text-[#1a4d2e] text-xs font-mono flex items-start space-x-2">
                    <Check className="h-4 w-4 shrink-0 mt-0.5" />
                    <span>{successMsg}</span>
                  </div>
                )}

                <div className="space-y-3">
                  <div>
                    <label className="block text-[11px] font-mono font-medium text-[#484b52] mb-1">
                      WORK EMAIL
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-[#787c85]" />
                      <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="developer@company.com"
                        className="w-full text-xs font-mono pl-9 pr-3.5 py-2.5 rounded-lg bg-white border border-[#dedcd4] text-[#111215] placeholder:text-[#9c9ea6] focus:outline-none focus:border-[#111215] focus:ring-1 focus:ring-[#111215] transition"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[11px] font-mono font-medium text-[#484b52] mb-1">
                      PASSWORD
                    </label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-[#787c85]" />
                      <input
                        type="password"
                        required
                        minLength={6}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••••••"
                        className="w-full text-xs font-mono pl-9 pr-3.5 py-2.5 rounded-lg bg-white border border-[#dedcd4] text-[#111215] placeholder:text-[#9c9ea6] focus:outline-none focus:border-[#111215] focus:ring-1 focus:ring-[#111215] transition"
                      />
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full inline-flex items-center justify-center space-x-2 py-3 rounded-lg bg-[#111215] text-white text-xs font-mono font-medium hover:bg-[#282a30] transition cursor-pointer shadow-xs disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      <span>Authenticating...</span>
                    </>
                  ) : (
                    <span>
                      {authMode === "signup"
                        ? "Create Free Developer Account"
                        : "Sign In to VeriFact"}
                    </span>
                  )}
                </button>
              </form>
            )}
          </div>
        )}

        {/* Tab 2: Pricing & Revenue Model Matrix */}
        {tab === "pricing" && (
          <div className="p-6 space-y-5">
            <div className="text-center space-y-1">
              <h3 className="text-lg font-bold text-[#111215] tracking-tight">
                Predictable Usage-Grounded Pricing
              </h3>
              <p className="text-xs text-[#787c85] font-mono">
                B2B SaaS subscription tiers for developers, researchers, and enterprise pipelines
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5 pt-2">
              {/* Free Tier */}
              <div className="rounded-xl border border-[#e6e4dc] p-4 bg-[#faf9f5] space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] font-bold uppercase text-[#787c85]">
                      Starter
                    </span>
                    <span className="font-mono text-xs font-bold text-[#111215]">
                      $0
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-[#111215]">
                    Free Developer
                  </h4>
                  <ul className="space-y-1.5 text-[11px] text-[#484b52] font-sans">
                    {TIER_LIMITS.free.features.map((f, i) => (
                      <li key={i} className="flex items-start space-x-1.5">
                        <Check className="h-3.5 w-3.5 text-[#1a4d2e] shrink-0 mt-0.5" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <button
                  onClick={() => setTab("auth")}
                  className="w-full py-2 rounded-lg border border-[#dedcd4] bg-white text-xs font-mono font-medium text-[#111215] hover:border-[#111215] transition cursor-pointer"
                >
                  Current Tier
                </button>
              </div>

              {/* Pro Tier (Featured) */}
              <div className="rounded-xl border-2 border-[#111215] p-4 bg-white space-y-3 flex flex-col justify-between relative shadow-sm">
                <div className="absolute -top-2.5 right-3 bg-[#111215] text-white text-[9px] font-mono uppercase px-2 py-0.5 rounded font-bold">
                  Recommended
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] font-bold uppercase text-[#111215]">
                      Pro Studio
                    </span>
                    <span className="font-mono text-xs font-bold text-[#111215]">
                      $29 / mo
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-[#111215]">
                    Pro Researcher
                  </h4>
                  <ul className="space-y-1.5 text-[11px] text-[#484b52] font-sans">
                    {TIER_LIMITS.pro.features.map((f, i) => (
                      <li key={i} className="flex items-start space-x-1.5">
                        <Check className="h-3.5 w-3.5 text-[#1a4d2e] shrink-0 mt-0.5" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <button
                  onClick={() => {
                    alert(
                      "To connect Stripe or LemonSqueezy checkout, provide your billing webhook or keys!"
                    );
                  }}
                  className="w-full py-2 rounded-lg bg-[#111215] text-white text-xs font-mono font-bold hover:bg-[#282a30] transition cursor-pointer shadow-xs"
                >
                  Upgrade to Pro ($29)
                </button>
              </div>

              {/* Enterprise Tier */}
              <div className="rounded-xl border border-[#e6e4dc] p-4 bg-[#faf9f5] space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] font-bold uppercase text-[#787c85]">
                      Enterprise
                    </span>
                    <span className="font-mono text-xs font-bold text-[#111215]">
                      $299 / mo
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-[#111215]">
                    API & SLA Scale
                  </h4>
                  <ul className="space-y-1.5 text-[11px] text-[#484b52] font-sans">
                    {TIER_LIMITS.enterprise.features.map((f, i) => (
                      <li key={i} className="flex items-start space-x-1.5">
                        <Check className="h-3.5 w-3.5 text-[#1a4d2e] shrink-0 mt-0.5" />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <button
                  onClick={() => {
                    alert(
                      "Enterprise plans include custom contracts, dedicated clusters, and custom crawlers."
                    );
                  }}
                  className="w-full py-2 rounded-lg border border-[#dedcd4] bg-white text-xs font-mono font-medium text-[#111215] hover:border-[#111215] transition cursor-pointer"
                >
                  Contact Enterprise
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

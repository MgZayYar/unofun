"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

import { ApiError, apiPost, setToken, type TokenResponse } from "@/lib/api";

export function AuthCard({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const params = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const res = await apiPost<TokenResponse>(`/api/auth/${mode}`, { email, password });
      setToken(res.access_token);
      router.push(params.get("next") ?? "/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-6">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/3 left-1/2 h-[420px] w-[700px] -translate-x-1/2 rounded-full bg-violet-600/20 blur-[130px]" />
      </div>
      <div className="glass relative w-full max-w-md rounded-3xl p-10">
        <Link href="/" className="text-2xl font-extrabold tracking-tight">
          uno<span className="gradient-text">fun</span>
        </Link>
        <h1 className="mt-6 text-2xl font-bold">
          {mode === "register" ? "Create your account" : "Welcome back"}
        </h1>
        <p className="mt-2 text-sm text-white/55">
          {mode === "register"
            ? "30 free dubbing minutes. No credit card required."
            : "Log in to your dubbing studio."}
        </p>
        <form onSubmit={submit} className="mt-8 space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-white/60">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              className="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm outline-none placeholder:text-white/25 focus:border-violet-400/60"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-white/60">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
              className="h-12 w-full rounded-xl border border-white/10 bg-white/5 px-4 text-sm outline-none placeholder:text-white/25 focus:border-violet-400/60"
            />
          </div>
          {error && (
            <p role="alert" className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
              {error}
            </p>
          )}
          <button type="submit" disabled={busy} className="btn-primary h-12 w-full rounded-xl font-semibold">
            {busy ? "Please wait…" : mode === "register" ? "Start dubbing free" : "Log in"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-white/50">
          {mode === "register" ? (
            <>Already have an account? <Link href="/login" className="text-violet-300 hover:text-violet-200">Log in</Link></>
          ) : (
            <>New to unofun? <Link href="/register" className="text-violet-300 hover:text-violet-200">Create an account</Link></>
          )}
        </p>
      </div>
    </div>
  );
}

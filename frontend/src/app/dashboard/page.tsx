"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { DubStudio, JobList } from "@/components/dub-studio";
import { apiGet, getToken, setToken, type User } from "@/lib/api";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login?next=/dashboard");
      return;
    }
    apiGet<User>("/api/auth/me")
      .then(setUser)
      .catch(() => {
        setToken(null);
        router.replace("/login?next=/dashboard");
      });
  }, [router, refreshKey]);

  function logout() {
    setToken(null);
    router.replace("/");
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-white/50">Loading your studio…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-white/5 bg-ink/70 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Link href="/" className="text-xl font-extrabold tracking-tight">
            uno<span className="gradient-text">fun</span>
          </Link>
          <div className="flex items-center gap-3">
            <span className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-1.5 text-sm font-medium text-emerald-300">
              {user.credits_minutes} min left
            </span>
            <button onClick={logout} className="text-sm text-white/60 transition hover:text-white">
              Log out
            </button>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-6xl space-y-8 px-6 py-10">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Your <span className="gradient-text">dubbing studio</span>
          </h1>
          <p className="mt-2 text-white/55">Dub any video into 21 languages. Signed in as {user.email}.</p>
        </div>
        <DubStudio
          refreshKey={refreshKey}
          onJobStarted={() => {
            setRefreshKey((k) => k + 1);
            // refresh credits after the deduction lands
            setTimeout(() => apiGet<User>("/api/auth/me").then(setUser).catch(() => {}), 1500);
          }}
        />
        <div>
          <h2 className="mb-4 text-xl font-bold">My dubs</h2>
          <JobList refreshKey={refreshKey} />
        </div>
      </main>
    </div>
  );
}

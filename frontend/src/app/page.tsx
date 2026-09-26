"use client";

import Link from "next/link";
import { useState } from "react";

const LANGUAGES = [
  "Myanmar", "Thai", "Indonesian", "Vietnamese", "English", "Spanish",
  "French", "German", "Hindi", "Japanese", "Korean", "Chinese",
  "Arabic", "Portuguese", "Russian", "Malay", "Filipino", "Khmer",
  "Lao", "Bengali", "Tamil",
];

const FAQS = [
  {
    q: "What is unofun?",
    a: "unofun is an AI-powered video dubbing studio. Paste any video URL or upload a file and get a professional voice-over with synced subtitles in 20+ languages — in minutes.",
  },
  {
    q: "Is unofun free to use?",
    a: "Yes. Every new account gets 30 free dubbing minutes — no credit card required. When you run out, top up with a plan that fits your volume.",
  },
  {
    q: "Which languages are supported?",
    a: "21 languages at launch, with a focus on Southeast Asia: Myanmar, Thai, Indonesian, Vietnamese, Malay, Filipino, Khmer and Lao — plus English, Spanish, French, German, Hindi, Japanese, Korean, Chinese, Arabic, Portuguese, Russian, Bengali and Tamil.",
  },
  {
    q: "How does the dubbing work?",
    a: "Your video is transcribed with speech AI, the script is translated, natural voices are synthesized for each speaker, and the new audio is mixed over your original soundtrack — music and ambience preserved.",
  },
  {
    q: "Can I use unofun for TikTok and YouTube Shorts?",
    a: "Absolutely. Short-form creators dub once and publish everywhere — reach Myanmar, Thai, Indonesian and Vietnamese audiences without re-recording a thing.",
  },
];

function Nav() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-white/5 bg-ink/70 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link href="/" className="text-xl font-extrabold tracking-tight">
          uno<span className="gradient-text">fun</span>
        </Link>
        <nav className="hidden items-center gap-8 text-sm text-white/70 md:flex">
          <a href="#how" className="transition hover:text-white">How it works</a>
          <a href="#languages" className="transition hover:text-white">Languages</a>
          <a href="#pricing" className="transition hover:text-white">Pricing</a>
          <a href="#faq" className="transition hover:text-white">FAQ</a>
        </nav>
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-sm text-white/70 transition hover:text-white">
            Log in
          </Link>
          <Link href="/register" className="btn-primary rounded-full px-5 py-2 text-sm font-semibold">
            Start free
          </Link>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  const [url, setUrl] = useState("");
  return (
    <section className="relative overflow-hidden pt-36 pb-24">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 left-1/2 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-violet-600/25 blur-[140px]" />
        <div className="absolute top-40 -left-40 h-[400px] w-[400px] rounded-full bg-fuchsia-600/15 blur-[120px]" />
        <div className="absolute top-64 -right-40 h-[400px] w-[400px] rounded-full bg-cyan-500/15 blur-[120px]" />
      </div>
      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <p className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-medium text-white/80">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
          21 languages · AI voice-over studio
        </p>
        <h1 className="text-5xl font-extrabold leading-[1.05] tracking-tight md:text-7xl">
          Any video. <span className="gradient-text">Any language.</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-white/60">
          Paste a video link or upload a file. Get a natural voice-over in 20+
          languages with perfectly timed audio — in minutes, not days.
        </p>
        <form
          className="glass mx-auto mt-10 flex max-w-xl flex-col gap-2 rounded-2xl p-2 sm:flex-row"
          onSubmit={(e) => {
            e.preventDefault();
            window.location.href = `/register?next=/dashboard${url ? `&url=${encodeURIComponent(url)}` : ""}`;
          }}
        >
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste a video URL to try it…"
            className="h-12 flex-1 rounded-xl bg-transparent px-4 text-sm outline-none placeholder:text-white/30"
          />
          <button type="submit" className="btn-primary h-12 rounded-xl px-7 text-sm font-semibold">
            Dub it free
          </button>
        </form>
        <p className="mt-4 text-xs text-white/40">30 free minutes · No credit card required</p>
      </div>
    </section>
  );
}

function HowItWorks() {
  const steps = [
    { n: "01", title: "Drop in your video", text: "Paste any video URL or upload a file. We fetch it and get it ready in seconds." },
    { n: "02", title: "Pick a language & voice", text: "Choose from 21 languages and preview natural AI voices before you commit a single credit." },
    { n: "03", title: "Download your dub", text: "Speech is transcribed, translated, voiced and mixed over your original audio. Download the finished MP4." },
  ];
  return (
    <section id="how" className="mx-auto max-w-6xl px-6 py-24">
      <h2 className="text-center text-3xl font-bold tracking-tight md:text-4xl">
        Three steps. <span className="gradient-text">Any language.</span>
      </h2>
      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {steps.map((s) => (
          <div key={s.n} className="glass rounded-3xl p-8">
            <p className="gradient-text text-4xl font-extrabold">{s.n}</p>
            <h3 className="mt-4 text-lg font-semibold">{s.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-white/55">{s.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function Languages() {
  return (
    <section id="languages" className="border-y border-white/5 bg-white/[0.015] py-24">
      <div className="mx-auto max-w-6xl px-6">
        <h2 className="text-center text-3xl font-bold tracking-tight md:text-4xl">
          Reach <span className="gradient-text">every market</span>
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-center text-white/55">
          Built for creators going global — with deep coverage across Southeast Asia.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-3">
          {LANGUAGES.map((l) => (
            <span key={l} className="glass rounded-full px-5 py-2.5 text-sm text-white/80">
              {l}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: "Free",
      minutes: "30 minutes",
      features: ["30 free dubbing minutes", "All 21 languages", "Voice previews", "MP4 downloads"],
      cta: "Start free",
      highlight: false,
    },
    {
      name: "Creator",
      price: "$12",
      minutes: "300 minutes / mo",
      features: ["Everything in Starter", "Priority queue", "No watermark", "Commercial use"],
      cta: "Go Creator",
      highlight: true,
    },
    {
      name: "Studio",
      price: "$39",
      minutes: "1,200 minutes / mo",
      features: ["Everything in Creator", "Fastest queue", "Team seats (3)", "API access"],
      cta: "Go Studio",
      highlight: false,
    },
  ];
  return (
    <section id="pricing" className="mx-auto max-w-6xl px-6 py-24">
      <h2 className="text-center text-3xl font-bold tracking-tight md:text-4xl">
        Simple, <span className="gradient-text">global</span> pricing
      </h2>
      <p className="mt-4 text-center text-white/55">Pay for minutes. Cancel anytime.</p>
      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {plans.map((p) => (
          <div
            key={p.name}
            className={`rounded-3xl p-8 ${
              p.highlight
                ? "border border-fuchsia-500/40 bg-gradient-to-b from-fuchsia-500/10 to-transparent"
                : "glass"
            }`}
          >
            <h3 className="text-lg font-semibold">{p.name}</h3>
            <p className="mt-2 text-4xl font-extrabold">
              {p.price}
              {p.price !== "Free" && <span className="text-base font-normal text-white/50">/mo</span>}
            </p>
            <p className="mt-1 text-sm text-white/55">{p.minutes}</p>
            <ul className="mt-6 space-y-3 text-sm text-white/70">
              {p.features.map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <span className="text-emerald-400">✓</span> {f}
                </li>
              ))}
            </ul>
            <Link
              href="/register"
              className={`mt-8 block rounded-xl py-3 text-center text-sm font-semibold ${
                p.highlight ? "btn-primary" : "border border-white/15 transition hover:bg-white/5"
              }`}
            >
              {p.cta}
            </Link>
          </div>
        ))}
      </div>
    </section>
  );
}

function Faq() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section id="faq" className="mx-auto max-w-3xl px-6 py-24">
      <h2 className="text-center text-3xl font-bold tracking-tight md:text-4xl">
        Questions & <span className="gradient-text">answers</span>
      </h2>
      <div className="mt-10 space-y-3">
        {FAQS.map((f, i) => (
          <div key={f.q} className="glass overflow-hidden rounded-2xl">
            <button
              className="flex w-full items-center justify-between px-6 py-4 text-left font-medium"
              onClick={() => setOpen(open === i ? null : i)}
            >
              {f.q}
              <span className="text-white/40">{open === i ? "−" : "+"}</span>
            </button>
            {open === i && <p className="px-6 pb-5 text-sm leading-relaxed text-white/60">{f.a}</p>}
          </div>
        ))}
      </div>
    </section>
  );
}

export default function LandingPage() {
  return (
    <div>
      <Nav />
      <main>
        <Hero />
        <HowItWorks />
        <Languages />
        <Pricing />
        <Faq />
        <section className="mx-auto max-w-4xl px-6 pb-28 text-center">
          <div className="glass rounded-3xl px-8 py-14">
            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Go global <span className="gradient-text">without leaving your audience behind.</span>
            </h2>
            <Link href="/register" className="btn-primary mt-8 inline-block rounded-full px-10 py-3.5 font-semibold">
              Get started with unofun
            </Link>
          </div>
        </section>
      </main>
      <footer className="border-t border-white/5 py-10 text-center text-sm text-white/35">
        © 2026 unofun · AI video dubbing
      </footer>
    </div>
  );
}

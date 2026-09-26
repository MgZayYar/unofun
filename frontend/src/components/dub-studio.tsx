"use client";

import { useEffect, useRef, useState } from "react";

import {
  ApiError,
  apiGet,
  apiPost,
  apiUpload,
  stageLabel,
  type DubJob,
  type Language,
  type Video,
  type Voice,
} from "@/lib/api";

function formatDuration(sec: number | null): string {
  if (sec == null) return "—";
  const m = Math.floor(sec / 60);
  const s = Math.round(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function minutesFor(video: Video | null): number {
  if (!video) return 1;
  return Math.max(1, Math.ceil((video.duration_seconds ?? 60) / 60));
}

export function DubStudio({ onJobStarted, refreshKey }: { onJobStarted: () => void; refreshKey: number }) {
  const [tab, setTab] = useState<"url" | "upload">("url");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [video, setVideo] = useState<Video | null>(null);
  const [languages, setLanguages] = useState<Language[]>([]);
  const [language, setLanguage] = useState("my");
  const [voices, setVoices] = useState<Voice[]>([]);
  const [voice, setVoice] = useState<string | null>(null);
  const [previewing, setPreviewing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Language[]>("/api/dub/languages").then(setLanguages).catch(() => {});
    apiGet<Video[]>("/api/videos").then(setVideos).catch(() => {});
  }, [refreshKey]);

  useEffect(() => {
    const entry = languages.find((l) => l.code === language);
    if (entry) setVoice(entry.voices[0] ?? null);
    apiGet<Voice[]>(`/api/dub/voices?language=${language}`)
      .then((vs) => setVoices(vs))
      .catch(() => setVoices([]));
  }, [language, languages]);

  async function ingest(): Promise<Video | null> {
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      let v: Video;
      if (tab === "url") {
        if (!url.trim()) throw new ApiError(400, "Paste a video URL first.");
        v = await apiPost<Video>("/api/videos/from-url", { url: url.trim() });
        setNotice("Video fetched and ready.");
      } else {
        if (!file) throw new ApiError(400, "Choose a video file first.");
        v = await apiUpload<Video>("/api/videos/upload", file);
        setNotice("Upload complete.");
      }
      setVideos((prev) => [v, ...prev]);
      setVideo(v);
      return v;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load the video.");
      return null;
    } finally {
      setBusy(false);
    }
  }

  async function previewVoice() {
    if (!voice) return;
    setPreviewing(true);
    try {
      const res = await fetch("/api/dub/preview", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("unofun_token")}`,
        },
        body: JSON.stringify({ voice }),
      });
      if (!res.ok) throw new Error();
      const blob = await res.blob();
      const audio = new Audio(URL.createObjectURL(blob));
      await audio.play();
    } catch {
      setError("Voice preview failed. Try another voice.");
    } finally {
      setPreviewing(false);
    }
  }

  async function startDub() {
    const v = video ?? (await ingest());
    if (!v) return;
    setBusy(true);
    setError(null);
    try {
      await apiPost<DubJob>("/api/dub/start", {
        video_id: v.id,
        target_language: language,
        voice,
      });
      setNotice("Dubbing started — watch it below.");
      onJobStarted();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not start dubbing.");
    } finally {
      setBusy(false);
    }
  }

  const cost = minutesFor(video);

  return (
    <div className="glass rounded-3xl p-8">
      <h2 className="text-xl font-bold">New dub</h2>
      <p className="mt-1 text-sm text-white/50">Bring a video, pick a language, get it dubbed.</p>

      <div className="mt-6 flex gap-2 rounded-xl bg-white/5 p-1">
        {(["url", "upload"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-lg py-2.5 text-sm font-medium transition ${
              tab === t ? "bg-white/10 text-white" : "text-white/50 hover:text-white/80"
            }`}
          >
            {t === "url" ? "Paste URL" : "Upload file"}
          </button>
        ))}
      </div>

      <div className="mt-4">
        {tab === "url" ? (
          <div className="flex gap-2">
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://… (direct video link)"
              className="h-12 flex-1 rounded-xl border border-white/10 bg-white/5 px-4 text-sm outline-none placeholder:text-white/25 focus:border-violet-400/60"
            />
            <button onClick={() => void ingest()} disabled={busy} className="h-12 shrink-0 rounded-xl border border-white/15 px-5 text-sm font-medium transition hover:bg-white/5 disabled:opacity-50">
              {busy ? "…" : "Fetch"}
            </button>
          </div>
        ) : (
          <label className="flex h-24 cursor-pointer flex-col items-center justify-center gap-1 rounded-xl border border-dashed border-white/20 bg-white/[0.02] text-sm text-white/50 transition hover:border-violet-400/50 hover:text-white/80">
            <span className="text-2xl">⭳</span>
            {file ? file.name : "Drop a video file or click to browse"}
            <input
              type="file"
              accept="video/*"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
        )}
      </div>

      {videos.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-white/40">Your videos</p>
          <div className="flex flex-wrap gap-2">
            {videos.slice(0, 6).map((v) => (
              <button
                key={v.id}
                onClick={() => setVideo(v)}
                className={`rounded-full px-4 py-2 text-xs transition ${
                  video?.id === v.id
                    ? "bg-violet-500/30 text-white ring-1 ring-violet-400/50"
                    : "bg-white/5 text-white/60 hover:bg-white/10"
                }`}
              >
                {v.title.length > 28 ? v.title.slice(0, 28) + "…" : v.title} · {formatDuration(v.duration_seconds)}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-white/40">
            Target language
          </label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="h-12 w-full rounded-xl border border-white/10 bg-[#14141d] px-4 text-sm outline-none focus:border-violet-400/60"
          >
            {languages.map((l) => (
              <option key={l.code} value={l.code}>{l.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-white/40">
            Voice
          </label>
          <div className="flex gap-2">
            <select
              value={voice ?? ""}
              onChange={(e) => setVoice(e.target.value || null)}
              className="h-12 flex-1 rounded-xl border border-white/10 bg-[#14141d] px-4 text-sm outline-none focus:border-violet-400/60"
            >
              {voices.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name} {v.gender ? `(${v.gender})` : ""}
                </option>
              ))}
            </select>
            <button
              onClick={() => void previewVoice()}
              disabled={previewing || !voice}
              title="Preview voice"
              className="h-12 w-12 shrink-0 rounded-xl border border-white/15 text-lg transition hover:bg-white/5 disabled:opacity-50"
            >
              {previewing ? "…" : "▶"}
            </button>
          </div>
        </div>
      </div>

      {notice && <p className="mt-4 text-sm text-emerald-300">{notice}</p>}
      {error && (
        <p role="alert" className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          {error}
        </p>
      )}

      <button
        onClick={() => void startDub()}
        disabled={busy}
        className="btn-primary mt-6 h-13 w-full rounded-xl py-3.5 font-semibold disabled:opacity-50"
      >
        {busy ? "Working…" : `Dub it — ${cost} minute${cost === 1 ? "" : "s"} of credit`}
      </button>
      {!video && (
        <p className="mt-2 text-center text-xs text-white/35">
          Your video will be fetched first, then dubbing starts automatically.
        </p>
      )}
    </div>
  );
}

export function JobList({ refreshKey }: { refreshKey: number }) {
  const [jobs, setJobs] = useState<DubJob[]>([]);
  const [cancelling, setCancelling] = useState<number | null>(null);
  const jobsRef = useRef(jobs);
  jobsRef.current = jobs;

  async function load() {
    try {
      setJobs(await apiGet<DubJob[]>("/api/dub/jobs"));
    } catch {
      /* stay on previous list */
    }
  }

  useEffect(() => {
    void load();
    const timer = setInterval(() => {
      // Only poll while a job is still running.
      const active = jobsRef.current.some((j) => j.status === "queued" || j.status === "processing");
      if (active) void load();
    }, 2500);
    return () => clearInterval(timer);
  }, [refreshKey]);

  async function cancel(id: number) {
    setCancelling(id);
    try {
      await apiPost(`/api/dub/jobs/${id}/cancel`);
      await load();
    } catch {
      /* ignore */
    } finally {
      setCancelling(null);
    }
  }

  if (jobs.length === 0) {
    return (
      <div className="glass rounded-3xl p-10 text-center">
        <p className="text-4xl">🎙️</p>
        <h3 className="mt-4 font-semibold">No dubs yet</h3>
        <p className="mt-1 text-sm text-white/50">Your dubbed videos will appear here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {jobs.map((job) => {
        const running = job.status === "queued" || job.status === "processing";
        return (
          <div key={job.id} className="glass rounded-3xl p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-semibold">
                  Dub #{job.id} <span className="text-white/40">→</span>{" "}
                  <span className="gradient-text">{job.target_language}</span>
                </p>
                <p className="mt-0.5 text-xs text-white/45" aria-live="polite">
                  {stageLabel(job.status === "processing" ? job.stage : job.status)}
                  {running && ` · ${job.progress}%`}
                </p>
              </div>
              <div className="flex items-center gap-2">
                {job.status === "completed" && (
                  <a
                    href={`/api/dub/jobs/${job.id}/download`}
                    className="btn-primary rounded-xl px-5 py-2.5 text-sm font-semibold"
                  >
                    Download MP4
                  </a>
                )}
                {running && (
                  <button
                    onClick={() => void cancel(job.id)}
                    disabled={cancelling === job.id}
                    className="rounded-xl border border-white/15 px-4 py-2.5 text-sm text-white/70 transition hover:bg-white/5 disabled:opacity-50"
                  >
                    {cancelling === job.id ? "…" : "Cancel"}
                  </button>
                )}
                {job.status === "failed" && <span className="text-sm text-red-300">Failed</span>}
              </div>
            </div>
            {running && (
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-cyan-400 transition-all duration-500"
                  style={{ width: `${job.progress}%` }}
                />
              </div>
            )}
            {job.status === "failed" && job.error_message && (
              <p role="alert" className="mt-3 text-sm text-red-300">{job.error_message}</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

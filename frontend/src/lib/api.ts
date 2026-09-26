"use client";

/** Typed API client with JWT stored in localStorage. */

const TOKEN_KEY = "unofun_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (init.body && typeof init.body === "string") headers["Content-Type"] = "application/json";
  const res = await fetch(path, { ...init, headers });
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  let data: unknown = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? String((data as Record<string, unknown>).detail)
        : `Request failed (${res.status})`;
    throw new ApiError(res.status, detail);
  }
  return data as T;
}

export const apiGet = <T>(path: string): Promise<T> => request<T>(path);
export const apiPost = <T>(path: string, body?: unknown): Promise<T> =>
  request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) });
export const apiDelete = (path: string): Promise<void> => request<void>(path, { method: "DELETE" });

export async function apiUpload<T>(path: string, file: File): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  const headers: Record<string, string> = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(path, { method: "POST", headers, body: form });
  if (!res.ok) {
    const data = await res.json().catch(() => null);
    const detail =
      data && typeof data === "object" && "detail" in data ? String(data.detail) : `Upload failed (${res.status})`;
    throw new ApiError(res.status, detail);
  }
  return (await res.json()) as T;
}

/* ---------- domain types ---------- */

export type User = { id: number; email: string; credits_minutes: number; created_at: string };
export type TokenResponse = { access_token: string; token_type: string; user: User };
export type Video = { id: number; title: string; source_url: string | null; duration_seconds: number | null; created_at: string };
export type Language = { code: string; name: string; voices: string[] };
export type Voice = { id: string; name: string; language: string; gender: string };
export type DubJob = {
  id: number;
  video_id: number;
  target_language: string;
  voice: string | null;
  status: "queued" | "processing" | "completed" | "failed" | "cancelled";
  stage: string;
  progress: number;
  error_message: string | null;
  minutes_charged: number;
  created_at: string;
  finished_at: string | null;
};

export const STAGE_LABELS: Record<string, string> = {
  queued: "Waiting in queue",
  starting: "Starting",
  transcribing: "Transcribing speech",
  translating: "Translating script",
  synthesizing: "Synthesizing voices",
  mixing: "Mixing dubbed audio",
  finalizing: "Finalizing video",
  done: "Done",
  failed: "Failed",
  cancelled: "Cancelled",
};

export function stageLabel(stage: string): string {
  return STAGE_LABELS[stage] ?? stage;
}

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "unofun — AI Video Dubbing in 20+ Languages",
  description: "Paste any video URL. Get a voice-over in 20+ languages with synced subtitles — instantly.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-ink font-sans antialiased">{children}</body>
    </html>
  );
}

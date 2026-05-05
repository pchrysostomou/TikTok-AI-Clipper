import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "AI Clipper — YouTube to Shorts in Minutes",
  description: "Paste a YouTube URL. Our AI finds the best viral moments, crops to 9:16, adds subtitles, and lets you publish to YouTube Shorts instantly.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}

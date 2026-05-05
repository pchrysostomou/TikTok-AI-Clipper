"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { startProcessing } from "@/lib/api";
import { getUserId } from "@/lib/userId";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleProcess = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setError("");
    try {
      const userId = getUserId();
      const data = await startProcessing(url.trim(), userId);
      localStorage.setItem("current_job_id", data.job_id);
      router.push("/dashboard");
    } catch (e: any) {
      setError(e.message || "Something went wrong");
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleProcess();
  };

  return (
    <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "120px 24px 60px", position: "relative", overflow: "hidden" }}>
      {/* Background orbs */}
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none", overflow: "hidden" }}>
        <div style={{ position: "absolute", width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, #7c3aed30 0%, transparent 70%)", top: "-200px", left: "-200px", animation: "float 8s ease-in-out infinite" }} />
        <div style={{ position: "absolute", width: 500, height: 500, borderRadius: "50%", background: "radial-gradient(circle, #f7258530 0%, transparent 70%)", bottom: "-150px", right: "-150px", animation: "float 10s ease-in-out infinite reverse" }} />
      </div>

      {/* Badge */}
      <div className="fade-up" style={{ animationDelay: "0s", marginBottom: 24 }}>
        <span className="badge badge-processing" style={{ fontSize: 13, padding: "6px 16px" }}>
          <span className="pulse-dot" />
          Powered by Groq · Llama 3.3 70B · Whisper Large v3
        </span>
      </div>

      {/* Heading */}
      <h1 className="fade-up" style={{ fontFamily: "var(--font-heading)", fontSize: "clamp(42px, 7vw, 80px)", fontWeight: 800, textAlign: "center", lineHeight: 1.1, marginBottom: 20, animationDelay: "0.1s" }}>
        Turn YouTube Videos<br />
        <span className="gradient-text">Into Viral Clips</span>
      </h1>

      <p className="fade-up" style={{ color: "var(--muted)", fontSize: 18, textAlign: "center", maxWidth: 560, marginBottom: 48, lineHeight: 1.7, animationDelay: "0.2s" }}>
        Paste any YouTube URL. Our AI finds the best moments, crops to 9:16, adds subtitles, and gets them ready to publish — in minutes.
      </p>

      {/* Input area */}
      <div className="fade-up glass" style={{ width: "100%", maxWidth: 680, padding: 8, display: "flex", gap: 8, alignItems: "center", animationDelay: "0.3s" }}>
        <input
          className="input"
          style={{ border: "none", background: "transparent", flex: 1, fontSize: 16 }}
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={e => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button className="btn btn-primary" onClick={handleProcess} disabled={loading || !url.trim()}>
          {loading ? <><span className="spin">⟳</span> Processing...</> : <><span>🎬</span> Generate Clips</>}
        </button>
      </div>

      {error && (
        <div className="fade-up" style={{ marginTop: 16, color: "var(--error)", fontSize: 14, background: "#ef444415", padding: "10px 20px", borderRadius: 8, border: "1px solid #ef444430" }}>
          ⚠️ {error}
        </div>
      )}

      {/* Features */}
      <div className="fade-up" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, maxWidth: 860, width: "100%", marginTop: 72, animationDelay: "0.4s" }}>
        {[
          { icon: "🎙️", title: "AI Transcription", desc: "Whisper Large v3 with word-level timestamps" },
          { icon: "🤖", title: "Smart Analysis", desc: "Llama 3.3 70B finds the best viral moments" },
          { icon: "✂️", title: "Auto Crop 9:16", desc: "Face-tracking crop for vertical video" },
          { icon: "📝", title: "Auto Subtitles", desc: "Burned-in captions for silent viewers" },
          { icon: "▶️", title: "YouTube Shorts", desc: "Publish directly to your channel" },
          { icon: "💰", title: "Zero Cost", desc: "Runs entirely on free-tier APIs" },
        ].map(f => (
          <div key={f.title} className="glass" style={{ padding: "20px 24px", textAlign: "center" }}>
            <div style={{ fontSize: 32, marginBottom: 10 }}>{f.icon}</div>
            <div style={{ fontFamily: "var(--font-heading)", fontWeight: 600, fontSize: 15, marginBottom: 6 }}>{f.title}</div>
            <div style={{ color: "var(--muted)", fontSize: 13, lineHeight: 1.5 }}>{f.desc}</div>
          </div>
        ))}
      </div>
    </main>
  );
}

"use client";
import { useState, useRef } from "react";

type Clip = {
  id: string; title: string; ai_reason: string;
  start_time: number; end_time: number; duration: number;
  cloudinary_url: string; published_to: string[]; youtube_short_url?: string;
};

export default function ClipCard({ clip, onDelete, onPublish, publishing }: {
  clip: Clip;
  onDelete: () => void;
  onPublish: (caption?: string) => void;
  publishing: boolean;
}) {
  const [showCaption, setShowCaption] = useState(false);
  const [caption, setCaption] = useState(clip.title);
  const videoRef = useRef<HTMLVideoElement>(null);
  const isPublished = clip.published_to?.includes("youtube_shorts");

  const fmt = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = Math.floor(s % 60);
    return `${m}:${sec.toString().padStart(2, "0")}`;
  };

  return (
    <div className="glass" style={{ overflow: "hidden", display: "flex", flexDirection: "column" }}>
      {/* Video (9:16 aspect ratio) */}
      <div style={{ position: "relative", paddingBottom: "177.78%", background: "#000" }}>
        <video
          ref={videoRef}
          src={clip.cloudinary_url}
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
          controls
          preload="metadata"
        />
        {isPublished && (
          <div style={{ position: "absolute", top: 12, right: 12, background: "#10b981", borderRadius: 8, padding: "4px 10px", fontSize: 12, fontWeight: 600, color: "#fff" }}>
            ✓ Published
          </div>
        )}
      </div>

      {/* Info */}
      <div style={{ padding: "16px 20px", flex: 1, display: "flex", flexDirection: "column", gap: 12 }}>
        <div>
          <h3 style={{ fontFamily: "var(--font-heading)", fontWeight: 600, fontSize: 16, marginBottom: 6, lineHeight: 1.3 }}>{clip.title}</h3>
          <p style={{ color: "var(--muted)", fontSize: 13, lineHeight: 1.5 }}>🤖 {clip.ai_reason}</p>
        </div>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <span className="badge badge-pending">{fmt(clip.start_time)} → {fmt(clip.end_time)}</span>
          <span className="badge badge-pending">{Math.round(clip.duration)}s</span>
        </div>

        {/* Publish caption input */}
        {showCaption && (
          <div>
            <input
              className="input"
              style={{ fontSize: 13, padding: "10px 14px" }}
              value={caption}
              onChange={e => setCaption(e.target.value)}
              placeholder="Add a caption for your Short..."
            />
          </div>
        )}

        {/* Actions */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: "auto" }}>
          {isPublished ? (
            <a href={clip.youtube_short_url} target="_blank" rel="noreferrer" className="btn btn-success btn-sm" style={{ textAlign: "center", justifyContent: "center" }}>
              ▶️ View YouTube Short
            </a>
          ) : (
            <button
              className="btn btn-primary btn-sm"
              style={{ justifyContent: "center" }}
              onClick={() => {
                if (showCaption) { onPublish(caption); setShowCaption(false); }
                else setShowCaption(true);
              }}
              disabled={publishing}
            >
              {publishing ? <><span className="spin">⟳</span> Publishing...</> : showCaption ? "✓ Confirm & Publish" : "▶️ Publish to YouTube Shorts"}
            </button>
          )}

          <div style={{ display: "flex", gap: 8 }}>
            <a href={clip.cloudinary_url} download className="btn btn-outline btn-sm" style={{ flex: 1, justifyContent: "center" }}>
              ⬇️ Download
            </a>
            <button className="btn btn-danger btn-sm" onClick={onDelete} style={{ flex: 1, justifyContent: "center" }}>
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

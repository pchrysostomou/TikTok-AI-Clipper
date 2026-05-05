const STEPS: Record<string, { label: string; icon: string; index: number }> = {
  pending:      { label: "Queued...", icon: "⏳", index: 0 },
  downloading:  { label: "Downloading video", icon: "📥", index: 1 },
  transcribing: { label: "Transcribing audio (Whisper)", icon: "🎙️", index: 2 },
  analyzing:    { label: "Finding best clips (Llama 3.3)", icon: "🤖", index: 3 },
  editing:      { label: "Editing & cropping clips", icon: "✂️", index: 4 },
  uploading:    { label: "Uploading to Cloudinary", icon: "☁️", index: 5 },
  done:         { label: "Complete!", icon: "✅", index: 6 },
};

export default function ProcessingStatus({ job }: { job: { status: string; youtube_title?: string } }) {
  const current = STEPS[job.status] || STEPS["pending"];
  const totalSteps = 6;

  return (
    <div className="glass fade-up" style={{ padding: "24px 28px", marginBottom: 32, borderColor: "rgba(124,58,237,0.3)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontSize: 24 }}>{current.icon}</span>
          <div>
            <div style={{ fontWeight: 600, fontSize: 15 }}>{current.label}</div>
            {job.youtube_title && (
              <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 2 }}>"{job.youtube_title}"</div>
            )}
          </div>
        </div>
        <span className="badge badge-processing">
          <span className="pulse-dot" />
          Processing
        </span>
      </div>

      {/* Progress bar */}
      <div style={{ height: 6, background: "#ffffff10", borderRadius: 99, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${(current.index / totalSteps) * 100}%`,
          background: "linear-gradient(90deg, #7c3aed, #f72585)",
          borderRadius: 99,
          transition: "width 0.5s ease",
        }} />
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
        {Object.values(STEPS).slice(0, -1).map((s) => (
          <span key={s.index} style={{ fontSize: 10, color: s.index <= current.index ? "var(--primary-light)" : "var(--muted)" }}>
            {s.icon}
          </span>
        ))}
      </div>
    </div>
  );
}

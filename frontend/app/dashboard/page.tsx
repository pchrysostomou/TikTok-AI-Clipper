"use client";
import { useState, useEffect, useCallback } from "react";
import { getJobStatus, getClips, deleteClip, publishToYouTube } from "@/lib/api";
import { getUserId } from "@/lib/userId";
import ClipCard from "@/components/ClipCard";
import ProcessingStatus from "@/components/ProcessingStatus";

const POLL_MS = 3000;

type Clip = {
  id: string; job_id: string; user_id: string; title: string;
  ai_reason: string; start_time: number; end_time: number; duration: number;
  cloudinary_url: string; cloudinary_public_id: string;
  published_to: string[]; youtube_short_url?: string; created_at: string;
};

type Job = {
  id: string; status: string; youtube_title?: string;
  youtube_thumbnail?: string; error_message?: string;
};

export default function Dashboard() {
  const [clips, setClips] = useState<Clip[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState<string | null>(null);
  const userId = typeof window !== "undefined" ? getUserId() : "";
  const jobId = typeof window !== "undefined" ? localStorage.getItem("current_job_id") : null;

  const fetchClips = useCallback(async () => {
    try {
      const data = await getClips(userId);
      setClips(data);
    } catch {}
  }, [userId]);

  useEffect(() => {
    if (!jobId) { setLoading(false); fetchClips(); return; }
    let timer: ReturnType<typeof setInterval>;

    const poll = async () => {
      try {
        const j = await getJobStatus(jobId);
        setJob(j);
        if (j.status === "done" || j.status === "failed") {
          clearInterval(timer);
          await fetchClips();
          setLoading(false);
        }
      } catch { clearInterval(timer); setLoading(false); }
    };

    poll();
    timer = setInterval(poll, POLL_MS);
    return () => clearInterval(timer);
  }, [jobId, fetchClips]);

  const handleDelete = async (clipId: string) => {
    if (!confirm("Delete this clip?")) return;
    await deleteClip(clipId, userId);
    setClips(prev => prev.filter(c => c.id !== clipId));
  };

  const handlePublish = async (clipId: string, caption?: string) => {
    setPublishing(clipId);
    try {
      const res = await publishToYouTube(clipId, userId, caption);
      window.open(res.youtube_url, "_blank");
      await fetchClips();
    } catch (e: any) {
      alert("Failed to publish: " + e.message);
    } finally { setPublishing(null); }
  };

  const isProcessing = job && !["done", "failed"].includes(job.status);

  return (
    <main style={{ minHeight: "100vh", padding: "100px 24px 60px", maxWidth: 1100, margin: "0 auto" }}>
      <div className="fade-up" style={{ marginBottom: 40 }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 36, fontWeight: 700, marginBottom: 8 }}>
          Your <span className="gradient-text">Clips</span>
        </h1>
        <p style={{ color: "var(--muted)" }}>AI-generated short clips ready to publish</p>
      </div>

      {isProcessing && job && <ProcessingStatus job={job} />}
      {job?.status === "failed" && (
        <div className="glass fade-up" style={{ padding: 20, marginBottom: 32, borderColor: "#ef444430", background: "#ef444410" }}>
          <strong style={{ color: "var(--error)" }}>⚠️ Processing failed:</strong>
          <span style={{ color: "var(--muted)", marginLeft: 8 }}>{job.error_message || "Unknown error"}</span>
        </div>
      )}

      {loading && isProcessing ? null : clips.length === 0 ? (
        <div className="glass fade-up" style={{ padding: "60px 40px", textAlign: "center" }}>
          <div style={{ fontSize: 64, marginBottom: 20 }}>🎬</div>
          <h3 style={{ fontFamily: "var(--font-heading)", fontSize: 22, marginBottom: 12 }}>No clips yet</h3>
          <p style={{ color: "var(--muted)", marginBottom: 28 }}>Paste a YouTube URL on the home page to get started.</p>
          <a href="/" className="btn btn-primary">Go to Home</a>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 24 }}>
          {clips.map((clip, i) => (
            <div key={clip.id} className="fade-up" style={{ animationDelay: `${i * 0.1}s` }}>
              <ClipCard
                clip={clip}
                onDelete={() => handleDelete(clip.id)}
                onPublish={(caption) => handlePublish(clip.id, caption)}
                publishing={publishing === clip.id}
              />
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

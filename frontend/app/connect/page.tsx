"use client";
import { useState, useEffect } from "react";
import { getYouTubeStatus, disconnectYouTube } from "@/lib/api";
import { getUserId } from "@/lib/userId";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type YTStatus = { connected: boolean; username?: string; avatar?: string };

export default function ConnectPage() {
  const [ytStatus, setYtStatus] = useState<YTStatus>({ connected: false });
  const [loading, setLoading] = useState(true);
  const [disconnecting, setDisconnecting] = useState(false);

  const userId = typeof window !== "undefined" ? getUserId() : "";

  useEffect(() => {
    getYouTubeStatus(userId).then(s => { setYtStatus(s); setLoading(false); });
    const params = new URLSearchParams(window.location.search);
    if (params.get("success")) {
      getYouTubeStatus(userId).then(setYtStatus);
      window.history.replaceState({}, "", "/connect");
    }
  }, [userId]);

  const handleConnect = () => {
    window.location.href = `${API}/api/auth/youtube?user_id=${userId}`;
  };

  const handleDisconnect = async () => {
    setDisconnecting(true);
    await disconnectYouTube(userId);
    setYtStatus({ connected: false });
    setDisconnecting(false);
  };

  return (
    <main style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "100px 24px 60px" }}>
      <div className="fade-up" style={{ textAlign: "center", marginBottom: 48 }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: 40, fontWeight: 700, marginBottom: 12 }}>
          Connect <span className="gradient-text">Accounts</span>
        </h1>
        <p style={{ color: "var(--muted)", fontSize: 16 }}>Link your social accounts to publish clips directly</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: 24, width: "100%", maxWidth: 800 }}>
        {/* YouTube card */}
        <div className="glass fade-up" style={{ padding: 32 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
            <div style={{ width: 52, height: 52, borderRadius: 14, background: "#ff000020", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28 }}>▶️</div>
            <div>
              <div style={{ fontFamily: "var(--font-heading)", fontWeight: 700, fontSize: 18 }}>YouTube</div>
              <div style={{ color: "var(--muted)", fontSize: 13 }}>Publish as YouTube Shorts</div>
            </div>
          </div>

          {loading ? (
            <div style={{ color: "var(--muted)" }}>Checking status...</div>
          ) : ytStatus.connected ? (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20, padding: "12px 16px", background: "#10b98115", borderRadius: 10, border: "1px solid #10b98130" }}>
                {ytStatus.avatar && <img src={ytStatus.avatar} alt="" style={{ width: 40, height: 40, borderRadius: "50%" }} />}
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>✅ Connected</div>
                  <div style={{ color: "var(--muted)", fontSize: 13 }}>{ytStatus.username}</div>
                </div>
              </div>
              <button className="btn btn-danger" style={{ width: "100%" }} onClick={handleDisconnect} disabled={disconnecting}>
                {disconnecting ? "Disconnecting..." : "Disconnect YouTube"}
              </button>
            </>
          ) : (
            <>
              <p style={{ color: "var(--muted)", fontSize: 14, marginBottom: 20, lineHeight: 1.6 }}>
                Connect your YouTube channel to publish clips as Shorts with one click.
              </p>
              <button className="btn btn-primary" style={{ width: "100%" }} onClick={handleConnect}>
                🔗 Connect YouTube
              </button>
            </>
          )}
        </div>
      </div>
    </main>
  );
}

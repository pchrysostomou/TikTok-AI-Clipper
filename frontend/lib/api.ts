const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function startProcessing(youtubeUrl: string, userId: string) {
  const res = await fetch(`${API}/api/process`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ youtube_url: youtubeUrl, user_id: userId }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getJobStatus(jobId: string) {
  const res = await fetch(`${API}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export async function getClips(userId: string) {
  const res = await fetch(`${API}/api/clips?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to fetch clips");
  return res.json();
}

export async function deleteClip(clipId: string, userId: string) {
  const res = await fetch(`${API}/api/clips/${clipId}?user_id=${userId}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete clip");
  return res.json();
}

export async function publishToYouTube(clipId: string, userId: string, caption?: string) {
  const res = await fetch(`${API}/api/clips/${clipId}/publish/youtube`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, caption }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getYouTubeStatus(userId: string) {
  const res = await fetch(`${API}/api/auth/youtube/status?user_id=${userId}`);
  if (!res.ok) return { connected: false };
  return res.json();
}

export async function disconnectYouTube(userId: string) {
  await fetch(`${API}/api/auth/youtube/disconnect?user_id=${userId}`, { method: "DELETE" });
}

-- ============================================================
-- YouTube → TikTok AI Clipper — Supabase Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- Connected social accounts (YouTube OAuth tokens)
CREATE TABLE IF NOT EXISTS connected_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  access_token TEXT NOT NULL,
  refresh_token TEXT DEFAULT '',
  expires_at TIMESTAMPTZ,
  platform_user_id TEXT DEFAULT '',
  platform_username TEXT DEFAULT '',
  platform_avatar TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, platform)
);

-- Processing jobs
CREATE TABLE IF NOT EXISTS processing_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  youtube_url TEXT NOT NULL,
  youtube_title TEXT DEFAULT '',
  youtube_thumbnail TEXT DEFAULT '',
  status TEXT DEFAULT 'pending',
  error_message TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- Generated clips
CREATE TABLE IF NOT EXISTS clips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES processing_jobs(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL,
  title TEXT DEFAULT '',
  ai_reason TEXT DEFAULT '',
  start_time FLOAT DEFAULT 0,
  end_time FLOAT DEFAULT 0,
  duration FLOAT DEFAULT 0,
  cloudinary_url TEXT DEFAULT '',
  cloudinary_public_id TEXT DEFAULT '',
  published_to JSONB DEFAULT '[]'::jsonb,
  youtube_short_url TEXT DEFAULT '',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE connected_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE clips ENABLE ROW LEVEL SECURITY;

-- Permissive policies for development (tighten with proper auth later)
DROP POLICY IF EXISTS "allow_all_connected_accounts" ON connected_accounts;
CREATE POLICY "allow_all_connected_accounts" ON connected_accounts FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "allow_all_processing_jobs" ON processing_jobs;
CREATE POLICY "allow_all_processing_jobs" ON processing_jobs FOR ALL USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "allow_all_clips" ON clips;
CREATE POLICY "allow_all_clips" ON clips FOR ALL USING (true) WITH CHECK (true);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON processing_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_clips_user_id ON clips(user_id);
CREATE INDEX IF NOT EXISTS idx_clips_job_id ON clips(job_id);
CREATE INDEX IF NOT EXISTS idx_accounts_user_platform ON connected_accounts(user_id, platform);

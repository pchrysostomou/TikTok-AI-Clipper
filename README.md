# 🎬 YouTube → TikTok AI Clipper

![Project Banner](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-black?logo=next.js)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)
![AI](https://img.shields.io/badge/AI-Whisper_%26_Llama_3-blue)
 
An automated, end-to-end AI application that takes any long-form YouTube video, transcribes it, uses AI to find the most "viral" moments, automatically crops the video to vertical (9:16) format, and uploads the final clips ready for TikTok, YouTube Shorts, or Instagram Reels.

## ✨ Features
* **Lightning Fast Downloads**: Uses `yt-dlp` to download only the specific timestamps of the video, saving huge amounts of bandwidth and time.
* **AI Transcription**: High-accuracy word-level transcription powered by OpenAI's Whisper model (via Groq API).
* **Viral Moment Detection**: Leverages Llama 3 to analyze the transcript context and extract the funniest, most engaging, or most educational clips (30-90 seconds).
* **Automated Video Editing**: Uses FFmpeg to perform centered face-tracking/cropping and scales the video perfectly for mobile aspect ratios.
* **Cloud Ready**: Auto-uploads the final, polished clips straight to your Cloudinary storage.

---

## 🏗️ Tech Stack

* **Frontend**: Next.js (React), TailwindCSS, TypeScript
* **Backend**: FastAPI (Python 3.12), Pydantic
* **AI Models**: Groq Cloud (Llama 3.3 for analysis, Whisper-Large for transcription)
* **Media Processing**: FFmpeg, yt-dlp
* **Database**: Supabase (PostgreSQL)
* **Storage**: Cloudinary

---

## ⚙️ Prerequisites

Before you start, make sure you have the following installed on your machine:
1. **Node.js** (v18+)
2. **Python** (v3.10+)
3. **FFmpeg**: The core video editing engine.
   * *Mac*: `brew install ffmpeg`
   * *Windows*: `winget install ffmpeg`

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd TikTok-Ai-Tool
```

### 2. Frontend Setup
```bash
cd frontend
npm install
# or yarn install
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

You need to set up your API keys to make the magic happen.

In the `backend/` folder, create a `.env` file (if it doesn't exist) and fill it with your credentials:

```env
# AI Models (Get your free key at console.groq.com)
GROQ_API_KEY=your_groq_api_key

# Video Storage (Get from cloudinary.com)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Database (Get from supabase.com)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_api_key

# YouTube OAuth (Google Cloud Console)
YOUTUBE_CLIENT_ID=your_client_id
YOUTUBE_CLIENT_SECRET=your_client_secret
YOUTUBE_REDIRECT_URI=http://localhost:8002/api/auth/youtube/callback

# Frontend Communication
FRONTEND_URL=http://localhost:3000
```

---

## 🗄️ Database Setup (Supabase)

For the system to track jobs and save clips, you must create the tables in your Supabase project:
1. Open your [Supabase Dashboard](https://supabase.com).
2. Go to **SQL Editor** on the left menu.
3. Click **New Query**.
4. Copy the entire contents of the `supabase/schema.sql` file from this repository, paste it into the editor, and click **Run**.

---

## 🏃‍♂️ Running the Application

You need two terminal windows to run both the frontend and backend simultaneously.

**Terminal 1 (Backend - FastAPI):**
```bash
cd backend
# Make sure your virtual environment is activated
python run.py
# The backend will run on http://localhost:8002
```

**Terminal 2 (Frontend - Next.js):**
```bash
cd frontend
npm run dev
# The frontend will run on http://localhost:3000
```

> **🎉 You're Done!** Open `http://localhost:3000` in your browser, paste a YouTube link, and watch the AI do all the hard work!

---

## ⚠️ Known MacOS Limitations
If you are running this on a Mac (especially older Intel Macs or under Rosetta), there are two specific adjustments already handled in the codebase to prevent silent crashes:
1. **AVX Face Tracking**: `mediapipe` requires AVX instructions. If your Mac lacks this, the app defaults to a clean center-crop instead of crashing.
2. **FFmpeg Subtitles**: Standard Homebrew FFmpeg installations sometimes lack the `libass` library. Hardcoded subtitles are bypassed if `libass` isn't present, so the pipeline completes flawlessly without text overlays.

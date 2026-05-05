from dotenv import load_dotenv
import os
load_dotenv(".env")
from database import get_db
try:
    db = get_db()
    jobs = db.table("processing_jobs").select("*").order("created_at", desc=True).limit(2).execute()
    if jobs.data:
        for job in jobs.data:
            print(f"Job ID: {job['id']} | Status: {job['status']}")
            clips = db.table("clips").select("*").eq("job_id", job["id"]).execute()
            print(f"  -> Found {len(clips.data)} clips for this job.")
    else:
        print("No jobs found in DB.")
except Exception as e:
    print(f"Error querying DB: {e}")

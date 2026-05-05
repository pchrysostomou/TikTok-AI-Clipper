from dotenv import load_dotenv
load_dotenv(".env")
from database import get_db
db = get_db()
jobs = db.table("processing_jobs").select("*").eq("status", "failed").execute()
for j in jobs.data:
    print(f"Failed Error: {j.get('error_message')}")

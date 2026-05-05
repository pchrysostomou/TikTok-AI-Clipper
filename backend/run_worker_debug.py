from dotenv import load_dotenv
load_dotenv(".env")
from database import get_db
db = get_db()
job = db.table("processing_jobs").select("*").eq("id", "47534c0b-1eb9-4059-aef7-cbb55513b3f0").execute().data[0]
print(job["id"], job["youtube_url"], job["user_id"])

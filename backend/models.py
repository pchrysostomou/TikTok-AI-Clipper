from pydantic import BaseModel
from typing import Optional, List

class ProcessRequest(BaseModel):
    youtube_url: str
    user_id: str

class ProcessResponse(BaseModel):
    status: str
    job_id: str
    message: str

class PublishYouTubeRequest(BaseModel):
    user_id: str
    caption: Optional[str] = None

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse
from database import get_db
import os, httpx, logging, datetime
from urllib.parse import urlencode
try:
    from postgrest.exceptions import APIError as PGError
except ImportError:
    PGError = Exception

router = APIRouter()
logger = logging.getLogger(__name__)

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"

SCOPES = " ".join([
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "openid", "email", "profile",
])


@router.get("/auth/youtube")
async def start_oauth(user_id: str = Query(...)):
    params = {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "redirect_uri": os.getenv("YOUTUBE_REDIRECT_URI"),
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": user_id,
    }
    return RedirectResponse(f"{AUTH_URL}?{urlencode(params)}")


@router.get("/auth/youtube/callback")
async def oauth_callback(code: str = Query(None), state: str = Query(None), error: str = Query(None)):
    frontend = os.getenv("FRONTEND_URL", "http://localhost:3000")
    if error:
        return RedirectResponse(f"{frontend}/connect?error={error}")
    if not code or not state:
        raise HTTPException(400, "Missing code or state")

    async with httpx.AsyncClient() as client:
        tokens_r = await client.post(TOKEN_URL, data={
            "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
            "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv("YOUTUBE_REDIRECT_URI"),
        })
    if tokens_r.status_code != 200:
        return RedirectResponse(f"{frontend}/connect?error=token_failed")

    tokens = tokens_r.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        ui = (await client.get(USERINFO_URL, headers=headers)).json()
        ch = (await client.get(CHANNELS_URL, params={"part": "snippet", "mine": "true"}, headers=headers)).json()

    if ch.get("items"):
        snippet = ch["items"][0]["snippet"]
        acc = {
            "platform_user_id": ch["items"][0]["id"],
            "platform_username": snippet.get("title", ui.get("name", "")),
            "platform_avatar": snippet.get("thumbnails", {}).get("default", {}).get("url", ui.get("picture", "")),
        }
    else:
        acc = {"platform_user_id": ui.get("sub", ""), "platform_username": ui.get("name", ""), "platform_avatar": ui.get("picture", "")}

    expires_at = None
    if "expires_in" in tokens:
        expires_at = (datetime.datetime.now(datetime.timezone.utc) +
                      datetime.timedelta(seconds=tokens["expires_in"])).isoformat()

    get_db().table("connected_accounts").upsert({
        "user_id": state,
        "platform": "youtube",
        "access_token": access_token,
        "refresh_token": tokens.get("refresh_token", ""),
        "expires_at": expires_at,
        **acc,
    }, on_conflict="user_id,platform").execute()

    return RedirectResponse(f"{frontend}/connect?success=true")


@router.get("/auth/youtube/status")
async def youtube_status(user_id: str = Query(...)):
    try:
        r = get_db().table("connected_accounts").select("*").eq("user_id", user_id).eq("platform", "youtube").execute()
        if r.data:
            a = r.data[0]
            return {"connected": True, "username": a.get("platform_username", ""), "avatar": a.get("platform_avatar", "")}
    except Exception as e:
        logger.warning(f"DB not ready yet: {e}")
    return {"connected": False}


@router.delete("/auth/youtube/disconnect")
async def disconnect(user_id: str = Query(...)):
    get_db().table("connected_accounts").delete().eq("user_id", user_id).eq("platform", "youtube").execute()
    return {"success": True}

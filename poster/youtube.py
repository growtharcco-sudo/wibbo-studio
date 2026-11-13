"""Upload a Short with the official YouTube Data API v3 (Wibbo's own Google Cloud project, so its own quota).

Needs: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (scopes youtube.upload + youtube).
Every Wibbo Short is "made for kids" (COPPA) and carries the "altered or synthetic content" disclosure.
"""
import os, time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError


def _env(name):
    """Secrets pasted with their label ("YT_CLIENT_ID = ...") or spaces still work."""
    v = os.environ.get(name, "").strip()
    if "=" in v and v.split("=", 1)[0].strip().upper() == name: v = v.split("=", 1)[1].strip()
    return v.strip().strip('"').strip("'").strip()


SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]


def _client():
    creds = Credentials(None, refresh_token=_env("YT_REFRESH_TOKEN"), client_id=_env("YT_CLIENT_ID"),
                        client_secret=_env("YT_CLIENT_SECRET"), token_uri="https://oauth2.googleapis.com/token", scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload_short(path, title, description, tags=None, privacy=None, made_for_kids=True):
    privacy = privacy or os.environ.get("YT_PRIVACY", "public")
    body = {"snippet": {"title": title[:100], "description": description[:4900], "tags": tags or [],
                        "categoryId": "27", "defaultLanguage": "en", "defaultAudioLanguage": "en"},   # 27 = Education
            "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": bool(made_for_kids),
                       "containsSyntheticMedia": True}}
    req = _client().videos().insert(part="snippet,status", body=body,
                                    media_body=MediaFileUpload(path, mimetype="video/mp4", resumable=True, chunksize=8 << 20))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    st = resp.get("status", {})
    return {"yt_video_id": resp["id"], "yt_url": f"https://youtube.com/shorts/{resp['id']}",
            "yt_privacy": st.get("privacyStatus"), "yt_made_for_kids": st.get("selfDeclaredMadeForKids")}


def set_thumbnail(video_id, image_path, tries=8, wait=45):
    """Use the cover as the thumbnail once the video has processed. A refusal never blocks the post."""
    yt = _client(); mime = "image/png"
    if os.path.getsize(image_path) > 2_000_000:          # API limit is 2 MB: send a high-quality JPEG copy
        from PIL import Image
        jpg = image_path.rsplit(".", 1)[0] + "_yt.jpg"; Image.open(image_path).convert("RGB").save(jpg, "JPEG", quality=95)
        image_path, mime = jpg, "image/jpeg"
    for i in range(tries):
        try:
            yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(image_path, mimetype=mime)).execute()
            return "set"
        except HttpError as e:
            code = e.resp.status
            if code == 403: return "not allowed yet (custom thumbnails need a verified channel)"
            if code in (400, 404, 409) and i < tries - 1: time.sleep(wait); continue
            return f"failed ({code})"
        except Exception as e:
            return f"failed ({type(e).__name__})"
    return "failed (video still processing)"


def delete_video(video_id):
    """Used only by the deep check to remove its own unlisted test upload."""
    _client().videos().delete(id=video_id).execute()

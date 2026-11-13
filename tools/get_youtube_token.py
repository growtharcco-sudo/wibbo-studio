"""One-time: get the YouTube refresh token. Run on your laptop. At sign-in, pick the WIBBO channel (@HelloWibbo).

  pip3 install google-auth-oauthlib
  python3 tools/get_youtube_token.py ~/Downloads/client_secret_XXXX.json      (the NEWEST file from Wibbo's project)

It prints YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN to paste into GitHub Secrets (not into a chat).
"""
import json, sys
from google_auth_oauthlib.flow import InstalledAppFlow

cfg = json.load(open(sys.argv[1]))
if "installed" not in cfg:
    sys.exit("This client file is not a Desktop app client. In Google Cloud > Credentials, create an OAuth client of type 'Desktop app' and download it.")
flow = InstalledAppFlow.from_client_secrets_file(sys.argv[1], ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
cfg = cfg["installed"]
print("\nPaste these into GitHub > Settings > Secrets and variables > Actions (one secret each):\n")
print("YT_CLIENT_ID     =", cfg["client_id"])
print("YT_CLIENT_SECRET =", cfg["client_secret"])
print("YT_REFRESH_TOKEN =", creds.refresh_token)

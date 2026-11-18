# One-time setup

Everything is free. Keys go only into GitHub's encrypted Secrets, never into a file or a chat.
Claude guides each step one screen at a time.

## A. GitHub
1. Repo `growtharcco-sudo/wibbo-studio`, Public (done), Claude GitHub app has access (done).
2. Repo -> Settings -> Pages -> Source *Deploy from a branch* -> `media` / `(root)` -> Save.
   Check: https://growtharcco-sudo.github.io/wibbo-studio/ shows the Wibbo page.

## B. Instagram key (never expires): reuse the existing Meta system user and app
Portfolio **The Real Number**, system user **unhyped-poster**, app **Real Number Studio**.
1. @hellowibbo -> Settings -> Account type -> switch to a **Business** (professional) account.
   TRAP: this can silently create a NEW business portfolio. It must end up in **The Real Number** portfolio.
2. business.facebook.com -> The Real Number -> Settings -> Accounts -> Pages -> Add -> **Create a new Page** "Wibbo".
   Then Accounts -> Instagram accounts -> Add -> connect @hellowibbo, and link it to the Wibbo Page.
3. Settings -> Users -> System users -> unhyped-poster -> **Assign assets**: the Wibbo Page and the @hellowibbo
   Instagram account, Full control. TRAP: re-open the system user and check both really show **Full access**
   (it can say "Nothing assigned yet").
4. Generate new token -> app **Real Number Studio** -> expiration **Never** -> permissions `instagram_basic`,
   `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`, `business_management` -> that is
   `IG_TOKEN` (starts with EAA). A new token does not break the other channels' tokens.
5. `IG_USER_ID`: leave it out at first. The **Check keys** run prints the ID to use.

## C. YouTube key: a NEW Google Cloud project for Wibbo (its own daily upload quota)
1. console.cloud.google.com -> New project **Wibbo Studio** -> APIs & Services -> Library -> **YouTube Data API v3** -> Enable.
2. Google Auth Platform (OAuth consent screen): External, app name **Wibbo Studio**, your email.
   - Branding: home page https://growtharcco-sudo.github.io/wibbo-studio/ , privacy .../privacy.html ,
     terms .../terms.html , authorized domain `growtharcco-sudo.github.io`.
     TRAP: "Publish app" stays greyed out until these three links and the domain are in.
   - Data access: add scopes `.../auth/youtube.upload` and `.../auth/youtube`.
   - Audience: **Publish app** -> "In production".
3. Clients -> Create client -> type **Desktop app** -> Download JSON.
   TRAP: `redirect_uri_mismatch` = wrong client type (must be Desktop) or an older client_secret file in Downloads.
4. On the laptop: `pip3 install google-auth-oauthlib`, then
   `python3 tools/get_youtube_token.py ~/Downloads/client_secret_<NEWEST>.json`. Sign in, choose the **Wibbo**
   channel (@HelloWibbo), click through "Google hasn't verified this app" (Advanced -> Go to Wibbo Studio).
   It prints `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

## D. Secrets
Repo -> Settings -> Secrets and variables -> Actions -> New repository secret, one each:
`IG_TOKEN`, `IG_USER_ID`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
Paste only the value (if a label or spaces slip in, the code cleans them).

## E. Test (posts nothing publicly). Claude runs these by pushing to `checks/`
1. **Check keys**: prints the Instagram username, YouTube channel name, IDs and quota. Never key values.
2. **Deep check**: Instagram processes a test Reel without publishing it; YouTube gets an UNLISTED test upload
   that is checked (stays unlisted = public uploads work), given the thumbnail, then deleted.
3. One real end-to-end post (slot `test`, `"now": true`), then the daily task is switched on.

## F. Scheduled task (Claude)
ONE cloud task, "Wibbo (group B)", runs `ROUTINE.md` section A every other day (even dates) at about 2 AM IST and makes 4 Reels: 08:00 and 18:30 for that day and the next.
It needs "Skip all approvals" (Automatically approve) on and no connectors it doesn't use.

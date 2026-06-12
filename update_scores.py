import json, urllib.request
from datetime import datetime, timezone

API_URL = "https://worldcup26.ir/get/games"

def main():
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}] Fetching...")
    req = urllib.request.Request(API_URL, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"❌ {e}"); return 1

    matches = data if isinstance(data, list) else (data.get("games") or data.get("matches") or [])
    print(f"Total: {len(matches)}")

    # Print finished and time_elapsed for ALL matches
    for m in matches:
        finished = m.get("finished", "N/A")
        elapsed  = m.get("time_elapsed", "N/A")
        home     = m.get("home_team_name_en", "?")
        away     = m.get("away_team_name_en", "?")
        hs       = m.get("home_score", "?")
        as_      = m.get("away_score", "?")
        if str(finished).upper() != "FALSE" or str(elapsed).lower() != "notstarted":
            print(f"  {home} vs {away} | finished={finished} | elapsed={elapsed} | score={hs}-{as_}")

if __name__ == "__main__":
    main()

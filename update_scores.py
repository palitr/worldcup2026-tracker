"""
update_scores.py - DEBUG VERSION
Prints status values to identify what worldcup26.ir uses
"""
import json, urllib.request, urllib.error
from datetime import datetime, timezone

API_URL = "https://worldcup26.ir/get/games"

def fetch_games():
    req = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())

def main():
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}] Fetching...")
    try:
        data = fetch_games()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    matches = data
    if isinstance(data, dict):
        matches = data.get("games") or data.get("matches") or data.get("data") or []

    print(f"Total matches: {len(matches)}")

    # Print ALL unique status values seen
    statuses = {}
    for m in matches:
        s = str(m.get("status") or m.get("matchStatus") or "NONE")
        statuses[s] = statuses.get(s, 0) + 1

    print("Status values found:")
    for k, v in sorted(statuses.items()):
        print(f"  '{k}': {v} matches")

    # Print first 3 matches in full to see structure
    print("\nFirst 3 matches (full structure):")
    for m in matches[:3]:
        print(json.dumps(m, indent=2, default=str))

    return 0

if __name__ == "__main__":
    exit(main())

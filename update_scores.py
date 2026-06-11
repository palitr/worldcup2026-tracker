"""
update_scores.py
FIFA World Cup 2026 — Live Score Updater
Fetches results from worldcup26.ir (free, no API key needed for /get/games)
© 2026 Rajarshi Palit
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL = "https://worldcup26.ir/get/games"

# ── Team name mapping: API name → tracker name ────────────────────────────
TEAM_MAP = {
    "Mexico":                    "Mexico",
    "South Africa":              "South Africa",
    "South Korea":               "South Korea",
    "Korea Republic":            "South Korea",
    "Czechia":                   "Czechia",
    "Czech Republic":            "Czechia",
    "Canada":                    "Canada",
    "Bosnia and Herzegovina":    "Bosnia-Herzegovina",
    "Bosnia & Herzegovina":      "Bosnia-Herzegovina",
    "Qatar":                     "Qatar",
    "Switzerland":               "Switzerland",
    "Brazil":                    "Brazil",
    "Morocco":                   "Morocco",
    "Haiti":                     "Haiti",
    "Scotland":                  "Scotland",
    "USA":                       "USA",
    "United States":             "USA",
    "Paraguay":                  "Paraguay",
    "Australia":                 "Australia",
    "Turkey":                    "Turkiye",
    "Turkiye":                   "Turkiye",
    "Türkiye":                   "Turkiye",
    "Germany":                   "Germany",
    "Curacao":                   "Curacao",
    "Curaçao":                   "Curacao",
    "Ivory Coast":               "Ivory Coast",
    "Côte d'Ivoire":             "Ivory Coast",
    "Ecuador":                   "Ecuador",
    "Netherlands":               "Netherlands",
    "Japan":                     "Japan",
    "Sweden":                    "Sweden",
    "Tunisia":                   "Tunisia",
    "Belgium":                   "Belgium",
    "Egypt":                     "Egypt",
    "Saudi Arabia":              "Saudi Arabia",
    "Uruguay":                   "Uruguay",
    "Iran":                      "Iran",
    "New Zealand":               "New Zealand",
    "Spain":                     "Spain",
    "Cape Verde":                "Cape Verde",
    "Cabo Verde":                "Cape Verde",
    "France":                    "France",
    "Senegal":                   "Senegal",
    "Iraq":                      "Iraq",
    "Norway":                    "Norway",
    "Argentina":                 "Argentina",
    "Algeria":                   "Algeria",
    "Austria":                   "Austria",
    "Jordan":                    "Jordan",
    "Portugal":                  "Portugal",
    "DR Congo":                  "DR Congo",
    "Congo DR":                  "DR Congo",
    "Uzbekistan":                "Uzbekistan",
    "Colombia":                  "Colombia",
    "England":                   "England",
    "Croatia":                   "Croatia",
    "Ghana":                     "Ghana",
    "Panama":                    "Panama",
}

# ── Match ID mapping: (home_team, away_team) → tracker ID ─────────────────
MATCH_MAP = {
    ("Mexico",          "South Africa"):       "A1",
    ("South Korea",     "Czechia"):            "A2",
    ("Czechia",         "South Africa"):       "A3",
    ("Mexico",          "South Korea"):        "A4",
    ("South Africa",    "South Korea"):        "A5",
    ("Mexico",          "Czechia"):            "A6",
    ("Canada",          "Bosnia-Herzegovina"): "B1",
    ("Qatar",           "Switzerland"):        "B2",
    ("Switzerland",     "Bosnia-Herzegovina"): "B3",
    ("Canada",          "Qatar"):              "B4",
    ("Switzerland",     "Canada"):             "B5",
    ("Bosnia-Herzegovina", "Qatar"):           "B6",
    ("Brazil",          "Morocco"):            "C1",
    ("Haiti",           "Scotland"):           "C2",
    ("Scotland",        "Morocco"):            "C3",
    ("Brazil",          "Haiti"):              "C4",
    ("Scotland",        "Brazil"):             "C5",
    ("Morocco",         "Haiti"):              "C6",
    ("USA",             "Paraguay"):           "D1",
    ("Australia",       "Turkiye"):            "D2",
    ("USA",             "Australia"):          "D3",
    ("Turkiye",         "Paraguay"):           "D4",
    ("Turkiye",         "USA"):                "D5",
    ("Paraguay",        "Australia"):          "D6",
    ("Germany",         "Curacao"):            "E1",
    ("Ivory Coast",     "Ecuador"):            "E2",
    ("Germany",         "Ivory Coast"):        "E3",
    ("Ecuador",         "Curacao"):            "E4",
    ("Ecuador",         "Germany"):            "E5",
    ("Curacao",         "Ivory Coast"):        "E6",
    ("Netherlands",     "Japan"):              "F1",
    ("Sweden",          "Tunisia"):            "F2",
    ("Netherlands",     "Sweden"):             "F3",
    ("Tunisia",         "Japan"):              "F4",
    ("Japan",           "Sweden"):             "F5",
    ("Tunisia",         "Netherlands"):        "F6",
    ("Belgium",         "Egypt"):              "G1",
    ("Saudi Arabia",    "Uruguay"):            "G2",
    ("Belgium",         "Iran"):               "G3",
    ("Uruguay",         "Cape Verde"):         "G4",
    ("Egypt",           "Iran"):               "G5",
    ("New Zealand",     "Belgium"):            "G6",
    ("Spain",           "Cape Verde"):         "H1",
    ("Iran",            "New Zealand"):        "H2",
    ("Spain",           "Saudi Arabia"):       "H3",
    ("Cape Verde",      "Saudi Arabia"):       "H4",
    ("Uruguay",         "Spain"):              "H5",
    ("New Zealand",     "Egypt"):              "H6",
    ("France",          "Senegal"):            "I1",
    ("Iraq",            "Norway"):             "I2",
    ("Norway",          "Senegal"):            "I3",
    ("France",          "Iraq"):               "I4",
    ("Norway",          "France"):             "I5",
    ("Senegal",         "Iraq"):               "I6",
    ("Argentina",       "Algeria"):            "J1",
    ("Austria",         "Jordan"):             "J2",
    ("Argentina",       "Austria"):            "J3",
    ("Jordan",          "Algeria"):            "J4",
    ("Algeria",         "Austria"):            "J5",
    ("Jordan",          "Argentina"):          "J6",
    ("Portugal",        "DR Congo"):           "K1",
    ("Uzbekistan",      "Colombia"):           "K2",
    ("Portugal",        "Uzbekistan"):         "K3",
    ("Colombia",        "DR Congo"):           "K4",
    ("Colombia",        "Portugal"):           "K5",
    ("DR Congo",        "Uzbekistan"):         "K6",
    ("England",         "Croatia"):            "L1",
    ("Ghana",           "Panama"):             "L2",
    ("England",         "Ghana"):              "L3",
    ("Panama",          "Croatia"):            "L4",
    ("Panama",          "England"):            "L5",
    ("Croatia",         "Ghana"):              "L6",
}

# KO stage mapping
KO_STAGE_MAP = {
    "Round of 32":         "R32",
    "Round Of 32":         "R32",
    "last_32":             "R32",
    "Round of 16":         "R16",
    "Round Of 16":         "R16",
    "last_16":             "R16",
    "Quarter Final":       "QF",
    "Quarter Finals":      "QF",
    "quarter_finals":      "QF",
    "Semi Final":          "SF",
    "Semi Finals":         "SF",
    "semi_finals":         "SF",
    "Final":               "FINAL",
    "final":               "FINAL",
    "Third Place":         "BRONZE",
    "Third Place Playoff": "BRONZE",
    "third_place":         "BRONZE",
}


def fetch_games():
    req = urllib.request.Request(
        API_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def map_team(name):
    if not name:
        return name
    return TEAM_MAP.get(name, name)


def build_scores(data):
    scores = {}
    pen_scores = {}
    ko_counters = {s: 1 for s in ["R32", "R16", "QF", "SF"]}

    matches = data
    if isinstance(data, dict):
        matches = (data.get("games") or data.get("matches")
                   or data.get("data") or [])

    print(f"  Total matches from API: {len(matches)}")

    for m in matches:
        status = str(m.get("status") or m.get("matchStatus") or "").lower()
        if status not in ("completed", "finished", "in_play", "live",
                          "inplay", "in-play", "paused", "1", "2", "3"):
            continue

        home_raw = ((m.get("homeTeam") or {}).get("name")
                    or m.get("home_team") or m.get("team1") or "")
        away_raw = ((m.get("awayTeam") or {}).get("name")
                    or m.get("away_team") or m.get("team2") or "")

        home_score = (m.get("homeScore") or m.get("home_score")
                      or m.get("score1") or 0)
        away_score = (m.get("awayScore") or m.get("away_score")
                      or m.get("score2") or 0)

        if home_score is None or away_score is None:
            continue

        home  = map_team(home_raw.strip())
        away  = map_team(away_raw.strip())
        stage = str(m.get("stage") or m.get("round") or m.get("phase") or "")

        match_id = MATCH_MAP.get((home, away))

        if not match_id:
            stage_key = KO_STAGE_MAP.get(stage)
            if stage_key:
                if stage_key in ("FINAL", "BRONZE"):
                    match_id = stage_key
                else:
                    n = ko_counters.get(stage_key, 1)
                    match_id = f"{stage_key}_{n}"
                    ko_counters[stage_key] = n + 1

        if not match_id:
            print(f"  ⚠️  Unmatched: {home} vs {away} [{stage}] status={status}")
            continue

        scores[match_id] = {"h": int(home_score), "a": int(away_score)}
        print(f"  ✅ {match_id}: {home} {home_score}–{away_score} {away}")

    return scores, pen_scores


def main():
    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}] "
          f"Fetching WC2026 scores from worldcup26.ir...")

    try:
        data = fetch_games()
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.reason}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    scores, pen_scores = build_scores(data)

    output = {
        "updated":   datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00Z"),
        "scores":    scores,
        "penScores": pen_scores,
    }

    with open("scores.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ scores.json written — {len(scores)} results")
    return 0


if __name__ == "__main__":
    exit(main())

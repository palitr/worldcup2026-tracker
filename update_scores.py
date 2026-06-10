"""
update_scores.py
FIFA World Cup 2026 — Live Score Updater
Fetches results from football-data.org v4 API and writes scores.json
© 2026 Rajarshi Palit
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_KEY = os.environ.get("FOOTBALL_DATA_API_KEY", "")
API_URL = "https://api.football-data.org/v4/competitions/WC/matches?season=2026"

# ── Team name mapping: API name → your tracker name ──────────────────────
TEAM_MAP = {
    "Mexico":                    "Mexico",
    "Korea Republic":            "South Korea",
    "South Africa":              "South Africa",
    "Czechia":                   "Czechia",
    "Canada":                    "Canada",
    "Bosnia and Herzegovina":    "Bosnia-Herzegovina",
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
    "Türkiye":                   "Turkiye",
    "Turkey":                    "Turkiye",
    "Germany":                   "Germany",
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

# ── Match ID mapping: (home_team, away_team) → your tracker ID ───────────
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

# KO stage matches identified by API stage field
KO_STAGE_MAP = {
    "LAST_32":          "R32",
    "LAST_16":          "R16",
    "QUARTER_FINALS":   "QF",
    "SEMI_FINALS":      "SF",
    "FINAL":            "FINAL",
    "THIRD_PLACE":      "BRONZE",
}


def fetch_matches():
    req = urllib.request.Request(
        API_URL,
        headers={"X-Auth-Token": API_KEY}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def map_team(api_name):
    return TEAM_MAP.get(api_name, api_name)


def build_scores(data):
    scores = {}
    pen_scores = {}
    ko_counters = {stage: 1 for stage in KO_STAGE_MAP.values()}

    for m in data.get("matches", []):
        status = m.get("status", "")
        if status not in ("FINISHED", "IN_PLAY", "PAUSED"):
            continue

        full_time = m.get("score", {}).get("fullTime", {})
        home_score = full_time.get("home")
        away_score = full_time.get("away")
        if home_score is None or away_score is None:
            continue

        home_team = map_team(m.get("homeTeam", {}).get("name", ""))
        away_team = map_team(m.get("awayTeam", {}).get("name", ""))
        stage     = m.get("stage", "")

        # Group stage: look up match ID by team pair
        match_id = MATCH_MAP.get((home_team, away_team))

        # KO stage: assign sequential IDs
        if not match_id and stage in KO_STAGE_MAP:
            prefix = KO_STAGE_MAP[stage]
            if prefix in ("FINAL", "BRONZE"):
                match_id = prefix
            else:
                n = ko_counters[prefix]
                match_id = f"{prefix}_{n}"
                ko_counters[prefix] += 1

        if not match_id:
            print(f"  ⚠️  Unmatched: {home_team} vs {away_team} [{stage}]")
            continue

        scores[match_id] = {"h": home_score, "a": away_score}

        # Penalty shootout
        penalties = m.get("score", {}).get("penalties", {})
        ph = penalties.get("home")
        pa = penalties.get("away")
        if ph is not None and pa is not None:
            pen_scores[match_id] = {"h": ph, "a": pa}

    return scores, pen_scores


def main():
    if not API_KEY:
        print("❌ FOOTBALL_DATA_API_KEY not set")
        return 1

    print(f"[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}] Fetching WC2026 scores...")

    try:
        data = fetch_matches()
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

    print(f"✅ scores.json written — {len(scores)} results, {len(pen_scores)} penalty shootouts")
    return 0


if __name__ == "__main__":
    exit(main())

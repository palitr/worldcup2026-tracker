"""
update_scores.py
FIFA World Cup 2026 — Live Score Updater
Fetches results from worldcup26.ir (all tabs)
Fetches goal events from API-Football (More Stats tab only)
© 2026 Rajarshi Palit
"""

import json
import os
import time
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL    = "https://worldcup26.ir/get/games"
AF_API_URL = "https://v3.football.api-sports.io"
AF_LEAGUE  = 1
AF_SEASON  = 2026

# ── Team name mapping ─────────────────────────────────────────────────────
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
    "D.R. Congo":                "DR Congo",
    "Democratic Republic of Congo": "DR Congo",
    "Democratic Republic of the Congo": "DR Congo",
    "DRC":                       "DR Congo",
    "Uzbekistan":                "Uzbekistan",
    "Colombia":                  "Colombia",
    "England":                   "England",
    "Croatia":                   "Croatia",
    "Ghana":                     "Ghana",
    "Panama":                    "Panama",
}

# ── Group stage match ID mapping ──────────────────────────────────────────
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

# ── KO match UTC → tracker ID mapping (corrected times) ──────────────────
KO_UTC_MAP = {
    # Round of 32 (corrected)
    "2026-06-28T19:00:00Z": "R32_1",
    "2026-06-29T17:00:00Z": "R32_2",
    "2026-06-29T20:30:00Z": "R32_3",
    "2026-06-30T01:00:00Z": "R32_4",
    "2026-06-30T17:00:00Z": "R32_5",
    "2026-06-30T21:00:00Z": "R32_6",
    "2026-07-01T01:00:00Z": "R32_7",
    "2026-07-02T16:00:00Z": "R32_8",
    "2026-07-02T20:00:00Z": "R32_9",
    "2026-07-03T00:00:00Z": "R32_10",
    "2026-07-03T18:00:00Z": "R32_11",
    "2026-07-03T19:00:00Z": "R32_12",
    "2026-07-03T22:00:00Z": "R32_13",
    "2026-07-03T23:00:00Z": "R32_14",
    "2026-07-04T01:30:00Z": "R32_15",
    "2026-07-04T03:00:00Z": "R32_16",
    # Round of 16 (corrected)
    "2026-07-04T17:00:00Z": "R16_1",
    "2026-07-04T21:00:00Z": "R16_2",
    "2026-07-05T20:00:00Z": "R16_3",
    "2026-07-06T00:00:00Z": "R16_4",
    "2026-07-06T19:00:00Z": "R16_5",
    "2026-07-07T00:00:00Z": "R16_6",
    "2026-07-07T16:00:00Z": "R16_7",
    "2026-07-07T20:00:00Z": "R16_8",
    # Quarter Finals (corrected)
    "2026-07-09T19:00:00Z": "QF1",
    "2026-07-10T19:00:00Z": "QF2",
    "2026-07-11T21:00:00Z": "QF3",
    "2026-07-12T01:00:00Z": "QF4",
    # Semi Finals
    "2026-07-14T19:00:00Z": "SF1",
    "2026-07-15T19:00:00Z": "SF2",
    # Bronze & Final (corrected)
    "2026-07-18T21:00:00Z": "BRONZE",
    "2026-07-19T19:00:00Z": "FINAL",
}


def normalise_utc(s):
    """Handle multiple date formats from worldcup26.ir API"""
    if not s:
        return None
    s = s.strip()
    from datetime import datetime as _dt
    if '/' in s:
        try:
            dt = _dt.strptime(s, "%m/%d/%Y %H:%M")
            return dt.strftime("%Y-%m-%dT%H:%M:00Z")
        except Exception:
            pass
    s = s.replace(' ', 'T')
    if not s.endswith('Z'):
        s += 'Z'
    parts = s.rstrip('Z').split('T')
    if len(parts) == 2:
        time_part = parts[1]
        if time_part.count(':') == 1:
            s = parts[0] + 'T' + time_part + ':00Z'
    return s


def make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    if hasattr(ssl, 'OP_LEGACY_SERVER_CONNECT'):
        ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
    return ctx


def fetch_games(retries=3, delay=15):
    """Fetch from worldcup26.ir with SSL workaround."""
    last_error = None
    ssl_ctx = make_ssl_context()
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                API_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Connection": "close",
                }
            )
            with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            last_error = e
            print(f"  Attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                print(f"  Waiting {delay}s before retry...")
                time.sleep(delay)
    raise last_error


def fetch_af(path, params, api_key):
    """Fetch from API-Football v3."""
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{AF_API_URL}/{path}?{query}"
    req = urllib.request.Request(
        url,
        headers={
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "v3.football.api-sports.io",
        }
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def parse_scorers(raw):
    import re
    if not raw:
        return []
    s = str(raw).strip()
    if s.lower() in ('null', '{}', ''):
        return []
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
    if not s.strip():
        return []
    names = re.findall(r'"([^"]+)"', s)
    return [n.strip() for n in names if n.strip() and n.strip().lower() != 'null']


def map_team(name):
    if not name:
        return name
    return TEAM_MAP.get(name.strip(), name.strip())


def is_finished(m):
    finished = str(m.get("finished") or "").upper()
    elapsed  = str(m.get("time_elapsed") or "").lower().strip()
    if finished == "TRUE":
        return True
    if elapsed in ("finished", "ht", "live", "in_play",
                   "inplay", "in-play", "paused"):
        return True
    try:
        if int(elapsed) > 0:
            return True
    except (ValueError, TypeError):
        pass
    return False


def build_scores(data):
    scores = {}
    pen_scores = {}
    scorers = {}

    matches = data
    if isinstance(data, dict):
        matches = (data.get("games") or data.get("matches")
                   or data.get("data") or [])

    print(f"  Total matches from API: {len(matches)}")

    for m in matches:
        if not is_finished(m):
            continue

        home_raw = m.get("home_team_name_en") or ""
        away_raw = m.get("away_team_name_en") or ""

        try:
            home_score = int(m.get("home_score") or 0)
            away_score = int(m.get("away_score") or 0)
        except (ValueError, TypeError):
            continue

        home  = map_team(home_raw)
        away  = map_team(away_raw)
        mtype = str(m.get("type") or "").lower()

        match_id = MATCH_MAP.get((home, away))

        if not match_id and mtype.startswith("knockout"):
            utc_raw = (m.get("local_date") or m.get("utc") or
                       m.get("datetime") or "")
            utc_norm = normalise_utc(utc_raw)
            match_id = KO_UTC_MAP.get(utc_norm)
            if not match_id:
                print(f"  ⚠️  KO UTC not in map: {utc_norm} | {home} vs {away}")

        if not match_id:
            print(f"  ⚠️  Unmatched: {home} vs {away} [type={mtype}]")
            continue

        scores[match_id] = {"h": home_score, "a": away_score}

        h_scorers = parse_scorers(m.get("home_scorers"))
        a_scorers = parse_scorers(m.get("away_scorers"))
        if h_scorers or a_scorers:
            scorers[match_id] = {"h": h_scorers, "a": a_scorers}

        print(f"  ✅ {match_id}: {home} {home_score}–{away_score} {away}"
              + (f" | ⚽ {h_scorers}" if h_scorers else "")
              + (f" / {a_scorers}" if a_scorers else ""))

    return scores, pen_scores, scorers


def build_af_stats(api_key, existing_af):
    """
    Fetch goal events from API-Football for all completed WC2026 matches.
    Only fetches fixture IDs not already processed.
    Returns updated af_stats dict.
    """
    # Preserve existing data — only add new fixtures
    af = existing_af if existing_af else {
        "fetched_ids": [],
        "players": {},
        "total_og": 0,
        "total_pen": 0,
        "hat_tricks": 0,
    }

    try:
        # Step 1 — get all completed fixtures (1 API call)
        print("  [API-Football] Fetching completed fixtures...")
        resp = fetch_af("fixtures", {
            "league": AF_LEAGUE,
            "season": AF_SEASON,
            "status": "FT"
        }, api_key)

        all_fixtures = resp.get("response", [])
        fetched_ids  = set(af.get("fetched_ids", []))
        new_fixtures = [
            f for f in all_fixtures
            if f["fixture"]["id"] not in fetched_ids
        ]
        print(f"  [API-Football] {len(all_fixtures)} completed, "
              f"{len(new_fixtures)} new to fetch")

        if not new_fixtures:
            print("  [API-Football] No new fixtures — skipping")
            return af

        # Step 2 — fetch events for each new fixture (1 call each)
        for fix in new_fixtures:
            fid  = fix["fixture"]["id"]
            home = fix["teams"]["home"]["name"]
            away = fix["teams"]["away"]["name"]
            try:
                ev_resp = fetch_af("fixtures/events", {
                    "fixture": fid,
                    "type": "Goal"
                }, api_key)

                events = ev_resp.get("response", [])

                # Count goals per player in this match (for hat-trick detection)
                match_goals = {}

                for ev in events:
                    detail     = ev.get("detail", "")
                    player     = ev.get("player", {}).get("name", "")
                    team_name  = ev.get("team", {}).get("name", "")

                    # Skip missed penalties
                    if detail == "Missed Penalty":
                        continue

                    is_og  = (detail == "Own Goal")
                    is_pen = (detail == "Penalty")

                    if is_og:
                        af["total_og"] = af.get("total_og", 0) + 1
                        # OG credited to opposing team — skip player tally
                        continue

                    if not player:
                        continue

                    key = f"{player}|{team_name}"
                    if key not in af["players"]:
                        af["players"][key] = {
                            "name":  player,
                            "team":  team_name,
                            "goals": 0,
                            "pen":   0,
                            "npg":   0,
                            "mp":    0,
                        }

                    af["players"][key]["goals"] += 1
                    if is_pen:
                        af["players"][key]["pen"] += 1
                        af["total_pen"] = af.get("total_pen", 0) + 1
                    else:
                        af["players"][key]["npg"] += 1

                    # Track per-match goals for hat-trick detection
                    match_goals[key] = match_goals.get(key, 0) + 1

                # Update matches played for each scorer in this game
                for key in match_goals:
                    if key in af["players"]:
                        af["players"][key]["mp"] = \
                            af["players"][key].get("mp", 0) + 1
                    # Hat-trick check
                    if match_goals[key] >= 3:
                        af["hat_tricks"] = af.get("hat_tricks", 0) + 1

                af.setdefault("fetched_ids", [])
                af["fetched_ids"].append(fid)
                print(f"  [API-Football] ✅ {home} vs {away} "
                      f"({len(events)} goal events)")

                # Small delay to be respectful to the API
                time.sleep(0.5)

            except Exception as e:
                print(f"  [API-Football] ⚠️  Failed fixture {fid} "
                      f"({home} vs {away}): {e}")
                continue

    except Exception as e:
        print(f"  [API-Football] ⚠️  Failed: {e}")

    return af


def write_heartbeat(now):
    try:
        with open("heartbeat.json", "w") as f:
            json.dump({"updated": now}, f)
    except Exception as e:
        print(f"⚠️  heartbeat write failed: {e}")


def load_existing_scores():
    """Load existing scores.json to preserve af_stats across runs."""
    try:
        with open("scores.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00Z")
    print(f"[{now}] Fetching WC2026 scores from worldcup26.ir...")

    write_heartbeat(now)

    # ── Step 1: worldcup26.ir (primary source for all tabs) ──────────────
    try:
        data = fetch_games(retries=3, delay=15)
    except Exception as e:
        print(f"⚠️  API unavailable after 3 attempts: {e}")
        print("heartbeat.json written — scores unchanged, will retry next run")
        return 0

    scores, pen_scores, scorers = build_scores(data)

    # ── Step 2: API-Football (More Stats tab only) ────────────────────────
    api_key = os.environ.get("API_FOOTBALL_KEY", "")
    existing = load_existing_scores()
    existing_af = existing.get("af_stats", None)

    if api_key:
        print(f"[{now}] Fetching goal events from API-Football...")
        af_stats = build_af_stats(api_key, existing_af)
    else:
        print("  [API-Football] No API key found — skipping")
        af_stats = existing_af or {}

    # ── Write scores.json ─────────────────────────────────────────────────
    output = {
        "updated":   now,
        "scores":    scores,
        "penScores": pen_scores,
        "scorers":   scorers,
        "af_stats":  af_stats,
    }

    with open("scores.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ scores.json written — {len(scores)} results, "
          f"{len(af_stats.get('players', {}))} AF players")
    return 0


if __name__ == "__main__":
    exit(main())

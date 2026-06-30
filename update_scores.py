"""
update_scores.py
FIFA World Cup 2026 — Live Score Updater
Fetches results from worldcup26.ir
Maps KO matches by UTC datetime for reliable ID assignment
© 2026 Rajarshi Palit
"""

import json
import time
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL = "https://worldcup26.ir/get/games"

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

# ── KO match UTC → tracker ID mapping ────────────────────────────────────
# NOTE: worldcup26.ir sends local kickoff time (not UTC) in the datetime field.
# Each entry has BOTH the true UTC time AND the local time so matching works
# regardless of which the API returns.
KO_UTC_MAP = {
    # Round of 32 — UTC times
    "2026-06-28T19:00:00Z": "R32_1",
    "2026-06-29T17:00:00Z": "R32_2",
    "2026-06-29T20:30:00Z": "R32_3",
    "2026-06-30T01:00:00Z": "R32_4",
    "2026-06-30T17:00:00Z": "R32_5",
    "2026-06-30T21:00:00Z": "R32_6",
    "2026-07-01T01:00:00Z": "R32_7",
    "2026-07-01T16:00:00Z": "R32_8",
    "2026-07-01T20:00:00Z": "R32_9",
    "2026-07-02T00:00:00Z": "R32_10",
    "2026-07-03T18:00:00Z": "R32_11",
    "2026-07-02T19:00:00Z": "R32_12",
    "2026-07-03T22:00:00Z": "R32_13",
    "2026-07-02T23:00:00Z": "R32_14",
    "2026-07-04T01:30:00Z": "R32_15",
    "2026-07-03T03:00:00Z": "R32_16",
    # Round of 32 — local times (worldcup26.ir quirk)
    "2026-06-28T12:00:00Z": "R32_1",   # Los Angeles (UTC-7)
    "2026-06-29T12:00:00Z": "R32_2",   # Houston (UTC-5)
    "2026-06-29T16:30:00Z": "R32_3",   # Boston (UTC-4)
    "2026-06-29T19:00:00Z": "R32_4",   # Monterrey (UTC-6)
    "2026-06-30T12:00:00Z": "R32_5",   # Dallas (UTC-5)
    "2026-06-30T17:00:00Z": "R32_6",   # New York NJ (UTC-4)
    "2026-06-30T19:00:00Z": "R32_7",   # Mexico City (UTC-6)
    "2026-07-01T12:00:00Z": "R32_8",   # Atlanta (UTC-4)
    "2026-07-01T13:00:00Z": "R32_9",   # Seattle (UTC-7)
    "2026-07-01T17:00:00Z": "R32_10",  # SF Bay Area (UTC-7)
    "2026-07-03T13:00:00Z": "R32_11",  # Dallas (UTC-5)
    "2026-07-02T12:00:00Z": "R32_12",  # Los Angeles (UTC-7)
    "2026-07-03T18:00:00Z": "R32_13",  # Miami (UTC-4)
    "2026-07-02T19:00:00Z": "R32_14",  # Toronto (UTC-4)
    "2026-07-03T20:30:00Z": "R32_15",  # Kansas City (UTC-5)
    "2026-07-02T20:00:00Z": "R32_16",  # Vancouver (UTC-7)
    # Round of 16 — UTC times
    "2026-07-04T17:00:00Z": "R16_1",
    "2026-07-04T21:00:00Z": "R16_2",
    "2026-07-05T20:00:00Z": "R16_3",
    "2026-07-06T00:00:00Z": "R16_4",
    "2026-07-06T19:00:00Z": "R16_5",
    "2026-07-07T00:00:00Z": "R16_6",
    "2026-07-07T16:00:00Z": "R16_7",
    "2026-07-07T20:00:00Z": "R16_8",
    # Round of 16 — local times
    "2026-07-04T12:00:00Z": "R16_1",   # Houston (UTC-5)
    "2026-07-05T16:00:00Z": "R16_3",   # New York NJ (UTC-4)
    "2026-07-05T18:00:00Z": "R16_4",   # Mexico City (UTC-6)
    "2026-07-06T12:00:00Z": "R16_5",   # Los Angeles (UTC-7)
    "2026-07-06T17:00:00Z": "R16_6",   # Seattle (UTC-7)
    "2026-07-07T12:00:00Z": "R16_7",   # Atlanta (UTC-4)
    "2026-07-07T15:00:00Z": "R16_8",   # Dallas (UTC-5)
    # Quarter Finals — UTC times
    "2026-07-09T19:00:00Z": "QF1",
    "2026-07-10T19:00:00Z": "QF2",
    "2026-07-11T21:00:00Z": "QF3",
    "2026-07-12T01:00:00Z": "QF4",
    # Quarter Finals — local times
    "2026-07-09T15:00:00Z": "QF1",     # Boston (UTC-4)
    "2026-07-10T12:00:00Z": "QF2",     # Los Angeles (UTC-7)
    "2026-07-11T17:00:00Z": "QF3",     # Miami (UTC-4)
    "2026-07-11T20:00:00Z": "QF4",     # Kansas City (UTC-5)
    # Semi Finals — UTC times
    "2026-07-14T19:00:00Z": "SF1",
    "2026-07-15T19:00:00Z": "SF2",
    # Semi Finals — local times
    "2026-07-14T14:00:00Z": "SF1",     # Dallas (UTC-5)
    "2026-07-15T15:00:00Z": "SF2",     # Atlanta (UTC-4)
    # Final — UTC and local
    "2026-07-19T19:00:00Z": "FINAL",
    "2026-07-19T15:00:00Z": "FINAL",   # New York NJ (UTC-4)
    # Bronze
    "2026-07-18T21:00:00Z": "BRONZE",
    "2026-07-18T17:00:00Z": "BRONZE",
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
    """
    Create an SSL context that tolerates worldcup26.ir's broken SSL config.
    UNEXPECTED_EOF_WHILE_READING = server closes connection abruptly during
    handshake — disabling cert verification + using TLSv1.2 fallback fixes it.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Allow legacy renegotiation (common cause of EOF on cheap hosting)
    # hasattr guard for Python < 3.12 compatibility
    if hasattr(ssl, 'OP_LEGACY_SERVER_CONNECT'):
        ctx.options |= ssl.OP_LEGACY_SERVER_CONNECT
    return ctx


def fetch_games(retries=3, delay=15):
    """Fetch with SSL workaround and longer delay between retries."""
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


def parse_scorers(raw):
    """
    Parse the messy scorer string from worldcup26.ir API.
    Input:  '{"J. Quiñones 9\'","R. Jiménez 67\'"}'  or  'null'  or  None
    Output: ["J. Quiñones 9'", "R. Jiménez 67'"]    or  []
    """
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


def extract_penalty_scores(m):
    """
    Try several plausible field-name variants for penalty shootout scores,
    since the exact worldcup26.ir field name hasn't been confirmed yet.
    Returns (home_pens, away_pens) or (None, None) if not found.
    """
    home_keys = ["home_score_penalties", "home_penalties", "penalty_home",
                 "pen_home", "home_pen", "homePenalties", "home_pens"]
    away_keys = ["away_score_penalties", "away_penalties", "penalty_away",
                 "pen_away", "away_pen", "awayPenalties", "away_pens"]

    pen_h = None
    for k in home_keys:
        if m.get(k) is not None:
            pen_h = m.get(k)
            break

    pen_a = None
    for k in away_keys:
        if m.get(k) is not None:
            pen_a = m.get(k)
            break

    # Nested "penalties": {"home": x, "away": y} structure
    if pen_h is None or pen_a is None:
        nested = m.get("penalties")
        if isinstance(nested, dict):
            if pen_h is None:
                pen_h = nested.get("home")
            if pen_a is None:
                pen_a = nested.get("away")

    return pen_h, pen_a


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

        KO_TYPES = {"knockout", "r32", "r16", "qf", "quarterfinal", "sf", "semifinal", "final"}
        if not match_id and (mtype.startswith("knockout") or any(mtype.startswith(t) for t in KO_TYPES)):
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

        # ── Penalty shootout scores ──────────────────────────────────────
        pen_h_raw, pen_a_raw = extract_penalty_scores(m)

        if pen_h_raw is not None and pen_a_raw is not None:
            try:
                pen_scores[match_id] = {
                    "h": int(pen_h_raw),
                    "a": int(pen_a_raw)
                }
                print(f"     🥅 Penalties: {pen_h_raw}-{pen_a_raw}")
            except (ValueError, TypeError):
                pass
        elif home_score == away_score and mtype and not mtype.startswith("group"):
            # Knockout match finished level — penalties expected but not found.
            # Log raw match keys once so we can identify the correct field name.
            print(f"  ⚠️  {match_id}: KO match level ({home_score}-{away_score}) "
                  f"but no penalty data found. Raw keys: {sorted(m.keys())}")

        # Parse scorers
        h_scorers = parse_scorers(m.get("home_scorers"))
        a_scorers = parse_scorers(m.get("away_scorers"))
        if h_scorers or a_scorers:
            scorers[match_id] = {"h": h_scorers, "a": a_scorers}

        print(f"  ✅ {match_id}: {home} {home_score}–{away_score} {away}"
              + (f" | ⚽ {h_scorers}" if h_scorers else "")
              + (f" / {a_scorers}" if a_scorers else ""))

    return scores, pen_scores, scorers


def write_heartbeat(now):
    try:
        with open("heartbeat.json", "w") as f:
            json.dump({"updated": now}, f)
    except Exception as e:
        print(f"⚠️  heartbeat write failed: {e}")


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:00Z")
    print(f"[{now}] Fetching WC2026 scores from worldcup26.ir...")

    write_heartbeat(now)

    try:
        data = fetch_games(retries=3, delay=15)
    except Exception as e:
        print(f"⚠️  API unavailable after 3 attempts: {e}")
        print("heartbeat.json written — scores unchanged, will retry next run")
        return 0

    scores, pen_scores, scorers = build_scores(data)

    output = {
        "updated":   now,
        "scores":    scores,
        "penScores": pen_scores,
        "scorers":   scorers,
    }

    with open("scores.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ scores.json written — {len(scores)} results")
    return 0


if __name__ == "__main__":
    exit(main())

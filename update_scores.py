"""
update_scores.py
FIFA World Cup 2026 — Live Score Updater
Fetches results from worldcup26.ir (all tabs)
Fetches scorer/penalty data from openfootball (More Stats tab only)
© 2026 Rajarshi Palit
"""

import json
import time
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL = "https://worldcup26.ir/get/games"
OFB_URL = "https://raw.githubusercontent.com/openfootball/worldcup.json/master/2026/worldcup.json"

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


def fetch_openfootball():
    """Fetch WC2026 scorer data from openfootball/worldcup.json (no API key needed)."""
    req = urllib.request.Request(
        OFB_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def build_openfootball_stats(data):
    """
    Build More Stats from openfootball/worldcup.json.
    Extracts all analytics for the More Stats tab.
    """
    # ── Minute helpers ────────────────────────────────────────────────────
    def parse_min(s):
        """'67' → 67.0,  '45+2' → 45.02,  '90+4' → 90.04"""
        if not s:
            return 999.0
        s = str(s).strip()
        if '+' in s:
            parts = s.split('+', 1)
            try:
                return float(parts[0]) + float(parts[1]) * 0.01
            except (ValueError, IndexError):
                return 999.0
        try:
            return float(s)
        except ValueError:
            return 999.0

    def period(s):
        """Classify a goal minute string into a display bucket."""
        if not s:
            return None
        s = str(s).strip()
        if '+' in s:
            base = int(s.split('+')[0])
            return '45+' if base <= 45 else '90+'
        try:
            v = int(s)
        except ValueError:
            return None
        if v <= 15: return '0-15'
        if v <= 30: return '16-30'
        if v <= 45: return '31-45'
        if v <= 60: return '46-60'
        if v <= 75: return '61-75'
        return '76-90'

    # ── Accumulators ─────────────────────────────────────────────────────
    players          = {}
    total_pen        = 0
    total_og         = 0
    hat_tricks       = 0
    ht_goals         = 0
    sh_goals         = 0
    goals_by_period  = {
        '0-15':0, '16-30':0, '31-45':0, '45+':0,
        '46-60':0, '61-75':0, '76-90':0, '90+':0
    }
    all_goals_list   = []   # for fastest/latest
    comeback_wins    = []
    threw_leads      = []
    matchday_goals   = {}   # round_label → total goals
    scoreline_freq   = {}   # "h-a" → count
    group_goals      = {}   # group → {player_key → {name,team,goals}}
    player_dates     = {}   # player_key → [match dates scored in]
    team_match_dates = {}   # team → sorted [match dates]
    one_man_shows    = []

    matches = data.get("matches", [])

    # ── Pass 1: build per-team match date order ───────────────────────────
    for m in matches:
        if not m.get("score", {}).get("ft"):
            continue
        d = m.get("date", "")
        for t in [m.get("team1",""), m.get("team2","")]:
            if t not in team_match_dates:
                team_match_dates[t] = []
            if d and d not in team_match_dates[t]:
                team_match_dates[t].append(d)
    for t in team_match_dates:
        team_match_dates[t].sort()

    # ── Pass 2: main stats ────────────────────────────────────────────────
    for m in matches:
        score = m.get("score", {})
        ft    = score.get("ft")
        ht    = score.get("ht")
        if not ft:
            continue

        team1    = m.get("team1", "")
        team2    = m.get("team2", "")
        rnd      = m.get("round", "")
        grp      = m.get("group", "")
        date     = m.get("date", "")
        ft1, ft2 = ft[0], ft[1]

        # Half-time / second-half goals split
        if ht:
            ht1, ht2 = ht[0], ht[1]
            ht_goals += ht1 + ht2
            sh_goals += (ft1 - ht1) + (ft2 - ht2)

            # Comeback wins: losing at HT → drew/won at FT
            if ht1 < ht2 and ft1 >= ft2:
                comeback_wins.append({
                    "team": team1, "opponent": team2,
                    "ht": f"{ht1}-{ht2}", "ft": f"{ft1}-{ft2}",
                    "result": "won" if ft1 > ft2 else "drew"
                })
            if ht2 < ht1 and ft2 >= ft1:
                comeback_wins.append({
                    "team": team2, "opponent": team1,
                    "ht": f"{ht2}-{ht1}", "ft": f"{ft2}-{ft1}",
                    "result": "won" if ft2 > ft1 else "drew"
                })

            # Threw away leads: winning at HT → drew/lost at FT
            if ht1 > ht2 and ft1 <= ft2:
                threw_leads.append({
                    "team": team1, "opponent": team2,
                    "ht": f"{ht1}-{ht2}", "ft": f"{ft1}-{ft2}",
                    "outcome": "lost" if ft1 < ft2 else "drew"
                })
            if ht2 > ht1 and ft2 <= ft1:
                threw_leads.append({
                    "team": team2, "opponent": team1,
                    "ht": f"{ht2}-{ht1}", "ft": f"{ft2}-{ft1}",
                    "outcome": "lost" if ft2 < ft1 else "drew"
                })

        # Matchday goals
        if rnd:
            matchday_goals[rnd] = matchday_goals.get(rnd, 0) + ft1 + ft2

        # Scoreline frequency (always larger score first)
        hi, lo = max(ft1,ft2), min(ft1,ft2)
        sl = f"{hi}-{lo}"
        scoreline_freq[sl] = scoreline_freq.get(sl, 0) + 1

        # Init group bucket
        if grp and grp not in group_goals:
            group_goals[grp] = {}

        # ── Per-side goal processing ──────────────────────────────────────
        match_goals = {}   # player_key → goals in this match (hat-trick)

        for side_goals, team, opponent in [
            (m.get("goals1") or [], team1, team2),
            (m.get("goals2") or [], team2, team1),
        ]:
            side_scorer_goals = {}  # player_key → goals for this side (one-man show)

            for goal in side_goals:
                name   = (goal.get("name") or "").strip()
                is_pen = bool(goal.get("penalty"))
                is_og  = bool(goal.get("owngoal"))
                minute = goal.get("minute", "")

                if is_og:
                    total_og += 1
                    continue

                if not name:
                    continue

                if is_pen:
                    total_pen += 1

                key = f"{name}|{team}"
                if key not in players:
                    players[key] = {
                        "name": name, "team": team,
                        "goals": 0, "pen": 0, "npg": 0, "mp": 0,
                    }

                players[key]["goals"] += 1
                if is_pen:
                    players[key]["pen"] += 1
                else:
                    players[key]["npg"] += 1

                match_goals[key]       = match_goals.get(key, 0) + 1
                side_scorer_goals[key] = side_scorer_goals.get(key, 0) + 1

                # Time period bucket
                p = period(minute)
                if p:
                    goals_by_period[p] += 1

                # All goals (for fastest/latest)
                sv = parse_min(minute)
                all_goals_list.append({
                    "player": name, "team": team,
                    "minute": str(minute), "sort_val": sv,
                    "opponent": opponent
                })

                # Group top scorers
                if grp:
                    if key not in group_goals[grp]:
                        group_goals[grp][key] = {
                            "name": name, "team": team, "goals": 0
                        }
                    group_goals[grp][key]["goals"] += 1

                # Scoring streaks: track match dates per player
                if key not in player_dates:
                    player_dates[key] = []
                if date and date not in player_dates[key]:
                    player_dates[key].append(date)

            # One-man show: one player scored ALL goals in a win
            team_ft  = ft1 if team == team1 else ft2
            opp_ft   = ft2 if team == team1 else ft1
            if team_ft > opp_ft and len(side_scorer_goals) == 1:
                sk    = list(side_scorer_goals.keys())[0]
                sg    = side_scorer_goals[sk]
                if sg == team_ft:
                    one_man_shows.append({
                        "player": players[sk]["name"], "team": team,
                        "goals": sg, "opponent": opponent,
                        "score": f"{team_ft}-{opp_ft}"
                    })

        # Hat-tricks + matches played
        for key, count in match_goals.items():
            if key in players:
                players[key]["mp"] += 1
            if count >= 3:
                hat_tricks += 1

    # ── Scoring streaks ───────────────────────────────────────────────────
    scoring_streaks = []
    for key, dates in player_dates.items():
        if key not in players:
            continue
        p    = players[key]
        tmd  = team_match_dates.get(p["team"], [])
        idxs = sorted({tmd.index(d) for d in dates if d in tmd})
        if len(idxs) < 2:
            continue
        max_s, cur = 1, 1
        for i in range(1, len(idxs)):
            if idxs[i] == idxs[i-1] + 1:
                cur += 1
                max_s = max(max_s, cur)
            else:
                cur = 1
        if max_s >= 2:
            scoring_streaks.append({
                "name": p["name"], "team": p["team"],
                "streak": max_s, "goals": p["goals"]
            })
    scoring_streaks.sort(key=lambda x: (-x["streak"], -x["goals"]))

    # ── Fastest / Latest goals ────────────────────────────────────────────
    valid = [g for g in all_goals_list if g["sort_val"] < 999]
    valid.sort(key=lambda g: g["sort_val"])
    fastest_goals = valid[:5]
    late_goals    = sorted(
        [g for g in valid if g["sort_val"] >= 90],
        key=lambda g: -g["sort_val"]
    )[:10]

    # ── Matchday goals: sorted list ───────────────────────────────────────
    import re as _re
    def md_sort(rnd):
        m2 = _re.search(r'\d+', rnd)
        return int(m2.group()) if m2 else 999
    matchday_goals_list = [
        {"round": r, "goals": g}
        for r, g in sorted(matchday_goals.items(), key=lambda x: md_sort(x[0]))
    ]

    # ── Scoreline frequency: top 10 ───────────────────────────────────────
    scoreline_list = sorted(
        [{"score": k, "count": v} for k, v in scoreline_freq.items()],
        key=lambda x: -x["count"]
    )[:10]

    # ── Group top scorers ─────────────────────────────────────────────────
    group_top = {}
    for grp, sd in group_goals.items():
        if not sd:
            continue
        top = max(sd.values(), key=lambda x: x["goals"])
        group_top[grp.replace("Group ", "")] = top

    print(f"  [openfootball] {len(players)} scorers, "
          f"{total_pen} pen, {total_og} OG, {hat_tricks} HT, "
          f"{len(comeback_wins)} comebacks, {len(one_man_shows)} one-man shows")

    return {
        "players":           players,
        "total_pen":         total_pen,
        "total_og":          total_og,
        "hat_tricks":        hat_tricks,
        "goals_by_period":   goals_by_period,
        "ht_goals":          ht_goals,
        "sh_goals":          sh_goals,
        "comeback_wins":     comeback_wins,
        "threw_leads":       threw_leads,
        "late_goals":        late_goals,
        "fastest_goals":     fastest_goals,
        "scoring_streaks":   scoring_streaks,
        "one_man_shows":     one_man_shows,
        "matchday_goals":    matchday_goals_list,
        "scoreline_freq":    scoreline_list,
        "group_top_scorers": group_top,
    }


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

        # Try reversed order — some sources swap home/away
        if not match_id:
            rev_id = MATCH_MAP.get((away, home))
            if rev_id:
                match_id = rev_id
                home_score, away_score = away_score, home_score

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

    # ── Step 1: worldcup26.ir (primary source for all tabs) ──────────────
    try:
        data = fetch_games(retries=3, delay=15)
    except Exception as e:
        print(f"⚠️  API unavailable after 3 attempts: {e}")
        print("heartbeat.json written — scores unchanged, will retry next run")
        return 0

    scores, pen_scores, scorers = build_scores(data)

    # ── Step 2: openfootball (More Stats tab — free, no API key) ─────────
    af_stats = {}
    try:
        print(f"[{now}] Fetching scorer data from openfootball...")
        ofb_data = fetch_openfootball()
        af_stats = build_openfootball_stats(ofb_data)
    except Exception as e:
        print(f"  [openfootball] ⚠️  Failed: {e}")

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
          f"{len(af_stats.get('players', {}))} OFB scorers")
    return 0


if __name__ == "__main__":
    exit(main())

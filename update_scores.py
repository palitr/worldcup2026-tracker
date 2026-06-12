"""
update_scores.py
FIFA World Cup 2026 — Live Score Updater
Fetches results from worldcup26.ir
© 2026 Rajarshi Palit
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timezone

API_URL = "https://worldcup26.ir/get/games"

TEAM_MAP = {
    "Mexico":                    "Mexico",
    "South Africa":              "South Africa",
    "South Korea":               "South Korea",
    "Korea Republic":            "South Korea",
    "Czechia":                   "Czechia",
    "Czech Republic":            "Czechia",
    "Canada":                    "Canada",
    "Bosnia and Herzegovina":    "Bosnia-Herzegovina",
    "Bosnia & Herzegovina":      "Bosnia-H

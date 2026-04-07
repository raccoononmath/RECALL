#!/usr/bin/env python3
"""
CPSC Recall Fetcher (v2 - uses curl for reliability on Mac)
Pulls recall data from the CPSC SaferProducts.gov REST API.
Saves raw JSON data to /data directory for the site generator.

API: https://www.saferproducts.gov/RestWebServices/Recall
No API key required. Free. Public data.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# --- Config ---
API_BASE = "https://www.saferproducts.gov/RestWebServices/Recall"
DATA_DIR = Path(__file__).parent.parent / "data"

PARENT_KEYWORDS = [
    "baby", "infant", "child", "children", "kid", "toddler", "newborn",
    "nursery", "crib", "stroller", "car seat", "high chair", "playpen",
    "play yard", "bassinet", "cradle", "pacifier", "teether", "bottle",
    "sippy", "diaper", "formula", "breast pump", "nursing", "swaddle",
    "toy", "rattle", "bouncer", "swing", "walker", "gate", "monitor",
    "carrier", "sling", "wrap", "onesie", "romper", "pajama", "sleepwear",
    "booster", "thermometer", "humidifier", "bath tub", "bath seat",
]

CATEGORY_MAP = {
    "cribs-cradles":    ["crib", "cradle", "bassinet"],
    "strollers":        ["stroller", "carriage", "buggy"],
    "car-seats":        ["car seat", "carseat", "booster seat", "infant seat"],
    "toys":             ["toy", "rattle", "doll", "game", "puzzle", "playset"],
    "clothing":         ["clothing", "pajama", "sleepwear", "onesie", "romper", "garment"],
    "high-chairs":      ["high chair", "highchair", "feeding chair"],
    "play-yards":       ["playpen", "play yard", "playard", "pack n play"],
    "baby-carriers":    ["carrier", "sling", "wrap"],
    "swings-bouncers":  ["swing", "bouncer", "rocker"],
    "baby-gates":       ["gate", "safety gate", "baby gate"],
    "furniture":        ["dresser", "changing table", "bookshelf", "shelf", "furniture"],
    "monitors":         ["monitor", "baby cam"],
    "feeding":          ["bottle", "sippy", "pacifier", "teether", "bib", "formula", "breast pump"],
    "bath":             ["bath", "tub"],
}


def fetch_with_curl(start_date: str, end_date: str) -> list:
    """Use curl to fetch recalls — more reliable than urllib on Mac."""
    url = f"{API_BASE}?format=json&RecallDateStart={start_date}&RecallDateEnd={end_date}"
    print(f"  Fetching {start_date} → {end_date}", end=" ", flush=True)

    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "30", "-H", "User-Agent: ParentRecallWatch/1.0", url],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode != 0:
            print(f"curl error {result.returncode}")
            return []
        if not result.stdout.strip():
            print("(empty)")
            return []
        data = json.loads(result.stdout)
        print(f"→ {len(data)} recalls")
        return data if isinstance(data, list) else []
    except subprocess.TimeoutExpired:
        print("(timeout)")
        return []
    except json.JSONDecodeError:
        print("(bad JSON)")
        return []
    except Exception as e:
        print(f"(error: {e})")
        return []


def is_parent_relevant(recall: dict) -> bool:
    text = ""
    for p in recall.get("Products", []):
        text += f" {p.get('Type','')} {p.get('Name','')} {p.get('Description','')}".lower()
    text += f" {recall.get('Title','')} {recall.get('Description','')}".lower()
    return any(kw in text for kw in PARENT_KEYWORDS)


def categorize(recall: dict) -> str:
    text = ""
    for p in recall.get("Products", []):
        text += f" {p.get('Type','')} {p.get('Name','')} {p.get('Description','')}".lower()
    text += f" {recall.get('Title','')}".lower()
    for slug, keywords in CATEGORY_MAP.items():
        if any(kw in text for kw in keywords):
            return slug
    return "other"


def load_existing(data_file: Path) -> dict:
    if data_file.exists():
        with open(data_file) as f:
            recalls = json.load(f)
            return {r["RecallNumber"]: r for r in recalls}
    return {}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "recent"
    print(f"\n=== CPSC Recall Fetcher — {mode} mode ===\n")

    if mode == "full":
        # 5 years, month by month
        date_ranges = []
        now = datetime.now()
        for i in range(60):
            d = now - timedelta(days=i * 30)
            start = d.replace(day=1).strftime("%Y-%m-%d")
            if d.month == 12:
                end = d.replace(year=d.year+1, month=1, day=1) - timedelta(days=1)
            else:
                end = d.replace(month=d.month+1, day=1) - timedelta(days=1)
            date_ranges.append((start, end.strftime("%Y-%m-%d")))
    else:
        # Just last 60 days — one call
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        date_ranges = [(start, end)]

    raw = []
    for start, end in date_ranges:
        raw.extend(fetch_with_curl(start, end))

    print(f"\nRaw recalls fetched: {len(raw)}")

    # Filter + categorize
    relevant = []
    for r in raw:
        if is_parent_relevant(r):
            r["_category"] = categorize(r)
            relevant.append(r)

    print(f"Parent-relevant: {len(relevant)}")

    # Merge with existing (so daily runs don't lose old data)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data_file = DATA_DIR / "recalls.json"
    existing = load_existing(data_file)
    for r in relevant:
        existing[r["RecallNumber"]] = r

    all_recalls = sorted(existing.values(), key=lambda r: r.get("RecallDate",""), reverse=True)

    with open(data_file, "w") as f:
        json.dump(list(all_recalls), f, indent=2, default=str)

    print(f"Saved {len(all_recalls)} total recalls → {data_file}")
    print("\nDone! Now run: python3 scripts/generate_site.py")


if __name__ == "__main__":
    main()

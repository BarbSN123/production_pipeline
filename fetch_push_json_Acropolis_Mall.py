#!/usr/bin/env python3
import os
import json
import time
import subprocess
import requests
from datetime import datetime, timedelta

# ========== CONFIG ==========
URL = "https://www.barbequenation.com/api/v1/menu-buffet-price"
HEADERS = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}


branches_config = {
  "224":{
        "name":"Acropolis Mall, East Kolkata Township",
        "slots":{
            "12:00:00": 1654, "12:30:00": 1654, "13:00:00": 1654,
            "13:30:00": 1654, "14:00:00": 1654, "14:30:00": 1655,
            "15:00:00": 1655, "15:30:00": 1655, "16:00:00": 1655,
            "16:30:00": 1655, "17:00:00": 1655, "17:30:00": 1655,
            "18:00:00": 1655, "18:30:00": 1656, "19:00:00": 1656,
            "19:30:00": 1656, "20:00:00": 1656, "20:30:00": 1656,
            "21:00:00": 1657, "21:30:00": 1657, "22:00:00": 1657,
            "22:30:00": 1657
        }
    }
}

# Local paths
OUT_DIR = "json"

# GitHub config
REPO_URL = "https://github.com/diyanshu-anand/bbq-data.git"   #  repo
BRANCH_NAME = "main"

# Fetch settings
REQUEST_TIMEOUT = 12
SLOT_DELAY = 0.6
BRANCH_DELAY = 2.0
RETRIES = 4
RETRY_BASE_DELAY = 2.0
# DAYS_TO_FETCH = 15



# ========== NETWORK HELPERS ==========
def safe_post(payload, retries=RETRIES, base_delay=RETRY_BASE_DELAY):
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(URL, json=payload, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                try:
                    return r.json()
                except ValueError:
                    print(f"⚠️ JSON decode error attempt {attempt}: {r.text[:200]}")
            else:
                print(f"⚠️ Attempt {attempt}: HTTP {r.status_code} - {r.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Attempt {attempt}: {e}")

        sleep_time = base_delay * attempt
        print(f"  → Retrying in {sleep_time:.1f}s...")
        time.sleep(sleep_time)
    return None

# ========== FETCH FUNCTION ==========
def fetch_day_slots(date_obj):
    """Fetches all slots for a specific date across all branches."""
    date_str = date_obj.strftime("%Y-%m-%d")
    day_records = []

    for idx, (branch_id, branch_info) in enumerate(branches_config.items(), start=1):
        branch_name = branch_info["name"]
        slot_map = branch_info["slots"]

        print(f"\n🏢 [{idx}/{len(branches_config)}] {branch_name} ({branch_id}) — {date_str}")

        for time_str, slot_id in slot_map.items():
            print(f"  • {branch_name} @ {time_str}")
            payload = {
                "branch_id": str(branch_id),
                "reservation_date": date_str,
                "reservation_time": time_str,
                "slot_id": slot_id
            }

            data = safe_post(payload)
            if not data:
                day_records.append({
                    "Branch": branch_name, "Branch ID": branch_id,
                    "Date": date_str, "Slot Time": time_str,
                    "Error": "Failed to fetch"
                })
                continue

            buffets = (
                data.get("results", {})
                    .get("buffets", {})
                    .get("buffet_data", [])
                    or []
            )

            if not buffets:
                day_records.append({
                    "Branch": branch_name, "Branch ID": branch_id,
                    "Date": date_str, "Slot Time": time_str,
                    "Error": "No buffet data"
                })
            else:
                for b in buffets:
                    day_records.append({
                        "Branch": branch_name,
                        "Branch ID": branch_id,
                        "Date": date_str,
                        "Slot Time": time_str,
                        "Period": b.get("period", {}).get("periodName", ""),
                        "Customer Type": b.get("customerType", ""),
                        "Food Type": b.get("foodType", ""),
                        "Plan": b.get("displayName", ""),
                        "Price": b.get("totalAmount", ""),
                        "Original Price": b.get("originalPrice", "")
                    })

            time.sleep(SLOT_DELAY)
        time.sleep(BRANCH_DELAY)

    return day_records


# ========== SAVE FUNCTION ==========
def save_day_json(records, date_obj):
    """Save a single day’s data to /json/YYYY-MM-DD.json"""
    os.makedirs(OUT_DIR, exist_ok=True)
    date_str = date_obj.strftime("%Y-%m-%d")
    run_id = os.getenv("GITHUB_RUN_ID", str(int(time.time())))
    job_id = os.getenv("GITHUB_RUN_ATTEMPT", "1")

    
    out_path = os.path.join(OUT_DIR, f"Acropolis_Mall_{date_str}_{run_id}_{job_id}.json")
    # out_path = os.path.join(OUT_DIR, f"Acropolis_Mall_{date_str}.json")

    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "records": records
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(records)} records → {out_path}")
    return out_path


# ========== MAIN RUN ==========
if __name__ == "__main__":
    print(f"🕒 Starting 30-day buffet data fetch + push...")

    # start_date = datetime.now()
    # for d in range(DAYS_TO_FETCH):
    #     date_obj = start_date + timedelta(days=d)
    #     print(f"\n📅 === Fetching {date_obj.strftime('%Y-%m-%d')} ===")
    #     records = fetch_day_slots(date_obj)
    #     save_day_json(records, date_obj)
    
    
    start_date = datetime.strptime(os.getenv("START_DATE"), "%Y-%m-%d")
    end_date = datetime.strptime(os.getenv("END_DATE"), "%Y-%m-%d")
    
    current_date = start_date
    
    while current_date <= end_date:
        print(f"\n📅 === Fetching {current_date.strftime('%Y-%m-%d')} ===")
    
        records = fetch_day_slots(current_date)
        save_day_json(records, current_date)
    
        current_date += timedelta(days=1)
    
        # print("\n🎉 All done — 30-day data saved and pushed successfully!")
        print("\n🎉 Incremental fetch complete!")

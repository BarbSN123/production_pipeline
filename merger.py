#!/usr/bin/env python3

import os
import json
from datetime import datetime

OUT_DIR = "json"
SPLIT_COUNT = 3   # number of output files


def get_valid_dates():
    """
    Get allowed date range from ENV (same as scraper)
    """
    start = os.getenv("START_DATE")
    end = os.getenv("END_DATE")

    if not start or not end:
        # fallback to today only
        today = datetime.now().strftime("%Y-%m-%d")
        return {today}

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    valid_dates = set()
    current = start_date

    while current <= end_date:
        valid_dates.add(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return valid_dates


def merge_all_jsons(out_dir=OUT_DIR):

    print("\n🧩 Starting JSON merge process")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print("📁 Created json directory")

    # 🔥 GET VALID DATES
    valid_dates = get_valid_dates()
    print(f"📅 Valid dates for merge: {valid_dates}")

    all_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "records": []
    }

    # 🔥 FILTER FILES BASED ON DATE
    json_files = sorted([
        f for f in os.listdir(out_dir)
        if f.endswith(".json")
        and not f.startswith("buffet_data")
        and any(date in f for date in valid_dates)   # ✅ KEY FIX
    ])

    if not json_files:
        print("⚠️ No valid JSON files found for current run.")
        return False

    print(f"\n📂 Found {len(json_files)} valid JSON files")

    for fname in json_files:

        path = os.path.join(out_dir, fname)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

                if "records" in data:
                    all_data["records"].extend(data["records"])
                    print(f"✅ {fname} merged ({len(data['records'])} records)")
                else:
                    print(f"⚠️ {fname} has no 'records' key")

        except Exception as e:
            print(f"❌ Skipped {fname}: {e}")

    total_records = len(all_data["records"])

    print(f"\n📦 Total records merged: {total_records}")

    if total_records == 0:
        print("⚠️ No records available to split")
        return False

    # 🔥 SPLITTING
    chunk_size = (total_records + SPLIT_COUNT - 1) // SPLIT_COUNT

    print(f"✂️ Splitting into {SPLIT_COUNT} files")

    for i in range(SPLIT_COUNT):

        chunk = all_data["records"][i * chunk_size:(i + 1) * chunk_size]

        out_path = os.path.join(out_dir, f"buffet_data_{i+1}.json")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "generated_at": all_data["generated_at"],
                    "records": chunk
                },
                f,
                indent=2,
                ensure_ascii=False
            )

        size_kb = os.path.getsize(out_path) / 1024

        print(f"📁 buffet_data_{i+1}.json created — {len(chunk)} records ({size_kb:.1f} KB)")

    print("\n✅ Merge and split completed successfully")

    return True


if __name__ == "__main__":
    from datetime import timedelta  # needed for date loop
    merge_all_jsons()

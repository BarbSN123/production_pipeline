#!/usr/bin/env python3

import os
import json
from datetime import datetime, timedelta
import re

OUT_DIR = "json"
SPLIT_COUNT = 3


# =========================
# GET VALID DATES
# =========================
def get_valid_dates():
    start = os.getenv("START_DATE")
    end = os.getenv("END_DATE")

    if not start or not end:
        raise ValueError("❌ START_DATE or END_DATE not set in merger job")

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    valid_dates = set()
    current = start_date

    while current <= end_date:
        valid_dates.add(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return valid_dates


# =========================
# EXTRACT DATE FROM RECORD
# =========================
def extract_date(record):
    return (
        record.get("Date")
        or record.get("date")
        or record.get("booking_date")
        or record.get("day")
    )


# =========================
# SAFE JSON LOAD
# =========================
def safe_load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Skipping corrupted file: {path} ({e})")
        return None


# =========================
# MERGE FUNCTION
# =========================
def merge_all_jsons(out_dir=OUT_DIR):

    print("\n🧩 Starting JSON merge process")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    valid_dates = get_valid_dates()
    print(f"📅 Valid dates: {sorted(valid_dates)}")

    all_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "records": []
    }

    seen = set()

    # ✅ ONLY PICK FILES RELEVANT TO VALID DATES
    json_files = []
    for f in os.listdir(out_dir):
        if not f.endswith(".json"):
            continue
        if f.startswith("buffet_data"):
            continue
        if any(date in f for date in valid_dates):
            json_files.append(f)

    json_files.sort()

    if not json_files:
        print("⚠️ No JSON files found")
        return False

    print(f"\n📂 Found {len(json_files)} relevant JSON files")

    for fname in json_files:
        path = os.path.join(out_dir, fname)

        data = safe_load_json(path)
        if not data:
            continue

        if "records" not in data:
            print(f"⚠️ {fname} missing 'records'")
            continue

        valid_count = 0

        for r in data["records"]:

            rec_date = extract_date(r)

            if not rec_date:
                continue

            # ✅ FIXED DATE NORMALIZATION
            rec_date = str(rec_date).strip()[:10]

            if rec_date not in valid_dates:
                continue

            unique_key = (
                r.get("Branch"),
                rec_date,
                r.get("Slot Time"),
                r.get("Food Type"),
                r.get("Plan")
            )

            if unique_key in seen:
                continue

            seen.add(unique_key)
            all_data["records"].append(r)
            valid_count += 1

        print(f"✅ {fname}: {valid_count} valid records")

    total_records = len(all_data["records"])
    print(f"\n📦 Total filtered records: {total_records}")

    if total_records == 0:
        print("⚠️ No valid records after filtering")
        return False

    # =========================
    # SPLIT OUTPUT
    # =========================
    chunk_size = (total_records + SPLIT_COUNT - 1) // SPLIT_COUNT

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
        print(f"📁 buffet_data_{i+1}.json → {len(chunk)} records ({size_kb:.1f} KB)")

    print("\n✅ Merge completed successfully")
    return True


# =========================
# CLEANUP FUNCTION
# =========================
def cleanup_old_files(out_dir=OUT_DIR, keep_days=15):

    print("\n🧹 Running date-based cleanup...")

    # ✅ USE START_DATE INSTEAD OF SYSTEM TIME
    start = os.getenv("START_DATE")
    today = datetime.strptime(start, "%Y-%m-%d").date()
    max_date = today + timedelta(days=keep_days)

    for fname in os.listdir(out_dir):

        if not fname.endswith(".json"):
            continue

        if fname.startswith("buffet_data"):
            continue

        try:
            # ✅ REGEX DATE EXTRACTION (WORKS FOR ALL FILENAMES)
            match = re.search(r"\d{4}-\d{2}-\d{2}", fname)

            if not match:
                print(f"⚠️ No date found in {fname}")
                continue

            date_str = match.group()
            file_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            if file_date < today:
                os.remove(os.path.join(out_dir, fname))
                print(f"🗑️ Deleted old file: {fname}")

            elif file_date > max_date:
                os.remove(os.path.join(out_dir, fname))
                print(f"🗑️ Deleted future overflow: {fname}")

        except Exception as e:
            print(f"⚠️ Skipping {fname}: {e}")


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    success = merge_all_jsons()

    if success:
        cleanup_old_files()

#!/usr/bin/env python3

import os
import json
from datetime import datetime, timedelta

OUT_DIR = "json"
SPLIT_COUNT = 3


def get_valid_dates():
    """
    STRICT: Must have ENV vars, otherwise fail
    """
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

    json_files = sorted([
        f for f in os.listdir(out_dir)
        if f.endswith(".json")
        and not f.startswith("buffet_data")
    ])

    if not json_files:
        print("⚠️ No JSON files found")
        return False

    print(f"\n📂 Found {len(json_files)} JSON files")

    for fname in json_files:

        path = os.path.join(out_dir, fname)

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

                if "records" not in data:
                    print(f"⚠️ {fname} missing 'records'")
                    continue

                # 🔥 FILTER RECORDS BY DATE (NOT FILE NAME)
                filtered = [
                    r for r in data["records"]
                    if str(r.get("date")) in valid_dates
                ]

                all_data["records"].extend(filtered)

                print(f"✅ {fname}: {len(filtered)} valid records")

        except Exception as e:
            print(f"❌ Error in {fname}: {e}")

    total_records = len(all_data["records"])
    print(f"\n📦 Total filtered records: {total_records}")

    if total_records == 0:
        print("⚠️ No valid records after filtering")
        return False

    # 🔥 SPLIT
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

        print(f"📁 buffet_data_{i+1}.json → {len(chunk)} records")

    print("\n✅ Merge completed successfully")
    return True


if __name__ == "__main__":
    merge_all_jsons()

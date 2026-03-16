# Final Workflow of merger has to be run in job 6 after all the task is done !!
#!/usr/bin/env python3

import os
import json
from datetime import datetime

OUT_DIR = "json"
MASTER_FILE = "buffet_data.json"
SPLIT_COUNT = 3   # number of output files


def merge_all_jsons(out_dir=OUT_DIR):

    print("\n🧩 Starting JSON merge process")

    # ensure json directory exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print("📁 Created json directory")

    all_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "records": []
    }

    # collect json files
    json_files = sorted([
        f for f in os.listdir(out_dir)
        if f.endswith(".json") and not f.startswith("buffet_data")
    ])

    if not json_files:
        print("⚠️ No branch JSON files found.")
        return False

    print(f"\n📂 Found {len(json_files)} branch JSON files")

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

    # splitting
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
    merge_all_jsons()
import json
import os
from datetime import datetime


# =========================================================
# CONFIGURATION
# =========================================================

JSON_FILES = [
    "json/buffet_data_1.json",
    "json/buffet_data_2.json",
    "json/buffet_data_3.json",
]

SNAPSHOT_FILE = "alerts/previous_snapshot.json"
ALERT_FILE = "alerts/alerts.json"


# =========================================================
# RECORD IDENTITY
# =========================================================
#
# These fields together identify one buffet record.
#
# If Price changes, it is still the SAME record.
#
# =========================================================

IDENTITY_FIELDS = [
    "Branch",
    "Date",
    "Slot Time",
    "Customer Type",
    "Food Type",
    "Plan",
]


# =========================================================
# IMPORTANT CHANGE FIELDS
# =========================================================

PRICE_FIELDS = [
    "Price",
    "Original Price",
]

OTHER_FIELDS = [
    "Period",
]


# =========================================================
# LOAD CURRENT JSON
# =========================================================

def load_current_dataset():

    all_records = []

    for path in JSON_FILES:

        if not os.path.exists(path):

            print(f"⚠️ Missing file: {path}")
            continue

        try:

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        except Exception as e:

            print(f"❌ Could not read {path}: {e}")
            continue

        records = data.get("records", [])

        if not isinstance(records, list):

            print(f"⚠️ Invalid records in {path}")
            continue

        all_records.extend(records)

    return all_records


# =========================================================
# LOAD PREVIOUS SNAPSHOT
# =========================================================

def load_previous_snapshot():

    if not os.path.exists(SNAPSHOT_FILE):

        print("\nℹ️ No previous snapshot found.")
        print("   This is the first alert run.")

        return None

    try:

        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        records = data.get("records", [])

        if not isinstance(records, list):

            print("⚠️ Previous snapshot is invalid.")

            return None

        return records

    except Exception as e:

        print(f"❌ Could not read previous snapshot: {e}")

        return None


# =========================================================
# SAVE CURRENT DATA AS SNAPSHOT
# =========================================================

def save_snapshot(records):

    os.makedirs(
        os.path.dirname(SNAPSHOT_FILE),
        exist_ok=True
    )

    data = {
        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "records": records
    }

    with open(
        SNAPSHOT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\n💾 Previous snapshot updated "
        f"({len(records)} records)"
    )


# =========================================================
# CREATE UNIQUE KEY
# =========================================================

def make_key(record):

    return tuple(
        record.get(field)
        for field in IDENTITY_FIELDS
    )


# =========================================================
# CREATE INDEX
# =========================================================

def create_index(records):

    indexed = {}

    for record in records:

        key = make_key(record)

        if key in indexed:

            continue

        indexed[key] = record

    return indexed


# =========================================================
# RECORD INFORMATION FOR ALERT
# =========================================================

def record_info(record):

    return {
        "Branch": record.get("Branch"),
        "Branch ID": record.get("Branch ID"),
        "Date": record.get("Date"),
        "Slot Time": record.get("Slot Time"),
        "Period": record.get("Period"),
        "Customer Type": record.get("Customer Type"),
        "Food Type": record.get("Food Type"),
        "Plan": record.get("Plan"),
        "Price": record.get("Price"),
        "Original Price": record.get("Original Price"),
    }


# =========================================================
# COMPARE DATA
# =========================================================

def compare_data(previous_records, current_records):

    previous = create_index(previous_records)
    current = create_index(current_records)

    changes = []

    # =====================================================
    # NEW + MODIFIED
    # =====================================================

    for key, current_record in current.items():

        # -------------------------------------------------
        # NEW RECORD
        # -------------------------------------------------

        if key not in previous:

            changes.append({
                "type": "NEW",
                "record": record_info(current_record)
            })

            continue

        previous_record = previous[key]

        # -------------------------------------------------
        # PRICE CHANGES
        # -------------------------------------------------

        price_changes = {}

        for field in PRICE_FIELDS:

            old_value = previous_record.get(field)
            new_value = current_record.get(field)

            if old_value != new_value:

                price_changes[field] = {
                    "old": old_value,
                    "new": new_value
                }

        if price_changes:

            changes.append({
                "type": "PRICE_CHANGED",
                "record": record_info(current_record),
                "changes": price_changes
            })

        # -------------------------------------------------
        # OTHER IMPORTANT CHANGES
        # -------------------------------------------------

        other_changes = {}

        for field in OTHER_FIELDS:

            old_value = previous_record.get(field)
            new_value = current_record.get(field)

            if old_value != new_value:

                other_changes[field] = {
                    "old": old_value,
                    "new": new_value
                }

        if other_changes:

            changes.append({
                "type": "OTHER_CHANGED",
                "record": record_info(current_record),
                "changes": other_changes
            })

    # =====================================================
    # REMOVED RECORDS
    # =====================================================

    for key, previous_record in previous.items():

        if key not in current:

            changes.append({
                "type": "REMOVED",
                "record": record_info(previous_record)
            })

    return changes


# =========================================================
# CREATE SUMMARY
# =========================================================

def create_summary(changes):

    summary = {
        "new": 0,
        "price_changed": 0,
        "removed": 0,
        "other_changed": 0
    }

    for change in changes:

        change_type = change["type"]

        if change_type == "NEW":

            summary["new"] += 1

        elif change_type == "PRICE_CHANGED":

            summary["price_changed"] += 1

        elif change_type == "REMOVED":

            summary["removed"] += 1

        elif change_type == "OTHER_CHANGED":

            summary["other_changed"] += 1

    return summary


# =========================================================
# SAVE ALERTS
# =========================================================

def save_alerts(changes):

    output = {
        "generated_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "total_changes": len(changes),
        "summary": create_summary(changes),
        "changes": changes
    }

    os.makedirs(
        os.path.dirname(ALERT_FILE),
        exist_ok=True
    )

    with open(
        ALERT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"\n💾 {ALERT_FILE} generated"
    )


# =========================================================
# DISPLAY ALERT
# =========================================================

def display_alert(change):

    change_type = change["type"]
    record = change["record"]

    print("\n" + "=" * 65)

    if change_type == "NEW":

        print("🆕 NEW BUFFET")

    elif change_type == "PRICE_CHANGED":

        print("💰 PRICE CHANGED")

    elif change_type == "REMOVED":

        print("🗑️ REMOVED")

    elif change_type == "OTHER_CHANGED":

        print("✏️ OTHER CHANGE")

    print("=" * 65)

    print(f"Branch        : {record.get('Branch')}")
    print(f"Date          : {record.get('Date')}")
    print(f"Slot Time     : {record.get('Slot Time')}")
    print(f"Period        : {record.get('Period')}")
    print(f"Customer Type : {record.get('Customer Type')}")
    print(f"Food Type     : {record.get('Food Type')}")
    print(f"Plan          : {record.get('Plan')}")

    if change_type == "NEW":

        print(
            f"Price         : ₹{record.get('Price')}"
        )

        print(
            f"Original Price: ₹{record.get('Original Price')}"
        )

    elif change_type == "REMOVED":

        print(
            f"Last Price    : ₹{record.get('Price')}"
        )

        print(
            f"Original Price: ₹{record.get('Original Price')}"
        )

    else:

        for field, values in change["changes"].items():

            print(
                f"{field}: "
                f"{values['old']} → {values['new']}"
            )


# =========================================================
# MAIN
# =========================================================

def main():

    print("\n🔔 BBQ ALERT ENGINE")
    print("=" * 65)

    # -----------------------------------------------------
    # LOAD CURRENT DATA
    # -----------------------------------------------------

    print("\n📂 Loading current dataset...")

    current_records = load_current_dataset()

    print(
        f"   Current records: "
        f"{len(current_records)}"
    )

    if not current_records:

        print(
            "\n❌ No current records found."
        )

        print(
            "❌ Snapshot will NOT be updated."
        )

        return False

    # -----------------------------------------------------
    # LOAD PREVIOUS SNAPSHOT
    # -----------------------------------------------------

    print("\n📂 Loading previous snapshot...")

    previous_records = load_previous_snapshot()

    # -----------------------------------------------------
    # FIRST RUN
    # -----------------------------------------------------

    if previous_records is None:

        print("\n🟢 FIRST RUN")

        print(
            "   Current data will be saved as "
            "the baseline."
        )

        print(
            "   No alerts will be generated."
        )

        save_alerts([])

        save_snapshot(current_records)

        print(
            "\n✅ Initial snapshot created."
        )

        return True

    # -----------------------------------------------------
    # COMPARE
    # -----------------------------------------------------

    print("\n🔍 Comparing previous vs current...")

    print(
        f"   Previous records: "
        f"{len(previous_records)}"
    )

    print(
        f"   Current records : "
        f"{len(current_records)}"
    )

    changes = compare_data(
        previous_records,
        current_records
    )

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    summary = create_summary(changes)

    print(
        f"\n📊 Total changes: "
        f"{len(changes)}"
    )

    print(
        f"   🆕 New           : "
        f"{summary['new']}"
    )

    print(
        f"   💰 Price changed : "
        f"{summary['price_changed']}"
    )

    print(
        f"   🗑️ Removed       : "
        f"{summary['removed']}"
    )

    print(
        f"   ✏️ Other changed : "
        f"{summary['other_changed']}"
    )

    # -----------------------------------------------------
    # DISPLAY
    # -----------------------------------------------------

    for change in changes:

        display_alert(change)

    # -----------------------------------------------------
    # SAVE ALERTS
    # -----------------------------------------------------

    save_alerts(changes)

    # -----------------------------------------------------
    # ONLY AFTER SUCCESSFUL COMPARISON
    # UPDATE SNAPSHOT
    # -----------------------------------------------------

    save_snapshot(current_records)

    print(
        "\n✅ Alert comparison completed."
    )

    return True


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":

    success = main()

    if not success:

        raise SystemExit(1)

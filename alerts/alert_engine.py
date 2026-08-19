# import json
# import os
# from datetime import datetime


# # =========================================================
# # CONFIGURATION
# # =========================================================

# JSON_FILES = [
#     "json/buffet_data_1.json",
#     "json/buffet_data_2.json",
#     "json/buffet_data_3.json",
# ]

# SNAPSHOT_FILE = "alerts/previous_snapshot.json"
# ALERT_FILE = "alerts/alerts.json"


# # =========================================================
# # RECORD IDENTITY
# # =========================================================
# #
# # These fields together identify one buffet record.
# #
# # If Price changes, it is still the SAME record.
# #
# # =========================================================

# IDENTITY_FIELDS = [
#     "Branch",
#     "Date",
#     "Slot Time",
#     "Customer Type",
#     "Food Type",
#     "Plan",
# ]


# # =========================================================
# # IMPORTANT CHANGE FIELDS
# # =========================================================

# PRICE_FIELDS = [
#     "Price",
#     "Original Price",
# ]

# OTHER_FIELDS = [
#     "Period",
# ]

# # =========================================================
# # EMAIL CONFIGURATION
# # =========================================================

# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587

# # Email account that will SEND the alert
# EMAIL_SENDER = "yourgmail@gmail.com"

# # Gmail App Password
# #
# # IMPORTANT:
# # Use a Gmail App Password here, NOT your normal Gmail
# # account password.
# #
# EMAIL_PASSWORD = "your_16_character_app_password"

# # Two recipients
# EMAIL_RECIPIENTS = [
#     "receiver1@example.com",
#     "receiver2@example.com",
# ]


# # =========================================================
# # LOAD CURRENT JSON
# # =========================================================

# def load_current_dataset():

#     all_records = []

#     for path in JSON_FILES:

#         if not os.path.exists(path):

#             print(f"⚠️ Missing file: {path}")
#             continue

#         try:

#             with open(path, "r", encoding="utf-8") as f:
#                 data = json.load(f)

#         except Exception as e:

#             print(f"❌ Could not read {path}: {e}")
#             continue

#         records = data.get("records", [])

#         if not isinstance(records, list):

#             print(f"⚠️ Invalid records in {path}")
#             continue

#         all_records.extend(records)

#     return all_records


# # =========================================================
# # LOAD PREVIOUS SNAPSHOT
# # =========================================================

# def load_previous_snapshot():

#     if not os.path.exists(SNAPSHOT_FILE):

#         print("\nℹ️ No previous snapshot found.")
#         print("   This is the first alert run.")

#         return None

#     try:

#         with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
#             data = json.load(f)

#         records = data.get("records", [])

#         if not isinstance(records, list):

#             print("⚠️ Previous snapshot is invalid.")

#             return None

#         return records

#     except Exception as e:

#         print(f"❌ Could not read previous snapshot: {e}")

#         return None


# # =========================================================
# # SAVE CURRENT DATA AS SNAPSHOT
# # =========================================================

# def save_snapshot(records):

#     os.makedirs(
#         os.path.dirname(SNAPSHOT_FILE),
#         exist_ok=True
#     )

#     data = {
#         "generated_at": datetime.now().strftime(
#             "%Y-%m-%d %H:%M:%S"
#         ),
#         "records": records
#     }

#     with open(
#         SNAPSHOT_FILE,
#         "w",
#         encoding="utf-8"
#     ) as f:

#         json.dump(
#             data,
#             f,
#             indent=2,
#             ensure_ascii=False
#         )

#     print(
#         f"\n💾 Previous snapshot updated "
#         f"({len(records)} records)"
#     )


# # =========================================================
# # CREATE UNIQUE KEY
# # =========================================================

# def make_key(record):

#     return tuple(
#         record.get(field)
#         for field in IDENTITY_FIELDS
#     )


# # =========================================================
# # CREATE INDEX
# # =========================================================

# def create_index(records):

#     indexed = {}

#     for record in records:

#         key = make_key(record)

#         if key in indexed:

#             continue

#         indexed[key] = record

#     return indexed


# # =========================================================
# # RECORD INFORMATION FOR ALERT
# # =========================================================

# def record_info(record):

#     return {
#         "Branch": record.get("Branch"),
#         "Branch ID": record.get("Branch ID"),
#         "Date": record.get("Date"),
#         "Slot Time": record.get("Slot Time"),
#         "Period": record.get("Period"),
#         "Customer Type": record.get("Customer Type"),
#         "Food Type": record.get("Food Type"),
#         "Plan": record.get("Plan"),
#         "Price": record.get("Price"),
#         "Original Price": record.get("Original Price"),
#     }


# # =========================================================
# # COMPARE DATA
# # =========================================================

# def compare_data(previous_records, current_records):

#     previous = create_index(previous_records)
#     current = create_index(current_records)

#     changes = []

#     # =====================================================
#     # NEW + MODIFIED
#     # =====================================================

#     for key, current_record in current.items():

#         # -------------------------------------------------
#         # NEW RECORD
#         # -------------------------------------------------

#         if key not in previous:

#             changes.append({
#                 "type": "NEW",
#                 "record": record_info(current_record)
#             })

#             continue

#         previous_record = previous[key]

#         # -------------------------------------------------
#         # PRICE CHANGES
#         # -------------------------------------------------

#         price_changes = {}

#         for field in PRICE_FIELDS:

#             old_value = previous_record.get(field)
#             new_value = current_record.get(field)

#             if old_value != new_value:

#                 price_changes[field] = {
#                     "old": old_value,
#                     "new": new_value
#                 }

#         if price_changes:

#             changes.append({
#                 "type": "PRICE_CHANGED",
#                 "record": record_info(current_record),
#                 "changes": price_changes
#             })

#         # -------------------------------------------------
#         # OTHER IMPORTANT CHANGES
#         # -------------------------------------------------

#         other_changes = {}

#         for field in OTHER_FIELDS:

#             old_value = previous_record.get(field)
#             new_value = current_record.get(field)

#             if old_value != new_value:

#                 other_changes[field] = {
#                     "old": old_value,
#                     "new": new_value
#                 }

#         if other_changes:

#             changes.append({
#                 "type": "OTHER_CHANGED",
#                 "record": record_info(current_record),
#                 "changes": other_changes
#             })

#     # =====================================================
#     # REMOVED RECORDS
#     # =====================================================

#     for key, previous_record in previous.items():

#         if key not in current:

#             changes.append({
#                 "type": "REMOVED",
#                 "record": record_info(previous_record)
#             })

#     return changes


# # =========================================================
# # CREATE SUMMARY
# # =========================================================

# def create_summary(changes):

#     summary = {
#         "new": 0,
#         "price_changed": 0,
#         "removed": 0,
#         "other_changed": 0
#     }

#     for change in changes:

#         change_type = change["type"]

#         if change_type == "NEW":

#             summary["new"] += 1

#         elif change_type == "PRICE_CHANGED":

#             summary["price_changed"] += 1

#         elif change_type == "REMOVED":

#             summary["removed"] += 1

#         elif change_type == "OTHER_CHANGED":

#             summary["other_changed"] += 1

#     return summary


# # =========================================================
# # SAVE ALERTS
# # =========================================================

# def save_alerts(changes):

#     output = {
#         "generated_at": datetime.now().strftime(
#             "%Y-%m-%d %H:%M:%S"
#         ),
#         "total_changes": len(changes),
#         "summary": create_summary(changes),
#         "changes": changes
#     }

#     os.makedirs(
#         os.path.dirname(ALERT_FILE),
#         exist_ok=True
#     )

#     with open(
#         ALERT_FILE,
#         "w",
#         encoding="utf-8"
#     ) as f:

#         json.dump(
#             output,
#             f,
#             indent=2,
#             ensure_ascii=False
#         )

#     print(
#         f"\n💾 {ALERT_FILE} generated"
#     )


# # =========================================================
# # DISPLAY ALERT
# # =========================================================

# def display_alert(change):

#     change_type = change["type"]
#     record = change["record"]

#     print("\n" + "=" * 65)

#     if change_type == "NEW":

#         print("🆕 NEW BUFFET")

#     elif change_type == "PRICE_CHANGED":

#         print("💰 PRICE CHANGED")

#     elif change_type == "REMOVED":

#         print("🗑️ REMOVED")

#     elif change_type == "OTHER_CHANGED":

#         print("✏️ OTHER CHANGE")

#     print("=" * 65)

#     print(f"Branch        : {record.get('Branch')}")
#     print(f"Date          : {record.get('Date')}")
#     print(f"Slot Time     : {record.get('Slot Time')}")
#     print(f"Period        : {record.get('Period')}")
#     print(f"Customer Type : {record.get('Customer Type')}")
#     print(f"Food Type     : {record.get('Food Type')}")
#     print(f"Plan          : {record.get('Plan')}")

#     if change_type == "NEW":

#         print(
#             f"Price         : ₹{record.get('Price')}"
#         )

#         print(
#             f"Original Price: ₹{record.get('Original Price')}"
#         )

#     elif change_type == "REMOVED":

#         print(
#             f"Last Price    : ₹{record.get('Price')}"
#         )

#         print(
#             f"Original Price: ₹{record.get('Original Price')}"
#         )

#     else:

#         for field, values in change["changes"].items():

#             print(
#                 f"{field}: "
#                 f"{values['old']} → {values['new']}"
#             )


# # =========================================================
# # MAIN
# # =========================================================

# def main():

#     print("\n🔔 BBQ ALERT ENGINE")
#     print("=" * 65)

#     # -----------------------------------------------------
#     # LOAD CURRENT DATA
#     # -----------------------------------------------------

#     print("\n📂 Loading current dataset...")

#     current_records = load_current_dataset()

#     print(
#         f"   Current records: "
#         f"{len(current_records)}"
#     )

#     if not current_records:

#         print(
#             "\n❌ No current records found."
#         )

#         print(
#             "❌ Snapshot will NOT be updated."
#         )

#         return False

#     # -----------------------------------------------------
#     # LOAD PREVIOUS SNAPSHOT
#     # -----------------------------------------------------

#     print("\n📂 Loading previous snapshot...")

#     previous_records = load_previous_snapshot()

#     # -----------------------------------------------------
#     # FIRST RUN
#     # -----------------------------------------------------

#     if previous_records is None:

#         print("\n🟢 FIRST RUN")

#         print(
#             "   Current data will be saved as "
#             "the baseline."
#         )

#         print(
#             "   No alerts will be generated."
#         )

#         save_alerts([])

#         save_snapshot(current_records)

#         print(
#             "\n✅ Initial snapshot created."
#         )

#         return True

#     # -----------------------------------------------------
#     # COMPARE
#     # -----------------------------------------------------

#     print("\n🔍 Comparing previous vs current...")

#     print(
#         f"   Previous records: "
#         f"{len(previous_records)}"
#     )

#     print(
#         f"   Current records : "
#         f"{len(current_records)}"
#     )

#     changes = compare_data(
#         previous_records,
#         current_records
#     )

#     # -----------------------------------------------------
#     # SUMMARY
#     # -----------------------------------------------------

#     summary = create_summary(changes)

#     print(
#         f"\n📊 Total changes: "
#         f"{len(changes)}"
#     )

#     print(
#         f"   🆕 New           : "
#         f"{summary['new']}"
#     )

#     print(
#         f"   💰 Price changed : "
#         f"{summary['price_changed']}"
#     )

#     print(
#         f"   🗑️ Removed       : "
#         f"{summary['removed']}"
#     )

#     print(
#         f"   ✏️ Other changed : "
#         f"{summary['other_changed']}"
#     )

#     # -----------------------------------------------------
#     # DISPLAY
#     # -----------------------------------------------------

#     for change in changes:

#         display_alert(change)

#     # -----------------------------------------------------
#     # SAVE ALERTS
#     # -----------------------------------------------------

#     save_alerts(changes)

#     # -----------------------------------------------------
#     # ONLY AFTER SUCCESSFUL COMPARISON
#     # UPDATE SNAPSHOT
#     # -----------------------------------------------------

#     save_snapshot(current_records)

#     print(
#         "\n✅ Alert comparison completed."
#     )

#     return True


# # =========================================================
# # ENTRY POINT
# # =========================================================

# if __name__ == "__main__":

#     success = main()

#     if not success:

#         raise SystemExit(1)


#  ==========================================================================================================================================
# Email integration in order to make the process smooth required rewriting of the code as the machinery language changed a lot.
#  ===========================================================================================================================================
import json
import os
import smtplib

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
# EMAIL CONFIGURATION
# =========================================================
#
# Recommended:
# Set these as environment variables instead of putting
# passwords directly in this file.
#
# Gmail:
#
# SMTP_SERVER = smtp.gmail.com
# SMTP_PORT   = 587
#
# EMAIL_SENDER      = your@gmail.com
# EMAIL_PASSWORD    = Gmail App Password
# EMAIL_RECIPIENT_1 = receiver1@example.com
# EMAIL_RECIPIENT_2 = receiver2@example.com
#
# =========================================================

# ====================================================================
# When implementing the env perspective make this uncomment
# =======================================================================
# SMTP_SERVER = os.getenv(
#     "SMTP_SERVER",
#     "smtp.gmail.com"
# )

# SMTP_PORT = int(
#     os.getenv(
#         "SMTP_PORT",
#         "587"
#     )
# )

# EMAIL_SENDER = os.getenv(
#     "EMAIL_SENDER"
# )

# EMAIL_PASSWORD = os.getenv(
#     "EMAIL_PASSWORD"
# )

# EMAIL_RECIPIENTS = [
#     os.getenv("EMAIL_RECIPIENT_1"),
#     os.getenv("EMAIL_RECIPIENT_2"),
# ]

# # Remove empty recipient values
# EMAIL_RECIPIENTS = [
#     email
#     for email in EMAIL_RECIPIENTS
#     if email
# ]

# =========================================================
# EMAIL CONFIGURATION
# =========================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Email account that will SEND the alert
EMAIL_SENDER = "atlantaswork@gmail.com"

# Gmail Password
EMAIL_PASSWORD = "jppw uksg kdku qmbl"

# Two recipients
EMAIL_RECIPIENTS = [
    "ops.mis@absolute-barbecue.com",
    "gaurav.a@absolute-barbecue.com",
]


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

            print(
                f"⚠️ Missing file: {path}"
            )

            continue

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

        except Exception as e:

            print(
                f"❌ Could not read {path}: {e}"
            )

            continue

        records = data.get(
            "records",
            []
        )

        if not isinstance(
            records,
            list
        ):

            print(
                f"⚠️ Invalid records in {path}"
            )

            continue

        all_records.extend(records)

    return all_records


# =========================================================
# LOAD PREVIOUS SNAPSHOT
# =========================================================

def load_previous_snapshot():

    if not os.path.exists(
        SNAPSHOT_FILE
    ):

        print(
            "\nℹ️ No previous snapshot found."
        )

        print(
            "   This is the first alert run."
        )

        return None

    try:

        with open(
            SNAPSHOT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        records = data.get(
            "records",
            []
        )

        if not isinstance(
            records,
            list
        ):

            print(
                "⚠️ Previous snapshot is invalid."
            )

            return None

        return records

    except Exception as e:

        print(
            f"❌ Could not read previous snapshot: {e}"
        )

        return None


# =========================================================
# SAVE CURRENT DATA AS SNAPSHOT
# =========================================================

def save_snapshot(records):

    snapshot_directory = os.path.dirname(
        SNAPSHOT_FILE
    )

    if snapshot_directory:

        os.makedirs(
            snapshot_directory,
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
        "Original Price": record.get(
            "Original Price"
        ),
    }


# =========================================================
# COMPARE DATA
# =========================================================

def compare_data(
    previous_records,
    current_records
):

    previous = create_index(
        previous_records
    )

    current = create_index(
        current_records
    )

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
                "record": record_info(
                    current_record
                )
            })

            continue

        previous_record = previous[key]

        # -------------------------------------------------
        # PRICE CHANGES
        # -------------------------------------------------

        price_changes = {}

        for field in PRICE_FIELDS:

            old_value = previous_record.get(
                field
            )

            new_value = current_record.get(
                field
            )

            if old_value != new_value:

                price_changes[field] = {
                    "old": old_value,
                    "new": new_value
                }

        if price_changes:

            changes.append({
                "type": "PRICE_CHANGED",
                "record": record_info(
                    current_record
                ),
                "changes": price_changes
            })

        # -------------------------------------------------
        # OTHER IMPORTANT CHANGES
        # -------------------------------------------------

        other_changes = {}

        for field in OTHER_FIELDS:

            old_value = previous_record.get(
                field
            )

            new_value = current_record.get(
                field
            )

            if old_value != new_value:

                other_changes[field] = {
                    "old": old_value,
                    "new": new_value
                }

        if other_changes:

            changes.append({
                "type": "OTHER_CHANGED",
                "record": record_info(
                    current_record
                ),
                "changes": other_changes
            })

    # =====================================================
    # REMOVED RECORDS
    # =====================================================

    for key, previous_record in previous.items():

        if key not in current:

            changes.append({
                "type": "REMOVED",
                "record": record_info(
                    previous_record
                )
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

    alert_directory = os.path.dirname(
        ALERT_FILE
    )

    if alert_directory:

        os.makedirs(
            alert_directory,
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

    print(
        "\n" + "=" * 65
    )

    if change_type == "NEW":

        print("🆕 NEW BUFFET")

    elif change_type == "PRICE_CHANGED":

        print("💰 PRICE CHANGED")

    elif change_type == "REMOVED":

        print("🗑️ REMOVED")

    elif change_type == "OTHER_CHANGED":

        print("✏️ OTHER CHANGE")

    print(
        "=" * 65
    )

    print(
        f"Branch        : "
        f"{record.get('Branch')}"
    )

    print(
        f"Date          : "
        f"{record.get('Date')}"
    )

    print(
        f"Slot Time     : "
        f"{record.get('Slot Time')}"
    )

    print(
        f"Period        : "
        f"{record.get('Period')}"
    )

    print(
        f"Customer Type : "
        f"{record.get('Customer Type')}"
    )

    print(
        f"Food Type     : "
        f"{record.get('Food Type')}"
    )

    print(
        f"Plan          : "
        f"{record.get('Plan')}"
    )

    if change_type == "NEW":

        print(
            f"Price         : "
            f"₹{record.get('Price')}"
        )

        print(
            f"Original Price: "
            f"₹{record.get('Original Price')}"
        )

    elif change_type == "REMOVED":

        print(
            f"Last Price    : "
            f"₹{record.get('Price')}"
        )

        print(
            f"Original Price: "
            f"₹{record.get('Original Price')}"
        )

    else:

        for field, values in change[
            "changes"
        ].items():

            print(
                f"{field}: "
                f"{values['old']} → "
                f"{values['new']}"
            )


# =========================================================
# HTML EMAIL BODY
# =========================================================

def create_email_body(changes):

    summary = create_summary(
        changes
    )

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

body {{
    font-family: Arial, sans-serif;
    background: #f5f5f5;
    padding: 20px;
}}

.container {{
    max-width: 800px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 10px;
}}

.summary {{
    background: #f0f0f0;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}}

.alert {{
    border: 1px solid #dddddd;
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 18px;
}}

.new {{
    border-left: 6px solid #2e7d32;
}}

.price {{
    border-left: 6px solid #f9a825;
}}

.removed {{
    border-left: 6px solid #c62828;
}}

.other {{
    border-left: 6px solid #1565c0;
}}

.label {{
    font-weight: bold;
}}

.change {{
    background: #f7f7f7;
    padding: 8px;
    border-radius: 5px;
    margin-top: 5px;
}}

.footer {{
    color: #777777;
    font-size: 12px;
    margin-top: 25px;
}}

</style>

</head>

<body>

<div class="container">

<h2>🔔 BBQ Buffet Alert</h2>

<p>
The buffet monitoring system detected
<strong>{len(changes)}</strong>
change(s).
</p>

<div class="summary">

<h3>📊 Summary</h3>

<ul>

<li>
🆕 New:
<strong>{summary['new']}</strong>
</li>

<li>
💰 Price Changed:
<strong>{summary['price_changed']}</strong>
</li>

<li>
🗑️ Removed:
<strong>{summary['removed']}</strong>
</li>

<li>
✏️ Other Changed:
<strong>{summary['other_changed']}</strong>
</li>

</ul>

</div>
"""

    # =====================================================
    # EACH CHANGE
    # =====================================================

    for change in changes:

        change_type = change["type"]
        record = change["record"]

        if change_type == "NEW":

            title = "🆕 NEW BUFFET"
            css_class = "new"

        elif change_type == "PRICE_CHANGED":

            title = "💰 PRICE CHANGED"
            css_class = "price"

        elif change_type == "REMOVED":

            title = "🗑️ REMOVED"
            css_class = "removed"

        else:

            title = "✏️ OTHER CHANGE"
            css_class = "other"

        html += f"""
<div class="alert {css_class}">

<h3>{title}</h3>

<p>
<span class="label">Branch:</span>
{record.get('Branch')}
</p>

<p>
<span class="label">Branch ID:</span>
{record.get('Branch ID')}
</p>

<p>
<span class="label">Date:</span>
{record.get('Date')}
</p>

<p>
<span class="label">Slot Time:</span>
{record.get('Slot Time')}
</p>

<p>
<span class="label">Period:</span>
{record.get('Period')}
</p>

<p>
<span class="label">Customer Type:</span>
{record.get('Customer Type')}
</p>

<p>
<span class="label">Food Type:</span>
{record.get('Food Type')}
</p>

<p>
<span class="label">Plan:</span>
{record.get('Plan')}
</p>
"""

        # -------------------------------------------------
        # NEW
        # -------------------------------------------------

        if change_type == "NEW":

            html += f"""
<p>
<span class="label">Price:</span>
₹{record.get('Price')}
</p>

<p>
<span class="label">Original Price:</span>
₹{record.get('Original Price')}
</p>
"""

        # -------------------------------------------------
        # REMOVED
        # -------------------------------------------------

        elif change_type == "REMOVED":

            html += f"""
<p>
<span class="label">Last Price:</span>
₹{record.get('Price')}
</p>

<p>
<span class="label">Original Price:</span>
₹{record.get('Original Price')}
</p>
"""

        # -------------------------------------------------
        # CHANGED
        # -------------------------------------------------

        else:

            html += """
<h4>Changes</h4>
"""

            for field, values in change[
                "changes"
            ].items():

                html += f"""
<div class="change">

<strong>{field}</strong>:

{values['old']}

&nbsp;→&nbsp;

<strong>{values['new']}</strong>

</div>
"""

        html += """
</div>
"""

    html += f"""

<div class="footer">

Generated automatically at
{generated_at}

</div>

</div>

</body>

</html>
"""

    return html


# =========================================================
# SEND EMAIL ALERT
# =========================================================

def send_email_alert(changes):

    # -----------------------------------------------------
    # NO CHANGES
    # -----------------------------------------------------

    if not changes:

        print(
            "\n📭 No changes detected."
        )

        print(
            "   Email notification not sent."
        )

        return True

    # -----------------------------------------------------
    # CHECK EMAIL CONFIGURATION
    # -----------------------------------------------------

    if not EMAIL_SENDER:

        print(
            "\n❌ EMAIL_SENDER is not configured."
        )

        return False

    if not EMAIL_PASSWORD:

        print(
            "\n❌ EMAIL_PASSWORD is not configured."
        )

        return False

    if not EMAIL_RECIPIENTS:

        print(
            "\n❌ No email recipients configured."
        )

        return False

    # -----------------------------------------------------
    # CREATE SUBJECT
    # -----------------------------------------------------

    summary = create_summary(
        changes
    )

    subject = (
        f"🔔 BBQ Alert: "
        f"{len(changes)} Change(s) "
        f"| New: {summary['new']} "
        f"| Price: {summary['price_changed']} "
        f"| Removed: {summary['removed']}"
    )

    # -----------------------------------------------------
    # CREATE MESSAGE
    # -----------------------------------------------------

    message = MIMEMultipart(
        "alternative"
    )

    message["From"] = EMAIL_SENDER

    message["To"] = ", ".join(
        EMAIL_RECIPIENTS
    )

    message["Subject"] = subject

    html_body = create_email_body(
        changes
    )

    message.attach(
        MIMEText(
            html_body,
            "html",
            "utf-8"
        )
    )

    # -----------------------------------------------------
    # SEND
    # -----------------------------------------------------

    try:

        print(
            "\n📧 Sending email alert..."
        )

        print(
            f"   Recipients: "
            f"{', '.join(EMAIL_RECIPIENTS)}"
        )

        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                EMAIL_SENDER,
                EMAIL_PASSWORD
            )

            server.sendmail(
                EMAIL_SENDER,
                EMAIL_RECIPIENTS,
                message.as_string()
            )

        print(
            "\n✅ Email alert sent successfully."
        )

        return True

    except Exception as e:

        print(
            f"\n❌ Failed to send email: {e}"
        )

        return False


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "\n🔔 BBQ ALERT ENGINE"
    )

    print(
        "=" * 65
    )

    # -----------------------------------------------------
    # LOAD CURRENT DATA
    # -----------------------------------------------------

    print(
        "\n📂 Loading current dataset..."
    )

    current_records = (
        load_current_dataset()
    )

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

    print(
        "\n📂 Loading previous snapshot..."
    )

    previous_records = (
        load_previous_snapshot()
    )

    # -----------------------------------------------------
    # FIRST RUN
    # -----------------------------------------------------

    if previous_records is None:

        print(
            "\n🟢 FIRST RUN"
        )

        print(
            "   Current data will be saved "
            "as the baseline."
        )

        print(
            "   No alerts will be generated."
        )

        save_alerts([])

        save_snapshot(
            current_records
        )

        print(
            "\n✅ Initial snapshot created."
        )

        return True

    # -----------------------------------------------------
    # COMPARE
    # -----------------------------------------------------

    print(
        "\n🔍 Comparing previous vs current..."
    )

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

    summary = create_summary(
        changes
    )

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
    # DISPLAY ALERTS
    # -----------------------------------------------------

    for change in changes:

        display_alert(
            change
        )

    # -----------------------------------------------------
    # SAVE ALERTS
    # -----------------------------------------------------

    save_alerts(
        changes
    )

    # -----------------------------------------------------
    # SEND EMAIL
    # -----------------------------------------------------
    #
    # If there are no changes, this simply returns True.
    #
    # If email fails, the snapshot is NOT updated.
    #
    # -----------------------------------------------------

    email_success = (
        send_email_alert(
            changes
        )
    )

    if not email_success:

        print(
            "\n❌ Email sending failed."
        )

        print(
            "❌ Snapshot will NOT be updated."
        )

        return False

    # -----------------------------------------------------
    # UPDATE SNAPSHOT
    # -----------------------------------------------------

    save_snapshot(
        current_records
    )

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

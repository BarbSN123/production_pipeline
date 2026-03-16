# Production pipeline controller

import subprocess
import time
import random
import sys

files = [
    "fetch_push_branch_banajara_hills.py",
    "fetch_push_branch_kormangala.py",
    "fetch_push_branch_Rukamani_Colony_AS_Rao_Nagar.py",
    "fetch_push_json_Abids.py",
    "fetch_push_json_Acropolis_Mall.py",
    "fetch_push_json_Alcazar_Mall_Jubilee_Hills.py",
    "fetch_push_json_Amanora.py",
    "fetch_push_json_Aundh.py",
    "fetch_push_json_Barasat.py",
    "fetch_push_json_Bazullah_Road.py",
    "fetch_push_json_Belapur.py",
    "fetch_push_json_brigade_twin_tower.py",
    "fetch_push_json_Chromepet.py",
    "fetch_push_json_Coimbatore.py",
    "fetch_push_json_DLF_Porur.py",
    "fetch_push_json_DSL_Virtue_Mall_Uppal.py",
    "fetch_push_json_Electronic_City_Phase_1.py",
    "fetch_push_json_Elpro_Mall.py",
    "fetch_push_json_Fraser_Road.py",
    "fetch_push_json_Hinjewadinagar.py",
    "fetch_push_json_Howrah.py",
    "fetch_push_json_inorbital.py",
    "fetch_push_json_Jessore_Road.py",
    "fetch_push_json_JP_Nagar.py",
    "fetch_push_json_Kalyan_Nagar.py",
    "fetch_push_json_Kalyani_Nagar.py",
    "fetch_push_json_Kompally_Hyderabad.py",
    "fetch_push_json_Kothapet.py",
    "fetch_push_json_Madhurwada.py",
    "fetch_push_json_Marathalli.py",
    "fetch_push_json_MgRoad.py",
    "fetch_push_json_Miyapur.py",
    "fetch_push_json_Nagpur.py",
    "fetch_push_json_nerul.py",
    "fetch_push_json_OMR.py",
    "fetch_push_json_Park_Street.py",
    "fetch_push_json_phoenix_centaurus_gachibowli.py",
    "fetch_push_json_Rajajinagar.py",
    "fetch_push_json_Sachivalay_Marg.py",
    "fetch_push_json_Sakinaka.py",
    "fetch_push_json_Salt_Lake.py",
    "fetch_push_json_Sector_24.py",
    "fetch_push_json_Sector_26.py",
    "fetch_push_json_Sector_62.py",
    "fetch_push_json_Udeshna_Building.py",
    "fetch_push_json_Vadapalani.py",
    "fetch_push_json_Velachery.py",
    "fetch_push_json_Wakad.py",
    "fetch_push_json_WhiteField.py",
    "fetch_push_json_Yelahanka.py"
]

# ---- read start and end index from workflow ----
start = int(sys.argv[1])
end = int(sys.argv[2])

selected_files = files[start:end]

print(f"\n⚙️ Running scripts {start} → {end}")

for f in selected_files:
    print(f"\n🚀 Running {f}")
    subprocess.run(["python", f])

    delay = random.uniform(6, 10)
    print(f"⏳ Waiting {delay:.1f} seconds...")
    time.sleep(delay)

print("\n✅ Job completed")
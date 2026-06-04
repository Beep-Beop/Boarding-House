import sys
import os
import time
import requests

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database import SessionLocal
from src.models import Location

PSGC_BASE = "https://psgc.gitlab.io/api"

def fetch(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def run_seeder():
    db = SessionLocal()
    inserted_counter = 0

    try:
        # Fetch all provinces + NCR separately (NCR is a region, not a province)
        provinces = fetch(f"{PSGC_BASE}/provinces/")
        ncr_cities = fetch(f"{PSGC_BASE}/regions/130000000/cities-municipalities/")

        # Build list of (province_name, province_code) tuples
        all_regions = [(p["name"], p["code"]) for p in provinces]

        print(f"Found {len(all_regions)} provinces. Fetching cities...")

        # Process regular provinces
        for province_name, province_code in all_regions:
            cities = fetch(f"{PSGC_BASE}/provinces/{province_code}/cities-municipalities/")
            time.sleep(0.1)

            for city in cities:
                city_name = city["name"]
                city_code = city["code"]

                barangays = fetch(f"{PSGC_BASE}/cities-municipalities/{city_code}/barangays/")
                time.sleep(0.1)

                for barangay in barangays:
                    exists = db.query(Location).filter(
                        Location.province == province_name,
                        Location.city == city_name,
                        Location.barangay == barangay["name"]
                    ).first()

                    if not exists:
                        db.add(Location(
                            province=province_name,
                            city=city_name,
                            barangay=barangay["name"]
                        ))
                        inserted_counter += 1

            db.commit()  # commit per province to avoid giant transactions
            print(f"  Done: {province_name}")

        # Process NCR cities
        print("Processing NCR...")
        for city in ncr_cities:
            city_name = city["name"]
            city_code = city["code"]

            barangays = fetch(f"{PSGC_BASE}/cities-municipalities/{city_code}/barangays/")
            time.sleep(0.1)

            for barangay in barangays:
                exists = db.query(Location).filter(
                    Location.province == "Metro Manila",
                    Location.city == city_name,
                    Location.barangay == barangay["name"]
                ).first()

                if not exists:
                    db.add(Location(
                        province="Metro Manila",
                        city=city_name,
                        barangay=barangay["name"]
                    ))
                    inserted_counter += 1

        db.commit()
        print(f"\nDone! Inserted {inserted_counter} records.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_seeder()
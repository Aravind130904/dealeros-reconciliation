import csv
import re
from decimal import Decimal, InvalidOperation
from datetime import date
from pathlib import Path
from .models import Location, SystemARecord, SystemBEntry

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def clean_text(value):
    return (value or "").strip()

def normalize_ref(raw):
    match = re.search(r"\d+", raw or "")
    return f"REC-{match.group()}" if match else None

def parse_amount(raw):
    value = clean_text(raw).replace(",", "")
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None

def parse_date(raw):
    value = clean_text(raw)
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None

def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as file:
        return [{key: clean_text(value) for key, value in row.items()} for row in csv.DictReader(file)]

def import_csv_data(data_dir=DATA_DIR):
    locations = read_csv(Path(data_dir) / "locations.csv")
    a_rows = read_csv(Path(data_dir) / "system_a.csv")
    b_rows = read_csv(Path(data_dir) / "system_b.csv")
    location_count = 0
    for row in locations:
        Location.objects.update_or_create(
            location_id=row["location_id"],
            defaults={"org_id": row["org_id"], "location_name": row.get("location_name", "")},
        )
        location_count += 1
    a_saved = 0
    for row in a_rows:
        location = Location.objects.get(location_id=row["location_id"])
        SystemARecord.objects.update_or_create(
            record_id=row["record_id"],
            defaults={
                "location": location,
                "event_date": parse_date(row.get("event_date")),
                "category_code": row.get("category_code", ""),
                "actor_id": row.get("actor_id") or None,
                "base_value": parse_amount(row.get("base_value")),
                "adjustment": parse_amount(row.get("adjustment")),
                "total_value": parse_amount(row.get("total_value")),
                "state": row.get("state", ""),
            },
        )
        a_saved += 1
    b_saved = 0
    blank_values = 0
    cleaned_refs = 0
    for row in b_rows:
        location = Location.objects.get(location_id=row["location_id"])
        normalized = normalize_ref(row.get("record_ref"))
        amount = parse_amount(row.get("value"))
        if amount is None:
            blank_values += 1
        if normalized != row.get("record_ref", ""):
            cleaned_refs += 1
        SystemBEntry.objects.update_or_create(
            entry_id=row["entry_id"],
            defaults={
                "record_ref_raw": row.get("record_ref", ""),
                "record_ref": normalized,
                "location": location,
                "recorded_on": parse_date(row.get("recorded_on")),
                "value_raw": row.get("value", ""),
                "value": amount,
                "label": row.get("label", ""),
            },
        )
        b_saved += 1
    return {"locations_read": len(locations), "locations_saved": location_count,
            "a_read": len(a_rows), "a_saved": a_saved, "b_read": len(b_rows), "b_saved": b_saved,
            "blank_b_values": blank_values, "refs_normalized": cleaned_refs}

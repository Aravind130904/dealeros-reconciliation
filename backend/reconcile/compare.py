from collections import defaultdict
from decimal import Decimal

REASONS = ["MISSING_IN_B", "ORPHAN_IN_B", "DUPLICATE_IN_B", "VALUE_MISMATCH", "LOCATION_MISMATCH", "DATE_MISMATCH"]

def compare(a_rows, b_rows):
    """Pure comparison. a_rows maps record id to total/location/date/state; b_rows is a list."""
    by_ref = defaultdict(list)
    output = []
    for entry in b_rows:
        by_ref[entry.get("ref")].append(entry)
    for ref, entries in by_ref.items():
        if ref not in a_rows:
            for entry in entries:
                output.append({"reason": "ORPHAN_IN_B", "record_id": ref or entry.get("ref_raw") or "UNKNOWN",
                              "entry_id": entry["entry_id"], "location": entry["location"],
                              "a_value": None, "b_value": entry.get("value"), "difference": None,
                              "a_location": None, "b_location": entry["location"]})
    for record_id, a in a_rows.items():
        entries = by_ref.get(record_id, [])
        if not entries:
            output.append({"reason": "MISSING_IN_B", "record_id": record_id,
                          "location": a["location"], "a_value": a.get("total"), "b_value": None,
                          "difference": None, "a_location": a["location"], "b_location": None})
            continue
        values = [entry.get("value") for entry in entries]
        if any(value is None for value in values):
            output.append({"reason": "VALUE_MISMATCH", "record_id": record_id,
                          "location": a["location"], "a_value": a.get("total"), "b_value": None,
                          "difference": None, "a_location": a["location"], "b_location": entries[0]["location"]})
            continue
        if len(entries) > 1:
            if sum(values, Decimal("0")) != a.get("total"):
                output.append({"reason": "DUPLICATE_IN_B", "record_id": record_id,
                              "location": a["location"], "a_value": a.get("total"),
                              "b_value": sum(values, Decimal("0")),
                              "difference": sum(values, Decimal("0")) - (a.get("total") or Decimal("0")),
                              "a_location": a["location"], "b_location": entries[0]["location"]})
            # A split whose entries sum to total is considered reconciled.
            continue
        entry = entries[0]
        if entry.get("value") != a.get("total"):
            output.append({"reason": "VALUE_MISMATCH", "record_id": record_id,
                          "location": a["location"], "a_value": a.get("total"),
                          "b_value": entry.get("value"),
                          "difference": (entry.get("value") or Decimal("0")) - (a.get("total") or Decimal("0")),
                          "a_location": a["location"], "b_location": entry["location"]})
        if entry.get("location") != a.get("location"):
            output.append({"reason": "LOCATION_MISMATCH", "record_id": record_id,
                          "location": a["location"], "a_value": a.get("total"),
                          "b_value": entry.get("value"), "difference": None,
                          "a_location": a["location"], "b_location": entry["location"]})
        if entry.get("date") != a.get("date"):
            output.append({"reason": "DATE_MISMATCH", "record_id": record_id,
                          "location": a["location"], "a_value": a.get("total"),
                          "b_value": entry.get("value"), "difference": None,
                          "a_location": a["location"], "b_location": entry["location"]})
    return output

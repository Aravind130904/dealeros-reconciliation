from decimal import Decimal
from reconcile.compare import compare

def arow(total="100.00", location="L1", date="2026-03-01"):
    return {"REC-1": {"total": Decimal(total), "location": location, "date": date, "state": "CONFIRMED"}}
def entry(id="E1", ref="REC-1", value="100.00", location="L1", date="2026-03-01"):
    return {"entry_id": id, "ref": ref, "ref_raw": ref, "value": Decimal(value) if value is not None else None, "location": location, "date": date}

def test_missing_in_b():
    assert compare(arow(), []) == [{"reason":"MISSING_IN_B", "record_id":"REC-1", "location":"L1", "a_value":Decimal("100.00"), "b_value":None, "difference":None, "a_location":"L1", "b_location":None}]
def test_orphan_in_b():
    result = compare({}, [entry(ref="REC-99")])
    assert result[0]["reason"] == "ORPHAN_IN_B"
def test_duplicate_in_b():
    result = compare(arow(), [entry(), entry(id="E2")])
    assert result[0]["reason"] == "DUPLICATE_IN_B"
def test_value_mismatch():
    result = compare(arow(), [entry(value="90.00")])
    assert result[0]["reason"] == "VALUE_MISMATCH"
def test_blank_value_is_not_zero():
    result = compare(arow(), [entry(value=None)])
    assert result[0]["reason"] == "VALUE_MISMATCH"
    assert result[0]["b_value"] is None
def test_split_that_sums_is_not_error():
    result = compare(arow(), [entry(value="40.00"), entry(id="E2", value="60.00")])
    assert result == []
def test_clean_row():
    assert compare(arow(), [entry()]) == []
def test_location_mismatch():
    result = compare(arow(), [entry(location="L2")])
    assert any(row["reason"] == "LOCATION_MISMATCH" for row in result)
def test_date_mismatch():
    result = compare(arow(), [entry(date="2026-03-02")])
    assert any(row["reason"] == "DATE_MISMATCH" for row in result)

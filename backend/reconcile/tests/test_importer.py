from decimal import Decimal
from reconcile.importer import normalize_ref, parse_amount

def test_normalize_dirty_refs():
    assert normalize_ref("rec1034") == "REC-1034"
    assert normalize_ref(" REC - 1070 ") == "REC-1070"
    assert normalize_ref("1112") == "REC-1112"
def test_indian_amount():
    assert parse_amount("1,25,400.00") == Decimal("125400.00")
def test_blank_is_none():
    assert parse_amount("") is None

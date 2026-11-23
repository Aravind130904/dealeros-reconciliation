import pytest
from django.test import Client
from reconcile.models import Location, SystemARecord, SystemBEntry
from decimal import Decimal

@pytest.mark.django_db
def test_org_api_does_not_return_other_org_locations():
    a = Location.objects.create(location_id="LOC-A", org_id="ORG-A")
    b = Location.objects.create(location_id="LOC-B", org_id="ORG-B")
    SystemARecord.objects.create(record_id="REC-A", location=a, total_value=Decimal("100"), state="CONFIRMED")
    SystemARecord.objects.create(record_id="REC-B", location=b, total_value=Decimal("100"), state="CONFIRMED")
    SystemBEntry.objects.create(entry_id="E-A", record_ref="REC-A", location=a, value=Decimal("90"))
    SystemBEntry.objects.create(entry_id="E-B", record_ref="REC-B", location=b, value=Decimal("90"))
    client = Client()
    response = client.get("/api/disagreements/?org=ORG-A")
    assert response.status_code == 200
    body = response.json()
    assert all(row["location"] != "LOC-B" for row in body["results"])
    assert all(row["record_id"] != "REC-B" for row in body["results"])

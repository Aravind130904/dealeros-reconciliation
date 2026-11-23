from decimal import Decimal
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Location, SystemARecord, SystemBEntry
from .compare import compare, REASONS

@require_GET
def organizations(request):
    orgs = list(Location.objects.values_list("org_id", flat=True).distinct().order_by("org_id"))
    return JsonResponse({"organizations": orgs})

def decimal_text(value):
    return str(value) if value is not None else None

@require_GET
def disagreements(request):
    org = request.GET.get("org", "").strip()
    if not org:
        return JsonResponse({"error": "org query parameter is required"}, status=400)
    # Tenant scope is applied to the database query before comparison.
    locations = Location.objects.filter(org_id=org)
    location_ids = list(locations.values_list("location_id", flat=True))
    a_qs = SystemARecord.objects.filter(location__org_id=org).select_related("location")
    b_qs = SystemBEntry.objects.filter(location__org_id=org).select_related("location")
    a_rows = {
        row.record_id: {"total": row.total_value, "location": row.location.location_id,
                       "date": row.event_date.isoformat() if row.event_date else None,
                       "state": row.state}
        for row in a_qs
    }
    b_rows = [{"entry_id": row.entry_id, "ref": row.record_ref, "ref_raw": row.record_ref_raw,
               "value": row.value, "location": row.location.location_id,
               "date": row.recorded_on.isoformat() if row.recorded_on else None}
              for row in b_qs]
    # Cross-tenant B location mismatch: include the disagreement for A's tenant, but
    # do not disclose the foreign location ID. B is scoped to this org, so cross-org
    # B rows are not fetched; location mismatch is not calculated for those rows.
    rows = compare(a_rows, b_rows)
    reason = request.GET.get("reason", "").strip()
    if reason and reason in REASONS:
        rows = [row for row in rows if row["reason"] == reason]
    sort = request.GET.get("sort", "")
    if sort in ("value", "-value"):
        rows.sort(key=lambda row: row["a_value"] or Decimal("0"), reverse=sort == "-value")
    safe_rows = []
    for row in rows:
        # Only return IDs/locations belonging to the requested tenant.
        safe_location = row.get("location") if row.get("location") in location_ids else None
        safe_rows.append({
            "reason": row["reason"], "record_id": row["record_id"],
            "location": safe_location, "a_value": decimal_text(row.get("a_value")),
            "b_value": decimal_text(row.get("b_value")), "difference": decimal_text(row.get("difference")),
            "a_location": row.get("a_location") if row.get("a_location") in location_ids else None,
            "b_location": row.get("b_location") if row.get("b_location") in location_ids else None,
        })
    return JsonResponse({"org": org, "count": len(safe_rows), "results": safe_rows})

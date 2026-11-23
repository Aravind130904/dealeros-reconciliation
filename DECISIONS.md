# Decisions

## Decision: Compare B with A's total value
- Rejected: compare against base_value.
- Why: B represents the final recorded amount; total_value includes base plus adjustment.

## Decision: Keep blank values as null
- Rejected: convert blank to zero.
- Why: blank means unknown and must not accidentally match a zero-valued record.

## Decision: Normalize references but preserve raw input
- Rejected: overwrite the original B reference.
- Why: normalized references allow matching while raw values remain auditable.

## Decision: A split is not a duplicate when it sums to A's total
- Rejected: flag every multi-entry reference.
- Why: multiple B rows can represent parts of one transaction.

## Decision: VOIDED records remain in the comparison
- Rejected: silently remove them.
- Why: the assignment asks that imported rows survive and the behavior should be visible. A voided A record with a B entry may be a business disagreement; this demo does not apply a special exemption.

## Decision: Date and location mismatches are extra reasons
- Rejected: only compare amounts.
- Why: they are useful data-quality signals and are explicitly present in the supplied files.

## Decision: Cross-tenant B locations are not exposed
- Rejected: return both raw location IDs.
- Why: the row can be attributed to A's tenant, but a B location belonging to another tenant is sensitive. The demo's tenant query scope avoids fetching foreign B rows and only returns locations owned by the requested org.

## Decision: SQLite and Decimal
- Rejected: a heavier database and floating-point amounts.
- Why: SQLite is enough for the assessment and Decimal provides exact money comparisons.

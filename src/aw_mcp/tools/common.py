"""Shared helpers for tools."""
from datetime import date, datetime
from decimal import Decimal

_INTERNET = (
    "SELECT OrderDateKey, ProductKey, TerritoryKey, SalesOrderNumber, "
    "OrderQty, LineTotal FROM dbo.FactInternetSales"
)
_RESELLER = (
    "SELECT OrderDateKey, ProductKey, TerritoryKey, SalesOrderNumber, "
    "OrderQty, LineTotal FROM dbo.FactResellerSales"
)
FACT_SOURCES = {
    "internet": _INTERNET,
    "reseller": _RESELLER,
    "all": _INTERNET + " UNION ALL " + _RESELLER,
}


def fact_source(channel: str) -> str:
    key = (channel or "all").lower()
    if key not in FACT_SOURCES:
        raise ValueError(f"channel must be one of {sorted(FACT_SOURCES)}")
    return FACT_SOURCES[key]


def year_filter(year: int | None) -> tuple[str, tuple]:
    if year is None:
        return "", ()
    return "WHERE d.[Year] = ?", (int(year),)


def clean_rows(rows: list[dict]) -> list[dict]:
    """Make rows JSON-friendly (Decimal -> float, dates -> text)."""
    cleaned = []
    for row in rows:
        item = {}
        for key, value in row.items():
            if isinstance(value, Decimal):
                value = round(float(value), 2)
            elif isinstance(value, (date, datetime)):
                value = value.isoformat()
            item[key] = value
        cleaned.append(item)
    return cleaned

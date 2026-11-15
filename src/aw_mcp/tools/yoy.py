"""Tool: year-over-year growth."""
from aw_mcp.db import run_query
from aw_mcp.tools.common import clean_rows, fact_source

# group_by -> (SELECT expression, GROUP BY expression or None)
_SEGMENTS = {
    "total": ("'All'", None),
    "category": (
        "ISNULL(p.ProductCategoryName, 'Unknown')",
        "ISNULL(p.ProductCategoryName, 'Unknown')",
    ),
    "territory": (
        "ISNULL(t.TerritoryName, 'Unknown')",
        "ISNULL(t.TerritoryName, 'Unknown')",
    ),
}
_METRICS = {"sales": "SUM(f.LineTotal)", "units": "SUM(f.OrderQty)"}


def compute_yoy(rows: list[dict]) -> list[dict]:
    """Add prev_value, growth_pct and comparable to rows.

    Each input row has: segment, year, value, months (months with data).
    comparable is False unless the year AND the previous year have 12 months.
    This function never touches the database, so pytest can test it alone.
    """
    # How many months of data each year has (max over segments)
    year_months: dict[int, int] = {}
    for r in rows:
        y = int(r["year"])
        year_months[y] = max(year_months.get(y, 0), int(r["months"]))

    by_key = {(r["segment"], int(r["year"])): r for r in rows}
    result = []
    for r in sorted(rows, key=lambda r: (r["segment"], int(r["year"]))):
        year = int(r["year"])
        prev = by_key.get((r["segment"], year - 1))
        prev_value = prev["value"] if prev else None
        growth = None
        if prev_value:
            growth = round((r["value"] - prev_value) / prev_value * 100, 1)
        comparable = (
            prev is not None
            and year_months[year] == 12
            and year_months.get(year - 1, 0) == 12
        )
        result.append(
            {
                "segment": r["segment"],
                "year": year,
                "value": r["value"],
                "prev_value": prev_value,
                "growth_pct": growth,
                "months": year_months[year],
                "comparable": comparable,
            }
        )
    return result


def yoy_growth(
    group_by: str = "total", metric: str = "sales", channel: str = "all"
) -> list[dict]:
    """Yearly totals with growth versus the previous year."""
    if group_by not in _SEGMENTS:
        raise ValueError(f"group_by must be one of {sorted(_SEGMENTS)}")
    if metric not in _METRICS:
        raise ValueError(f"metric must be one of {sorted(_METRICS)}")
    select_expr, group_expr = _SEGMENTS[group_by]
    group_clause = "d.[Year]" + (f", {group_expr}" if group_expr else "")
    sql = f"""
    SELECT {select_expr} AS segment,
           d.[Year] AS [year],
           {_METRICS[metric]} AS value,
           COUNT(DISTINCT d.MonthNumber) AS months
    FROM ({fact_source(channel)}) f
    JOIN dbo.DimDate d ON d.DateKey = f.OrderDateKey
    LEFT JOIN dbo.DimProduct p ON p.ProductKey = f.ProductKey
    LEFT JOIN dbo.DimSalesTerritory t ON t.TerritoryKey = f.TerritoryKey
    GROUP BY {group_clause}
    """
    return compute_yoy(clean_rows(run_query(sql)))


if __name__ == "__main__":
    # Press F5 in Spyder to run this quick check
    for row in yoy_growth():
        print(row)
"""Tools: sales_summary and top_products."""
from aw_mcp.db import run_query
from aw_mcp.tools.common import clean_rows, fact_source, year_filter

_GROUPS = {
    "year": "CAST(d.[Year] AS varchar(4))",
    "quarter": "CONCAT(d.[Year], '-Q', d.[Quarter])",
    "month": "CONCAT(d.[Year], '-', RIGHT('0' + CAST(d.MonthNumber AS varchar(2)), 2))",
    "category": "ISNULL(p.ProductCategoryName, 'Unknown')",
    "territory": "ISNULL(t.TerritoryName, 'Unknown')",
}
_ORDERS = {"sales": "SUM(f.LineTotal)", "units": "SUM(f.OrderQty)"}


def sales_summary(
    group_by: str = "year", year: int | None = None, channel: str = "all"
) -> list[dict]:
    """Sales, units and order count grouped by year/quarter/month/category/territory."""
    if group_by not in _GROUPS:
        raise ValueError(f"group_by must be one of {sorted(_GROUPS)}")
    expr = _GROUPS[group_by]
    where, params = year_filter(year)
    sql = f"""
    SELECT {expr} AS [{group_by}],
           SUM(f.LineTotal) AS sales,
           SUM(f.OrderQty) AS units,
           COUNT(DISTINCT f.SalesOrderNumber) AS orders
    FROM ({fact_source(channel)}) f
    JOIN dbo.DimDate d ON d.DateKey = f.OrderDateKey
    LEFT JOIN dbo.DimProduct p ON p.ProductKey = f.ProductKey
    LEFT JOIN dbo.DimSalesTerritory t ON t.TerritoryKey = f.TerritoryKey
    {where}
    GROUP BY {expr}
    ORDER BY 1
    """
    return clean_rows(run_query(sql, params))


def top_products(
    limit: int = 10, year: int | None = None, channel: str = "all", by: str = "sales"
) -> list[dict]:
    """Top products ranked by sales amount or units sold."""
    if by not in _ORDERS:
        raise ValueError(f"by must be one of {sorted(_ORDERS)}")
    limit = max(1, min(int(limit), 50))
    where, year_params = year_filter(year)
    sql = f"""
    SELECT TOP (?) p.ProductName,
           ISNULL(p.ProductCategoryName, 'Unknown') AS category,
           SUM(f.LineTotal) AS sales,
           SUM(f.OrderQty) AS units
    FROM ({fact_source(channel)}) f
    JOIN dbo.DimDate d ON d.DateKey = f.OrderDateKey
    JOIN dbo.DimProduct p ON p.ProductKey = f.ProductKey
    {where}
    GROUP BY p.ProductName, p.ProductCategoryName
    ORDER BY {_ORDERS[by]} DESC
    """
    return clean_rows(run_query(sql, (limit,) + year_params))

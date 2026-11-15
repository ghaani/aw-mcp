"""Tool: yearly KPI summary."""
from aw_mcp.db import run_query
from aw_mcp.tools.common import clean_rows, fact_source, year_filter


def build_kpi_row(r: dict) -> dict:
    """Turn raw sums (sales, units, orders, cost, months) into KPI fields.

    Pure function: no database access, so pytest can test it alone.
    """
    sales = r["sales"] or 0
    orders = r["orders"] or 0
    cost = r["cost"] or 0
    profit = sales - cost
    return {
        "year": int(r["year"]),
        "months": int(r["months"]),
        "sales": round(sales, 2),
        "units": int(r["units"] or 0),
        "orders": int(orders),
        "avg_order_value": round(sales / orders, 2) if orders else None,
        "gross_profit_est": round(profit, 2),
        "margin_pct": round(profit / sales * 100, 1) if sales else None,
    }


def kpi_summary(year: int | None = None, channel: str = "all") -> list[dict]:
    """Yearly KPIs: sales, units, orders, average order value, estimated profit."""
    where, params = year_filter(year)
    sql = f"""
    SELECT d.[Year] AS [year],
           COUNT(DISTINCT d.MonthNumber) AS months,
           SUM(f.LineTotal) AS sales,
           SUM(f.OrderQty) AS units,
           COUNT(DISTINCT f.SalesOrderNumber) AS orders,
           SUM(f.OrderQty * p.StandardCost) AS cost
    FROM ({fact_source(channel)}) f
    JOIN dbo.DimDate d ON d.DateKey = f.OrderDateKey
    LEFT JOIN dbo.DimProduct p ON p.ProductKey = f.ProductKey
    {where}
    GROUP BY d.[Year]
    ORDER BY d.[Year]
    """
    return [build_kpi_row(r) for r in clean_rows(run_query(sql, params))]


if __name__ == "__main__":
    # Press F5 in Spyder to run this quick check
    for row in kpi_summary():
        print(row)
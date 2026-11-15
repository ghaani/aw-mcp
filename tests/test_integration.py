"""Integration tests: need a reachable SQL Server. Skipped automatically otherwise."""
import pytest

from aw_mcp.db import run_query
from aw_mcp.tools.kpi import kpi_summary
from aw_mcp.tools.model import describe_model
from aw_mcp.tools.sales import sales_summary
from aw_mcp.tools.yoy import yoy_growth


def _db_available() -> bool:
    try:
        run_query("SELECT 1 AS x")
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="SQL Server not reachable")


def test_connection():
    assert run_query("SELECT 1 AS x") == [{"x": 1}]


def test_describe_model_lists_fact_tables():
    names = {r["table_name"] for r in describe_model()}
    assert {"FactInternetSales", "FactResellerSales"} <= names


def test_yoy_categories_add_up_to_total():
    totals = {r["year"]: r["value"] for r in yoy_growth()}
    by_year = {}
    for r in yoy_growth(group_by="category"):
        by_year[r["year"]] = by_year.get(r["year"], 0) + r["value"]
    for year, total in totals.items():
        assert by_year[year] == pytest.approx(total, abs=0.1)


def test_kpi_single_year():
    rows = kpi_summary(year=2024)
    assert len(rows) == 1
    assert rows[0]["year"] == 2024 and rows[0]["orders"] > 0


def test_kpi_sales_match_sales_summary():
    kpi = {r["year"]: r["sales"] for r in kpi_summary()}
    summary = {int(r["year"]): r["sales"] for r in sales_summary(group_by="year")}
    assert kpi == summary
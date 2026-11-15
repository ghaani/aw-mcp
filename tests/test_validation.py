"""Input-validation tests: these fail BEFORE any database call."""
from datetime import date
from decimal import Decimal

import pytest

from aw_mcp.db import run_query
from aw_mcp.tools.common import clean_rows, fact_source, year_filter
from aw_mcp.tools.sales import sales_summary, top_products
from aw_mcp.tools.yoy import yoy_growth


@pytest.mark.parametrize(
    "sql", ["DELETE FROM dbo.DimDate", "DROP TABLE x", "UPDATE t SET a = 1", ""]
)
def test_run_query_rejects_non_select(sql):
    with pytest.raises(ValueError):
        run_query(sql)


def test_fact_source_unknown_channel():
    with pytest.raises(ValueError):
        fact_source("store")


def test_fact_source_channels():
    assert "FactInternetSales" in fact_source("internet")
    assert "FactResellerSales" not in fact_source("internet")
    assert "UNION ALL" in fact_source("ALL")  # case-insensitive
    assert "UNION ALL" in fact_source(None)  # default is all


def test_year_filter():
    assert year_filter(None) == ("", ())
    assert year_filter(2024) == ("WHERE d.[Year] = ?", (2024,))


def test_clean_rows_makes_json_friendly():
    rows = [{"a": Decimal("1.239"), "d": date(2024, 1, 5), "n": 5}]
    assert clean_rows(rows) == [{"a": 1.24, "d": "2024-01-05", "n": 5}]


def test_tools_reject_bad_arguments():
    with pytest.raises(ValueError):
        yoy_growth(group_by="color")
    with pytest.raises(ValueError):
        yoy_growth(metric="profit")
    with pytest.raises(ValueError):
        sales_summary(group_by="color")
    with pytest.raises(ValueError):
        top_products(by="profit")
"""Pure-logic tests: no database needed."""
from aw_mcp.tools.kpi import build_kpi_row
from aw_mcp.tools.yoy import compute_yoy


def _rows(*items):
    return [
        {"segment": s, "year": y, "value": v, "months": m} for s, y, v, m in items
    ]


def _by_year(result, field):
    return {r["year"]: r[field] for r in result}


# ---------- compute_yoy ----------
TOTAL = _rows(
    ("All", 2022, 100.0, 8),
    ("All", 2023, 200.0, 12),
    ("All", 2024, 300.0, 12),
    ("All", 2025, 150.0, 6),
)


def test_yoy_growth_values():
    result = compute_yoy(TOTAL)
    assert _by_year(result, "growth_pct") == {
        2022: None,
        2023: 100.0,
        2024: 50.0,
        2025: -50.0,
    }


def test_yoy_first_year_has_no_previous():
    first = compute_yoy(TOTAL)[0]
    assert first["year"] == 2022
    assert first["prev_value"] is None


def test_yoy_comparable_only_when_both_years_complete():
    result = compute_yoy(TOTAL)
    assert _by_year(result, "comparable") == {
        2022: False,
        2023: False,  # previous year (2022) has only 8 months
        2024: True,
        2025: False,  # 2025 has only 6 months
    }


def test_yoy_zero_previous_value_gives_no_growth():
    result = compute_yoy(_rows(("All", 2023, 0.0, 12), ("All", 2024, 100.0, 12)))
    assert result[1]["growth_pct"] is None


def test_yoy_segments_are_independent():
    rows = _rows(
        ("A", 2023, 100.0, 12),
        ("A", 2024, 200.0, 12),
        ("B", 2023, 50.0, 12),
        ("B", 2024, 25.0, 12),
    )
    growth = {(r["segment"], r["year"]): r["growth_pct"] for r in compute_yoy(rows)}
    assert growth[("A", 2024)] == 100.0
    assert growth[("B", 2024)] == -50.0


def test_yoy_segment_missing_previous_year():
    rows = _rows(("A", 2023, 100.0, 12), ("A", 2024, 200.0, 12), ("B", 2024, 80.0, 12))
    b_2024 = [r for r in compute_yoy(rows) if r["segment"] == "B"][0]
    assert b_2024["prev_value"] is None
    assert b_2024["comparable"] is False


# ---------- build_kpi_row ----------
def _raw(**overrides):
    base = {
        "year": 2024,
        "months": 12,
        "sales": 1000.0,
        "units": 10,
        "orders": 4,
        "cost": 800.0,
    }
    base.update(overrides)
    return base


def test_kpi_basic_row():
    row = build_kpi_row(_raw())
    assert row["avg_order_value"] == 250.0
    assert row["gross_profit_est"] == 200.0
    assert row["margin_pct"] == 20.0
    assert row["units"] == 10 and row["orders"] == 4


def test_kpi_rounding():
    row = build_kpi_row(_raw(orders=3, cost=666.67))
    assert row["avg_order_value"] == 333.33
    assert row["margin_pct"] == 33.3


def test_kpi_zero_orders_and_sales():
    row = build_kpi_row(_raw(sales=0.0, orders=0, cost=0.0))
    assert row["avg_order_value"] is None
    assert row["margin_pct"] is None


def test_kpi_none_values_become_zero():
    row = build_kpi_row(_raw(sales=None, units=None, orders=None, cost=None))
    assert row["sales"] == 0
    assert row["units"] == 0
    assert row["orders"] == 0


def test_kpi_negative_profit():
    row = build_kpi_row(_raw(sales=100.0, cost=150.0))
    assert row["gross_profit_est"] == -50.0
    assert row["margin_pct"] == -50.0
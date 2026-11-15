"""MCP server entry point. Run with: python -m aw_mcp.server"""
import functools
import logging

from mcp.server.mcpserver import MCPServer

from aw_mcp.logging_config import setup_logging

from aw_mcp.tools import kpi, model, sales, yoy

logger = logging.getLogger(__name__)
mcp = MCPServer("aw-mcp", version="0.1.0")


def _logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Tool called: %s %s", func.__name__, kwargs)
        try:
            return func(*args, **kwargs)
        except Exception:
            logger.exception("Tool failed: %s", func.__name__)
            raise

    return wrapper


@mcp.tool()
@_logged
def describe_model() -> list[dict]:
    """List every table in the AdventureWorksDW_Custom warehouse with its row
    count and columns. Call this first to understand what data is available."""
    return model.describe_model()


@mcp.tool()
@_logged
def sales_summary(
    group_by: str = "year", year: int | None = None, channel: str = "all"
) -> list[dict]:
    """Sales amount, units and order count.
    group_by: year, quarter, month, category or territory.
    year: optional calendar year filter, e.g. 2024.
    channel: internet, reseller or all."""
    return sales.sales_summary(group_by=group_by, year=year, channel=channel)


@mcp.tool()
@_logged
def top_products(
    limit: int = 10, year: int | None = None, channel: str = "all", by: str = "sales"
) -> list[dict]:
    """Top products ranked by sales amount or units.
    limit: how many products (1-50).
    year: optional calendar year filter.
    channel: internet, reseller or all.
    by: sales or units."""
    return sales.top_products(limit=limit, year=year, channel=channel, by=by)


@mcp.tool()
@_logged
def yoy_growth(
    group_by: str = "total", metric: str = "sales", channel: str = "all"
) -> list[dict]:
    """Year-over-year growth of sales or units.
    group_by: total, category or territory.
    metric: sales or units.
    channel: internet, reseller or all.
    Each row has growth_pct versus the previous year. comparable is false when
    either year does not cover all 12 months (a partial year), so read
    growth_pct with care and mention it to the user."""
    return yoy.yoy_growth(group_by=group_by, metric=metric, channel=channel)


@mcp.tool()
@_logged
def kpi_summary(year: int | None = None, channel: str = "all") -> list[dict]:
    """Yearly KPIs: sales, units, orders, average order value, estimated
    gross profit and margin.
    year: optional calendar year filter, e.g. 2024 (omit for all years).
    channel: internet, reseller or all.
    months is how many months of data that year has; gross_profit_est is an
    estimate (sales minus quantity times standard cost)."""
    return kpi.kpi_summary(year=year, channel=channel)



def main() -> None:
    setup_logging()
    logger.info("Starting aw-mcp server")
    mcp.run()


if __name__ == "__main__":
    main()

"""MCP server entry point. Run with: python -m aw_mcp.server"""
import functools
import logging

from mcp.server.fastmcp import FastMCP

from aw_mcp.logging_config import setup_logging
from aw_mcp.tools import model, sales

logger = logging.getLogger(__name__)
mcp = FastMCP("aw-mcp")


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


def main() -> None:
    setup_logging()
    logger.info("Starting aw-mcp server")
    mcp.run()


if __name__ == "__main__":
    main()

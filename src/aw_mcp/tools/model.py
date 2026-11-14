"""Tool: describe the data model (tables, columns, row counts)."""
from aw_mcp.db import run_query

_SQL = """
SELECT
    s.name AS schema_name,
    t.name AS table_name,
    (SELECT SUM(p.rows) FROM sys.partitions p
      WHERE p.object_id = t.object_id AND p.index_id IN (0, 1)) AS row_count,
    (SELECT STRING_AGG(c.name + ' (' + ty.name + ')', ', ')
            WITHIN GROUP (ORDER BY c.column_id)
       FROM sys.columns c
       JOIN sys.types ty ON ty.user_type_id = c.user_type_id
      WHERE c.object_id = t.object_id) AS columns
FROM sys.tables t
JOIN sys.schemas s ON s.schema_id = t.schema_id
ORDER BY s.name, t.name
"""


def describe_model() -> list[dict]:
    """Return every table with its row count and column list."""
    return run_query(_SQL)

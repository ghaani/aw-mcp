"""Logging setup. Never writes to stdout (stdout is reserved for the MCP protocol)."""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(
    os.getenv("AW_MCP_LOG_DIR", Path(__file__).resolve().parents[2] / "logs")
)
_configured = False


def setup_logging(level: str | None = None) -> None:
    global _configured
    if _configured:
        return
    level_name = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        LOG_DIR / "aw_mcp.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level_name)
    root.addHandler(file_handler)
    root.addHandler(stderr_handler)
    _configured = True

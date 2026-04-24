from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table


class OutputRenderer:
    def __init__(self, mode: str = "interactive") -> None:
        self.mode = mode
        self.console = Console(width=200)

    def render_items(self, rows) -> None:
        if self.mode == "json":
            print(json.dumps([row.model_dump() for row in rows], separators=(",", ":")))
            return
        table = Table(title="Files")
        table.add_column("Name")
        table.add_column("Modified")
        table.add_column("By")
        table.add_column("Path")
        for row in rows:
            table.add_row(
                row.name,
                row.last_modified_at or "",
                row.last_modified_by or "",
                row.path or "",
            )
        self.console.print(table)

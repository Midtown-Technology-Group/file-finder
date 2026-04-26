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
        table.add_column("Type")
        table.add_column("Name")
        table.add_column("Modified")
        table.add_column("By")
        table.add_column("Path")
        for row in rows:
            table.add_row(
                "Folder" if row.is_folder else "File",
                row.name,
                row.last_modified_at or "",
                row.last_modified_by or "",
                row.path or "",
            )
        self.console.print(table)

    def render_status(self, payload) -> None:
        if self.mode == "json":
            print(json.dumps(payload.model_dump(), separators=(",", ":")))
            return
        summary = f"{payload.action}: {payload.name} ({payload.item_id})"
        if payload.destination_id:
            summary += f" -> {payload.destination_id}"
        self.console.print(summary)

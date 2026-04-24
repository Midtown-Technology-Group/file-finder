from __future__ import annotations

from urllib.parse import quote

from file_finder_cli.models import DriveItemCard


class FileRepository:
    def __init__(self, client) -> None:
        self.client = client

    def recent(self, limit: int) -> list[DriveItemCard]:
        payload = self.client.get("/me/drive/recent", params={"$top": limit})
        return self._parse_items(payload.get("value", []))

    def search(self, query: str, limit: int) -> list[DriveItemCard]:
        encoded = quote(query, safe="")
        payload = self.client.get(f"/me/drive/root/search(q='{encoded}')", params={"$top": limit})
        return self._parse_items(payload.get("value", []))

    def _parse_items(self, rows: list[dict]) -> list[DriveItemCard]:
        items = []
        for row in rows:
            modifier = ((row.get("lastModifiedBy") or {}).get("user") or {}).get("displayName")
            parent_path = (row.get("parentReference") or {}).get("path")
            items.append(
                DriveItemCard(
                    id=row["id"],
                    name=row.get("name") or "Unnamed",
                    web_url=row.get("webUrl"),
                    size=row.get("size"),
                    path=parent_path,
                    last_modified_at=row.get("lastModifiedDateTime"),
                    last_modified_by=modifier,
                )
            )
        return items

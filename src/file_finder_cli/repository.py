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

    def make_folder(self, name: str, parent_id: str | None = None) -> DriveItemCard:
        path = f"/me/drive/items/{parent_id}/children" if parent_id else "/me/drive/root/children"
        payload = self.client.post(
            path,
            {
                "name": name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename",
            },
        )
        return self._map_item(payload)

    def rename(self, item_id: str, name: str) -> DriveItemCard:
        payload = self.client.patch(f"/me/drive/items/{item_id}", {"name": name})
        return self._map_item(payload)

    def move(self, item_id: str, destination_id: str) -> DriveItemCard:
        payload = self.client.patch(
            f"/me/drive/items/{item_id}",
            {"parentReference": {"id": destination_id}},
        )
        return self._map_item(payload)

    def delete(self, item_id: str) -> None:
        self.client.delete(f"/me/drive/items/{item_id}")

    def _parse_items(self, rows: list[dict]) -> list[DriveItemCard]:
        return [self._map_item(row) for row in rows]

    @staticmethod
    def _map_item(row: dict) -> DriveItemCard:
        modifier = ((row.get("lastModifiedBy") or {}).get("user") or {}).get("displayName")
        parent_path = (row.get("parentReference") or {}).get("path")
        return DriveItemCard(
            id=row["id"],
            name=row.get("name") or "Unnamed",
            web_url=row.get("webUrl"),
            size=row.get("size"),
            path=parent_path,
            last_modified_at=row.get("lastModifiedDateTime"),
            last_modified_by=modifier,
            is_folder="folder" in row,
        )

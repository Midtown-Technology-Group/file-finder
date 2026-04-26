from __future__ import annotations

from file_finder_cli.models import FileActionResult


class FileFinderService:
    def __init__(self, repo) -> None:
        self.repo = repo

    def recent(self, limit: int):
        return self.repo.recent(limit=limit)

    def search(self, query: str, limit: int):
        return self.repo.search(query=query, limit=limit)

    def make_folder(self, name: str, parent_id: str | None = None) -> FileActionResult:
        item = self.repo.make_folder(name=name, parent_id=parent_id)
        return FileActionResult(
            action="mkdir",
            item_id=item.id,
            name=item.name,
            parent_id=parent_id,
        )

    def rename(self, item_id: str, name: str) -> FileActionResult:
        item = self.repo.rename(item_id=item_id, name=name)
        return FileActionResult(
            action="rename",
            item_id=item.id,
            name=item.name,
        )

    def move(self, item_id: str, destination_id: str) -> FileActionResult:
        item = self.repo.move(item_id=item_id, destination_id=destination_id)
        return FileActionResult(
            action="move",
            item_id=item.id,
            name=item.name,
            destination_id=destination_id,
        )

    def delete(self, item_id: str) -> FileActionResult:
        self.repo.delete(item_id=item_id)
        return FileActionResult(
            action="delete",
            item_id=item_id,
            name=item_id,
        )

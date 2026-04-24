from __future__ import annotations


class FileFinderService:
    def __init__(self, repo) -> None:
        self.repo = repo

    def recent(self, limit: int):
        return self.repo.recent(limit=limit)

    def search(self, query: str, limit: int):
        return self.repo.search(query=query, limit=limit)

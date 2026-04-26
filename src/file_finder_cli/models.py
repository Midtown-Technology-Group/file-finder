from __future__ import annotations

from pydantic import BaseModel


class DriveItemCard(BaseModel):
    id: str
    name: str
    web_url: str | None = None
    size: int | None = None
    path: str | None = None
    last_modified_at: str | None = None
    last_modified_by: str | None = None
    is_folder: bool = False


class FileActionResult(BaseModel):
    action: str
    item_id: str
    name: str
    parent_id: str | None = None
    destination_id: str | None = None

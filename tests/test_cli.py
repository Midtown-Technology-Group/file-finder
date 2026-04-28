from typer.testing import CliRunner

from file_finder_cli.cli import app
from file_finder_cli.config import DEFAULT_CLIENT_ID, load_auth_config
from file_finder_cli.models import DriveItemCard, FileActionResult


class FakeService:
    def recent(self, limit: int):
        return [
            DriveItemCard(
                id="1",
                name="Q2 Proposal.docx",
                web_url="https://example.invalid/doc",
                path="/drive/root:/Shared Documents",
                last_modified_at="2026-04-24T12:00:00Z",
                last_modified_by="Alex",
            )
        ]

    def search(self, query: str, limit: int):
        return self.recent(limit)

    def make_folder(self, name: str, parent_id: str | None = None):
        return FileActionResult(action="mkdir", item_id="folder-1", name=name, parent_id=parent_id)

    def rename(self, item_id: str, name: str):
        return FileActionResult(action="rename", item_id=item_id, name=name)

    def move(self, item_id: str, destination_id: str):
        return FileActionResult(action="move", item_id=item_id, name=item_id, destination_id=destination_id)

    def delete(self, item_id: str):
        return FileActionResult(action="delete", item_id=item_id, name=item_id)


def test_recent_command_supports_json_output(monkeypatch):
    monkeypatch.setattr("file_finder_cli.cli.build_service", lambda: FakeService())
    runner = CliRunner()

    result = runner.invoke(app, ["--output", "json", "recent"])

    assert result.exit_code == 0
    assert '"name":"Q2 Proposal.docx"' in result.stdout
    assert '"last_modified_by":"Alex"' in result.stdout


def test_missing_scope_explains_required_files_permission(monkeypatch):
    monkeypatch.setattr("file_finder_cli.cli.has_required_scope", lambda: False)
    runner = CliRunner()

    result = runner.invoke(app, ["search", "proposal"])

    assert result.exit_code != 0
    assert "Files.Read" in result.stdout


def test_mkdir_command_supports_json_output(monkeypatch):
    monkeypatch.setattr("file_finder_cli.cli.build_service", lambda: FakeService())
    monkeypatch.setattr("file_finder_cli.cli.has_write_scope", lambda: True)
    runner = CliRunner()

    result = runner.invoke(app, ["--output", "json", "mkdir", "Codex Folder"])

    assert result.exit_code == 0
    assert '"action":"mkdir"' in result.stdout
    assert '"name":"Codex Folder"' in result.stdout


def test_write_scope_error_mentions_files_readwrite(monkeypatch):
    monkeypatch.setattr("file_finder_cli.cli.has_write_scope", lambda: False)
    runner = CliRunner()

    result = runner.invoke(app, ["mkdir", "Codex Folder"])

    assert result.exit_code != 0
    assert "Files.ReadWrite" in result.stdout


def test_load_auth_config_defaults_to_shared_client_id(monkeypatch):
    monkeypatch.delenv("FILE_FINDER_CLIENT_ID", raising=False)

    config = load_auth_config()

    assert config.client_id == DEFAULT_CLIENT_ID


def test_load_auth_config_allows_client_id_override(monkeypatch):
    monkeypatch.setenv("FILE_FINDER_CLIENT_ID", "11111111-1111-1111-1111-111111111112")

    config = load_auth_config()

    assert config.client_id == "11111111-1111-1111-1111-111111111112"

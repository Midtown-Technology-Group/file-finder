from typer.testing import CliRunner

from file_finder_cli.cli import app
from file_finder_cli.models import DriveItemCard


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

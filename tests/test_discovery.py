"""Discovery regressions using synthetic responses at the Graph request seam."""

from urllib.parse import unquote, urlsplit

import httpx
import pytest
from mtg_microsoft_auth import GraphClient
from typer.testing import CliRunner

from file_finder_cli.cli import app
from file_finder_cli.config import configured_scopes
from file_finder_cli.repository import FileRepository
from file_finder_cli.service import FileFinderService


@pytest.fixture
def graph(monkeypatch):
    client = GraphClient(None)
    calls = []
    pages = []

    def request(method, url, params=None, json=None):
        assert method == "GET"
        assert json is None
        calls.append((url, params))
        assert pages, "Unexpected Graph request"
        payload = pages.pop(0)
        if isinstance(payload, Exception):
            raise payload
        return httpx.Response(200, json=payload)

    monkeypatch.setattr(client, "_request_with_retry", request)
    return FileRepository(client), calls, pages


@pytest.mark.parametrize(
    ("query", "encoded"),
    [
        ("O'Neil", "O%27%27Neil"),
        ("''", "%27%27%27%27"),
        ("a/b?#&+%", "a%2Fb%3F%23%26%2B%25"),
        ("budget 2026", "budget%202026"),
        ("café", "caf%C3%A9"),
    ],
)
def test_search_escapes_odata_literal_before_path_encoding(graph, query, encoded):
    repo, calls, pages = graph
    pages.append({"value": []})

    assert repo.search(query, limit=5) == []

    url, params = calls[0]
    assert url == f"{GraphClient.BASE_URL}/me/drive/root/search(q='{encoded}')"
    assert params == {"$top": 5}
    assert urlsplit(url).query == ""
    assert urlsplit(url).fragment == ""
    literal = unquote(url).split("search(q='", 1)[1][:-2]
    assert literal.replace("''", "'") == query


def discover(repo, command, limit):
    if command == "search":
        return repo.search("proposal", limit=limit)
    return repo.recent(limit=limit)


@pytest.mark.parametrize("command", ["recent", "search"])
def test_discovery_follows_opaque_links_including_empty_pages(graph, command):
    repo, calls, pages = graph
    next_url = f"{GraphClient.BASE_URL}/me/drive/{command}?$skiptoken=a%2Bb%3D&$top=2"
    final_url = f"{GraphClient.BASE_URL}/me/drive/{command}?$skiptoken=c%252F"
    pages.extend(
        [
            {"value": [{"id": "1", "name": "first"}], "@odata.nextLink": next_url},
            {"value": [], "@odata.nextLink": final_url},
            {"value": [{"id": "2", "name": "second"}]},
        ]
    )

    rows = discover(repo, command, limit=5)

    assert [row.id for row in rows] == ["1", "2"]
    assert calls[0][1] == {"$top": 5}
    assert calls[1:] == [(next_url, None), (final_url, None)]
    assert not pages


@pytest.mark.parametrize("command", ["recent", "search"])
@pytest.mark.parametrize("first_page_size", [1, 3, 4])
def test_discovery_caps_total_and_stops_at_limit(graph, command, first_page_size):
    repo, calls, pages = graph
    next_url = f"{GraphClient.BASE_URL}/me/drive/{command}?$skiptoken=next"
    rows = [{"id": str(index), "name": "synthetic"} for index in range(6)]
    pages.extend(
        [
            {"value": rows[:first_page_size], "@odata.nextLink": next_url},
            {"value": rows[first_page_size:], "@odata.nextLink": next_url + "-unused"},
        ]
    )

    result = discover(repo, command, limit=3)

    assert [row.id for row in result] == ["0", "1", "2"]
    assert len(calls) == (2 if first_page_size < 3 else 1)


@pytest.mark.parametrize("command", ["recent", "search"])
def test_discovery_empty_terminal_page(graph, command):
    repo, calls, pages = graph
    pages.append({"value": []})

    assert discover(repo, command, limit=5) == []
    assert len(calls) == 1


@pytest.mark.parametrize("command", ["recent", "search"])
def test_cli_discovery_with_default_read_scope_returns_all_pages(
    graph, monkeypatch, command
):
    repo, calls, pages = graph
    monkeypatch.delenv("FILE_FINDER_SCOPES", raising=False)
    monkeypatch.setattr(
        "file_finder_cli.cli.build_service", lambda: FileFinderService(repo)
    )
    pages.extend(
        [
            {"value": [{"id": "1"}], "@odata.nextLink": f"{GraphClient.BASE_URL}/next"},
            {"value": [{"id": "2"}]},
        ]
    )
    args = [command, "proposal"] if command == "search" else [command]

    result = CliRunner().invoke(app, ["--output", "json", *args, "--limit", "2"])

    assert result.exit_code == 0
    assert '"id":"1"' in result.stdout
    assert '"id":"2"' in result.stdout
    assert configured_scopes() == ["Files.Read"]
    assert len(calls) == 2


@pytest.mark.parametrize("command", ["recent", "search"])
def test_cli_does_not_report_partial_success_when_next_page_fails(
    graph, monkeypatch, command
):
    repo, calls, pages = graph
    monkeypatch.delenv("FILE_FINDER_SCOPES", raising=False)
    monkeypatch.setattr(
        "file_finder_cli.cli.build_service", lambda: FileFinderService(repo)
    )
    pages.extend(
        [
            {"value": [{"id": "1"}], "@odata.nextLink": f"{GraphClient.BASE_URL}/next"},
            httpx.ConnectError("synthetic connection failure"),
        ]
    )
    args = [command, "proposal"] if command == "search" else [command]

    result = CliRunner().invoke(app, ["--output", "json", *args])

    assert result.exit_code != 0
    assert result.stdout == ""
    assert isinstance(result.exception, httpx.ConnectError)
    assert len(calls) == 2


def test_default_read_scope_still_blocks_writes_before_service_creation(monkeypatch):
    monkeypatch.delenv("FILE_FINDER_SCOPES", raising=False)

    def forbidden_service():
        pytest.fail("Write command must not create a service with default read scope")

    monkeypatch.setattr("file_finder_cli.cli.build_service", forbidden_service)
    for args in [
        ["mkdir", "synthetic"],
        ["rename", "1", "--name", "synthetic"],
        ["move", "1", "--destination-id", "2"],
        ["delete", "1"],
    ]:
        result = CliRunner().invoke(app, args)
        assert result.exit_code == 2
        assert "Files.ReadWrite" in result.stdout

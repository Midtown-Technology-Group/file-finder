"""Discovery regressions using synthetic responses at the Graph request seam."""

from urllib.parse import unquote, urlsplit

import httpx
import pytest
from mtg_microsoft_auth import GraphClient

from file_finder_cli.repository import FileRepository


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

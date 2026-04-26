from __future__ import annotations

import typer
from mtg_microsoft_auth import GraphAuthSession, GraphClient

from file_finder_cli.config import REQUIRED_SCOPE, WRITE_SCOPE, has_required_scope, has_write_scope, load_auth_config
from file_finder_cli.output import OutputRenderer
from file_finder_cli.repository import FileRepository
from file_finder_cli.service import FileFinderService

app = typer.Typer(help="Microsoft 365 file discovery and delegated file actions.")


def build_service() -> FileFinderService:
    session = GraphAuthSession(load_auth_config())
    client = GraphClient(session)
    repo = FileRepository(client)
    return FileFinderService(repo)


def _renderer(output: str) -> OutputRenderer:
    return OutputRenderer(mode=output)


def _require_scope() -> None:
    if has_required_scope():
        return
    typer.echo(
        f"This command needs {REQUIRED_SCOPE}. Set FILE_FINDER_SCOPES={REQUIRED_SCOPE} "
        "before running the file finder toy."
    )
    raise typer.Exit(code=2)


def _require_write() -> None:
    if has_write_scope():
        return
    typer.echo(
        f"This command needs {WRITE_SCOPE}. Set FILE_FINDER_SCOPES=Files.ReadWrite before running file actions."
    )
    raise typer.Exit(code=2)


@app.callback()
def root(
    ctx: typer.Context,
    output: str = typer.Option("interactive", "--output", "-o"),
) -> None:
    ctx.obj = {"output": output}


@app.command("recent")
def recent(
    ctx: typer.Context,
    limit: int = typer.Option(10, "--limit", "-n", min=1, max=100),
) -> None:
    _require_scope()
    rows = build_service().recent(limit=limit)
    _renderer(ctx.obj["output"]).render_items(rows)


@app.command("search")
def search(
    ctx: typer.Context,
    query: str,
    limit: int = typer.Option(10, "--limit", "-n", min=1, max=100),
) -> None:
    _require_scope()
    rows = build_service().search(query=query, limit=limit)
    _renderer(ctx.obj["output"]).render_items(rows)


@app.command("mkdir")
def mkdir(
    ctx: typer.Context,
    name: str,
    parent_id: str | None = typer.Option(None, "--parent-id"),
) -> None:
    _require_write()
    result = build_service().make_folder(name=name, parent_id=parent_id)
    _renderer(ctx.obj["output"]).render_status(result)


@app.command("rename")
def rename(
    ctx: typer.Context,
    item_id: str,
    name: str = typer.Option(..., "--name"),
) -> None:
    _require_write()
    result = build_service().rename(item_id=item_id, name=name)
    _renderer(ctx.obj["output"]).render_status(result)


@app.command("move")
def move(
    ctx: typer.Context,
    item_id: str,
    destination_id: str = typer.Option(..., "--destination-id"),
) -> None:
    _require_write()
    result = build_service().move(item_id=item_id, destination_id=destination_id)
    _renderer(ctx.obj["output"]).render_status(result)


@app.command("delete")
def delete(
    ctx: typer.Context,
    item_id: str,
) -> None:
    _require_write()
    result = build_service().delete(item_id=item_id)
    _renderer(ctx.obj["output"]).render_status(result)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

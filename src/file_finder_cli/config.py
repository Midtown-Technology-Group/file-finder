from __future__ import annotations

import os

from mtg_microsoft_auth import AuthConfig, AuthMode

REQUIRED_SCOPE = "Files.Read"
WRITE_SCOPE = "Files.ReadWrite"


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def configured_scopes() -> list[str]:
    raw = os.environ.get("FILE_FINDER_SCOPES", REQUIRED_SCOPE)
    return [scope.strip() for scope in raw.split(",") if scope.strip()]


def load_auth_config() -> AuthConfig:
    return AuthConfig(
        client_id=os.environ.get("FILE_FINDER_CLIENT_ID", "11111111-1111-1111-1111-111111111111"),
        tenant_id=os.environ.get("FILE_FINDER_TENANT_ID", "common"),
        scopes=configured_scopes(),
        mode=AuthMode(os.environ.get("FILE_FINDER_AUTH_MODE", "wam")),
        cache_namespace="file-finder-cli",
        allow_broker=_env_bool("FILE_FINDER_ALLOW_BROKER", True),
    )


def has_required_scope() -> bool:
    scopes = set(configured_scopes())
    return REQUIRED_SCOPE in scopes or WRITE_SCOPE in scopes


def has_write_scope() -> bool:
    return WRITE_SCOPE in set(configured_scopes())

# File Finder guidance

File Finder discovers Microsoft 365 files and performs delegated folder/file actions. Read [README](README.md), `pyproject.toml` and [pressure-test notes](PRESSURE_TEST.md). Implementation modules under `src/file_finder_cli/` separate CLI, service, repository, models and configuration.

Preserve the distinction between `recent`/`search` and writes: `mkdir`, `rename`, `move`, `delete`. The default scope bundle uses `Files.ReadWrite`; possessing that scope does not authorize a mutation. Confirm the exact account, drive item, destination and requested action before live writes. Use disposable data for destructive verification and reread the affected item after an authorized action. Discovery results alone are not a cleanup plan.

Use the shared MTG Microsoft Auth application and cache without incidental identity/scope changes. Isolate tests with `MTG_AUTH_CACHE_NAMESPACE` when appropriate and preserve account selection. Never log tokens or customer document contents; fixtures must be synthetic.

Python >=3.10 and development dependencies are declared in `pyproject.toml`. Pytest discovers `tests/`; `tests/test_cli.py` uses fake services to cover output and permission boundaries. Run focused pytest checks in an isolated development environment and report what actually ran. README examples use `.\invoke.ps1`; a live search or action is not a unit test.

Windows packaging lives in `packaging/windows/`. Preserve release-tag, installer checksum/ProductCode and mtg-winget dispatch contracts. MSI installation requires administrator rights. The Sonar job can skip when its token is missing, so do not claim test coverage from that status. Keep offline tests, authorized live pressure tests, package builds and publication evidence separate.

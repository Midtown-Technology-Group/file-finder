# File Finder CLI

Read-only Microsoft 365 file discovery for the Midtown toy chest.

Project site: <https://midtown-technology-group.github.io/file-finder/>

## Required Scope

- `Files.Read`

This toy now uses the shared `MTG Shared Microsoft Auth` app registration with its dedicated read-only scope already added.

## Environment

```powershell
$env:FILE_FINDER_CLIENT_ID='e02be6f7-063a-46a6-b2cc-109d5f51055c'
$env:FILE_FINDER_TENANT_ID='a3599b15-c39c-4b41-a219-7e24dd5b5190'
$env:FILE_FINDER_SCOPES='Files.Read'
$env:FILE_FINDER_AUTH_MODE='wam'
$env:FILE_FINDER_ALLOW_BROKER='true'
```

## Usage

```powershell
.\invoke.ps1 recent --limit 10
.\invoke.ps1 search "proposal" --limit 10
.\invoke.ps1 --output json recent
```

## Commands

- `recent`: List recently accessed files.
- `search`: Search OneDrive for files by query text.

## Project Site

This repo includes a lightweight GitHub Pages site in `docs/`.

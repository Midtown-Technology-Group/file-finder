# File Finder

Microsoft 365 file discovery and delegated file actions for the Midtown toy chest.

Project site: <https://midtown-technology-group.github.io/file-finder/>

## Scope Bundles

- discovery: `Files.ReadWrite`
- file actions: `Files.ReadWrite`

This toy uses the shared `MTG Shared Microsoft Auth` app registration.

## Environment

```powershell
$env:FILE_FINDER_CLIENT_ID='e02be6f7-063a-46a6-b2cc-109d5f51055c'
$env:FILE_FINDER_TENANT_ID='a3599b15-c39c-4b41-a219-7e24dd5b5190'
$env:FILE_FINDER_SCOPES='Files.ReadWrite'
$env:FILE_FINDER_AUTH_MODE='wam'
$env:FILE_FINDER_ALLOW_BROKER='true'
```

## Usage

```powershell
.\invoke.ps1 recent --limit 10
.\invoke.ps1 search "proposal" --limit 10
.\invoke.ps1 mkdir "Codex Folder"
.\invoke.ps1 rename 012345 --name "Renamed Folder"
.\invoke.ps1 delete 012345
.\invoke.ps1 --output json recent
```

## Commands

- `recent`: List recently accessed files.
- `search`: Search OneDrive for files by query text.
- `mkdir`: Create a folder in the root drive or under a specific parent item.
- `rename`: Rename a file or folder by drive item id.
- `move`: Move a file or folder into another parent item by destination id.
- `delete`: Delete a file or folder by drive item id.

## Project Site

This repo includes a lightweight GitHub Pages site in `docs/`.

## License

GPL-3.0-or-later.

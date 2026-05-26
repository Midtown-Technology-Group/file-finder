# Pressure-Testing File Finder

Issue #1: [Pressure-test file-finder as a real daily-driver toy](https://github.com/Midtown-Technology-Group/file-finder/issues/1)

## Goal

Use `file-finder` in real operator workflows to confirm the command surface, JSON output, and safety defaults feel right before promoting it to the main daily-driver toy lineup.

## Quick Start Test Checklist

```powershell
# Setup (run once)
$env:FILE_FINDER_CLIENT_ID='e02be6f7-063a-46a6-b2cc-109d5f51055c'
$env:FILE_FINDER_TENANT_ID='a3599b15-c39c-4b41-a219-7e24dd5b5190'
$env:FILE_FINDER_SCOPES='Files.ReadWrite'
$env:FILE_FINDER_AUTH_MODE='wam'
$env:FILE_FINDER_ALLOW_BROKER='true'

# Daily-driver commands to test

## 1. Recent file recall (daily)
.\invoke.ps1 recent --limit 10
.\invoke.ps1 recent --limit 25

## 2. Targeted OneDrive search (as needed)
.\invoke.ps1 search "proposal" --limit 10
.\invoke.ps1 search "2026-05 invoice" --limit 5

## 3. Lightweight folder organization (weekly)
.\invoke.ps1 mkdir "Archive/2026-Q2"
.\invoke.ps1 move 0123456789 --to 9876543210

## 4. Safe disposable-item cleanup (monthly)
.\invoke.ps1 --output json recent --limit 50 | ConvertFrom-Json | Where-Object { $_.lastModified -lt (Get-Date).AddDays(-90) }
.\invoke.ps1 delete 0123456789  # use with care!
```

## Feedback to Capture

| Area | Question | Your Notes |
|------|----------|------------|
| **Search quality** | Does search find what you expect? Rank well? | |
| **Path targeting** | Is move/rename targeting intuitive? | |
| **Naming** | Are command names (`mkdir`, `rename`, `move`) natural? | |
| **Move semantics** | Is the `--to` parameter for move clear? | |
| **Delete safety** | Do you feel confident about what's being deleted? | |
| **JSON output** | Is the JSON structure useful for piping? | |
| **WAM auth** | Does shared token cache work across toys? | |

## Acceptance Criteria

- [ ] Used `file-finder` in at least 3 real operator sessions
- [ ] Captured feedback in the table above
- [ ] Identified any friction points or UX improvements
- [ ] Confirmed or adjusted the daily-driver toy lineup status

## Reporting Results

Add your findings as comments on Issue #1, or open a PR with improvements to:
- This `PRESSURE_TEST.md` document
- README.md usage examples
- Command UX or safety defaults

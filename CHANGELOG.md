# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.1] - 2026-07-19

### Fixed
- Fixed a bug where splitting a bill that didn't divide evenly among people (e.g. $100 split 3 ways) could freeze the app in an infinite loop. The settlement algorithm now does its math in integer cents instead of floating-point dollars, which was the source of the rounding drift, and the loop is now hard-capped so it can never hang.

## [1.0.0] - 2026-07-18

### Added
- Core expense-splitting logic: total, fair share, individual balances, and a greedy settlement algorithm that minimizes the number of payments needed.
- Command-line version (`cli/expense_splitter.py`).
- Web app version (`web/`) with the same logic and a receipt-styled UI.
- English and Persian translations, loaded from JSON locale files in both versions.
- Right-to-left layout support for Persian in the web app.
- Progressive Web App support (installable on Android and iOS, offline-capable via a service worker).

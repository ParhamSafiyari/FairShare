# Changelog

All notable changes to this project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-07-18

### Added
- Core expense-splitting logic: total, fair share, individual balances, and a greedy settlement algorithm that minimizes the number of payments needed.
- Command-line version (`cli/expense_splitter.py`).
- Web app version (`web/`) with the same logic and a receipt-styled UI.
- English and Persian translations, loaded from JSON locale files in both versions.
- Right-to-left layout support for Persian in the web app.
- Progressive Web App support (installable on Android and iOS, offline-capable via a service worker).

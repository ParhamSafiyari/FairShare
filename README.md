# FairShare

Split a group bill fairly, in English or Persian — as a command-line tool or as an installable web app.

FairShare figures out:
- The total amount spent
- Everyone's fair share
- Who's owed money and who owes money
- The smallest possible set of payments needed to settle up (so nobody sends five separate 3-dollar transfers)

## What's in this repo

```
fairshare/
├── cli/                  Command-line version (Python)
│   ├── expense_splitter.py
│   └── locales/          Translations (en.json, fa.json)
│
└── web/                   Installable web app (PWA)
    ├── index.html
    ├── manifest.json
    ├── service-worker.js
    ├── icons/
    └── locales/           Translations (en.json, fa.json)
```

## CLI version

Requires Python 3.

```bash
cd cli
python3 expense_splitter.py
```

You'll be asked to pick a language, then enter each person's name and amount paid (type `done` when finished).

## Web app (installable on Android & iOS)

The `web/` folder is a Progressive Web App — visit it in a browser and it can be installed to a phone's home screen like a native app, including offline support.

### Run it locally

Browsers block `fetch()` on local `file://` pages, so serve the folder instead of double-clicking `index.html`:

```bash
cd web
python3 -m http.server 8000
```

Then open `http://localhost:8000` in a browser.

### Publish it (GitHub Pages)

1. Push this repo to GitHub.
2. Go to **Settings → Pages**.
3. Set the source to the `web/` folder on your default branch.
4. GitHub will give you a live HTTPS URL — that's what makes it installable (PWAs require HTTPS).

Once live:
- **Android (Chrome)**: an "Install app" prompt appears automatically.
- **iOS (Safari)**: tap the Share icon → **Add to Home Screen**.

## Adding a new language

Both versions load their text from JSON files instead of hardcoding it, so adding a language doesn't require touching the app logic:

1. Copy `en.json` to e.g. `de.json` in the relevant `locales/` folder.
2. Translate each value (keep the `{placeholders}` like `{name}` and `{amount:.2f}` intact).
3. For the CLI, add the new option in `choose_language()` in `expense_splitter.py`.
4. For the web app, add a button in the language toggle and a `setLang('de')` call in `index.html`.

## Roadmap

This is v1.0.0 — a solid first release. Ideas for future versions:
- Uneven splitting (not everyone owes the same share)
- Currency selection
- Saving/loading a bill from a file
- Exporting the settlement as an image to share in a group chat
- Packaging the web app for the Play Store / App Store via Capacitor

## License

MIT — see [LICENSE](LICENSE).

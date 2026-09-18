# CampusCompass

A lightweight MVP college recommendation quiz that asks whether a user is a first-time freshman or a transfer student, then ranks schools based on stated preferences and transfer-specific pain points.

## Features

- Freshman and transfer tracks
- Weighted school matching logic
- Ranked top-5 recommendations with percentage matches
- Transfer-specific pain-point deductions
- Simple explainable result cards

## Run locally

From the project folder, start a local static server:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000
```

## Files

- `index.html` — app shell
- `styles.css` — styling
- `app.js` — quiz flow and scoring logic

## Notes

This is a prototype MVP for concept validation and can be extended with real school data, a more advanced scoring model, and a production backend.

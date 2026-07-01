# Native Sons Retail Availability Portal

Public-facing portal showing this week's retail plant availability at Native Sons Wholesale Nursery.

## Files

- `index.html` — the portal page (open in browser)
- `availability_data.js` — current week's data (regenerate from PDF)
- `availability.json` — same data in JSON for editing
- `parse_pdf.py` — parser that converts the weekly PDF to JSON
- `cleanup_ocr.py` — fixes common OCR errors in the parsed data
- `deploy.sh` — one-shot deploy to GitHub Pages

## Regenerate from a new PDF

1. Drop the latest `natsons*.pdf` (Native Sons weekly availability) into this folder
2. Edit the `PDF = ...` line in `parse_pdf.py`
3. Run the parser:
   ```
   /Users/tfross/.hermes/hermes-agent/venv/bin/python parse_pdf.py
   ```
4. Run the OCR cleanup (applies ~14 known fixes):
   ```
   /Users/tfross/.hermes/hermes-agent/venv/bin/python cleanup_ocr.py
   ```
5. Re-deploy with `./deploy.sh` (see below)

## Deploy to GitHub Pages

```
GITHUB_TOKEN=ghp_xxxxx ./deploy.sh
```

The script:
- Creates the repo if it doesn't exist (you'll be prompted)
- Uploads `index.html` and `availability_data.js` via the GitHub API
- Prints the URL to enable Pages at: https://github.com/tfross67/nativesons-retail/settings/pages

## Features

- Search-first hero (botanical, common name, origin)
- Container-size chips (4", 1gal, 5gal, 15gal, 7gal, 20" boxes)
- "In bloom" filter (🌸)
- "CA native" filter
- Mobile-friendly
- Prices shown to all (matches PDF)

## Contact

- Email: orders@nativeson.com
- Phone: 805.481.5996

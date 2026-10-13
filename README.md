# India Elections – Lok Sabha 2024 + Maharashtra Assembly 2024

A static website (no server code, no build step, no dependencies).

## Run it
- **Easiest:** double-click `standalone.html` (one file, works offline) or `index.html`.
- **Local server (optional):** `python3 -m http.server 8000` in this folder, then open http://localhost:8000
- **Deploy anywhere:** upload the whole folder to Netlify / Vercel / GitHub Pages / Cloudflare Pages / any web host
  (S3, Apache, Nginx). Publish directory = this folder. No build command.

## What is where
| Path | Purpose |
|---|---|
| `index.html` | Main app. Loads big files (maps, Maharashtra data) only when needed. |
| `standalone.html` | Same site as one self-contained file. |
| `css/style.css`, `js/app.js` | Styles and application code |
| `js/data-ls.js`, `js/data-mh.js` | Result data (Lok Sabha 2024, Maharashtra 2024) |
| `js/geo-ls.js`, `js/geo-mh.js` | Map outlines (loaded on demand) |
| `js/symbols.js` | Party symbols (embedded images, ECI names, official image URLs) |
| `js/i18n.js` | Translations (English, Hindi, Marathi) |
| `data/India_Elections_Data.xlsx` | All website data as a formatted Excel workbook (formulas included) |
| `data/*.json` | Same data as JSON |

## Update the data
1. Edit the Excel sheets (or regenerate from ECI reports).
2. Export to the JSON/JS structure in `js/data-*.js` (see the `.json` files for the exact shape).

## Add a language
Open `js/i18n.js`, copy the `hi` block to a new key (e.g. `ta`), translate the values, then add
`<option value="ta">தமிழ்</option>` to the language `<select id="lg">` in both HTML files.
Constituency, candidate and party names are shown as published by ECI (English).

## Party symbols
Pages try official symbol images from Wikimedia (needs internet) and fall back to embedded images
(37 parties) and then to emoji. Without internet you still see the embedded images.

## Credits / sources
Election Commission of India (results), DataMeet (constituency boundaries), Wikimedia Commons (symbols),
public party-symbol dataset (embedded fallbacks).

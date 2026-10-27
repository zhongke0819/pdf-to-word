# PDF to Word

A PDF to Word converter website: upload PDF files, convert them to editable
`.docx` documents, download the results. The interface layout is inspired by
the general structure of online converter pages (header, tool card, steps,
features, FAQ); all copy on this site is original.

## Conversion engine

Server-side conversion uses the open-source
[pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) library (MIT).
The page auto-detects the backend: when the API answers, conversion runs on
the server (high fidelity); when it does not, the page falls back to
browser-side conversion (PDF.js text extraction + docx.js, text-focused,
needs internet access for the CDN libraries).

## Features

- Drag-and-drop or click to select, multiple PDF files, one-by-one conversion
- Per-file download, 50 MB per-file limit on the server
- 6 interface languages: English, 简体中文， Español, Português, Français,
  Deutsch — browser-language auto-match with English fallback, switchable
  from the top-right menu, choice remembered in localStorage
- SEO: per-language Title / Description / keywords that switch with the
  language, Open Graph + Twitter tags, JSON-LD WebApplication, `?lang=`
  share links (canonical / hreflang absolute URLs still need a real domain
  at deploy time)
- Uploaded files and converted outputs are deleted from the server after
  the download finishes

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install pdf2docx fastapi uvicorn python-multipart
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Then open http://127.0.0.1:8001. (`run_server.sh` does the same using the
shared venv in `../pdf2docx-test/.venv`, when present.)

## API

- `GET /api/health` → `{"ok": true, "engine": "pdf2docx"}`
- `POST /api/convert` (multipart field `file`, PDF only) → the `.docx` file

## Standalone page

`app/static/index.html` also works on its own when opened in a browser
(browser conversion mode only). Set `app/static/config.js` (`window.API_BASE`)
to the backend URL when the frontend and backend are deployed separately.

## Known limitations

- Scanned PDFs (pages that are just images) need OCR, which is not
  supported yet — only PDFs with selectable text convert.
- PDF to Word is a re-layout, not a perfect copy: simple single-column
  documents (especially Chinese) convert cleanly; English word spacing can
  partly merge on old-style typography, and complex multi-column layouts
  may duplicate content when rebuilt as tables. Complex documents may need
  manual touch-ups.
- Browser conversion mode depends on CDN libraries (PDF.js, docx.js).

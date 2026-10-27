#!/bin/bash
# PDF to Word website server (port 8001).
# Reuses the pdf2docx venv prepared in ../pdf2docx-test (same pattern as
# pdf2zh-mvp reusing the pdf2zh-demo venv): no second install needed.
set -e
cd "$(dirname "$0")"
VENV="../pdf2docx-test/.venv/bin/python"
if [ ! -x "$VENV" ]; then
  echo "pdf2docx venv not found at $VENV" >&2
  echo "Run: python3 -m venv ../pdf2docx-test/.venv && ../pdf2docx-test/.venv/bin/pip install pdf2docx fastapi uvicorn" >&2
  exit 1
fi
"$VENV" -c "import fastapi, uvicorn, multipart" 2>/dev/null || "$VENV" -m pip install -q fastapi uvicorn python-multipart
exec "$VENV" -m uvicorn app.main:app --host 127.0.0.1 --port 8001

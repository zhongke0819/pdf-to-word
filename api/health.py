"""Vercel Serverless Function: health check for the PDF to Word site.

The frontend calls this to decide between server conversion and its
browser fallback. `engine` tells the page which server engine is live:
`pymupdf-slim` (this Vercel function) vs `pdf2docx` (the FastAPI backend).
"""
import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        body = json.dumps({"ok": True, "engine": "pymupdf-slim"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

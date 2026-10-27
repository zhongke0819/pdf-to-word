"""PDF to Word website backend.

Engine: open-source pdf2docx (ArtifexSoftware/pdf2docx, MIT).
Serves the static frontend from app/static and exposes:
  GET  /api/health   -> {"ok": true}
  POST /api/convert  -> multipart PDF upload, returns the converted .docx
Uploaded files and outputs are deleted after the response is sent.
"""
import os
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

MAX_BYTES = 50 * 1024 * 1024  # 50 MB per file

app = FastAPI(title="PDF to Word")

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/api/health")
def health():
    return {"ok": True, "engine": "pdf2docx"}


@app.post("/api/convert")
def convert(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    workdir = Path(tempfile.mkdtemp(prefix="pdf2word-"))
    src = workdir / f"{uuid.uuid4().hex}.pdf"
    dst = workdir / f"{Path(file.filename).stem}.docx"
    try:
        size = 0
        with open(src, "wb") as out:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_BYTES:
                    raise HTTPException(status_code=413, detail="File exceeds 50 MB")
                out.write(chunk)
        # pdf2docx is synchronous; FastAPI runs this def endpoint in a threadpool.
        from pdf2docx import Converter

        cv = Converter(str(src))
        try:
            cv.convert(str(dst))
        finally:
            cv.close()
        if not dst.exists() or dst.stat().st_size == 0:
            raise HTTPException(status_code=500, detail="Conversion produced no output")
    except HTTPException:
        shutil.rmtree(workdir, ignore_errors=True)
        raise
    except Exception as exc:  # noqa: BLE001 - surface converter errors as 500
        shutil.rmtree(workdir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {exc}") from exc

    def cleanup():
        shutil.rmtree(workdir, ignore_errors=True)

    return FileResponse(
        path=str(dst),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=dst.name,
        background=BackgroundTask(cleanup),
    )


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

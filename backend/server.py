"""Aegis FastAPI backend: scan registration, SSE streaming, report + export."""
from __future__ import annotations
import json, uuid, pathlib
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
import config, pipeline, export
from schemas import ValidationReport

app = FastAPI(title="Aegis — Agentic Validation", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["http://localhost:5176", "http://127.0.0.1:5176"],
    allow_methods=["*"], allow_headers=["*"],
)

# In-memory scan registry: scanId -> {source, use_case, spec, categories, report?}
SCANS: dict[str, dict] = {}

def _persist(report: dict) -> None:
    sid = report.get("scan_id")
    if not sid:
        return
    try:
        (config.HISTORY_DIR / f"{sid}.json").write_text(json.dumps(report))
    except Exception:
        pass

def _load_report(scan_id: str) -> dict | None:
    entry = SCANS.get(scan_id)
    if entry and entry.get("report"):
        return entry["report"]
    p = config.HISTORY_DIR / f"{scan_id}.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return None
    return None

@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "model": config.MODEL, "keyConfigured": bool(config.api_key()),
            "allowFolder": config.ALLOW_FOLDER}

@app.post("/api/scan")
async def create_scan(request: Request):
    """Accepts either JSON {folderPath|githubUrl, useCase} or multipart with a zip `file`."""
    ct = request.headers.get("content-type", "")
    file_bytes = None; filename = None
    folder_path = github_url = use_case = spec = None
    categories = None
    if "application/json" in ct:
        data = await request.json()
        folder_path = data.get("folderPath"); github_url = data.get("githubUrl")
        use_case = data.get("useCase"); spec = data.get("spec")
        categories = data.get("categories")
    else:  # multipart/form-data (zip upload) or urlencoded
        form = await request.form()
        up = form.get("file")
        if up is not None and hasattr(up, "read"):
            file_bytes = await up.read(); filename = getattr(up, "filename", None)
        folder_path = form.get("folderPath"); github_url = form.get("githubUrl")
        use_case = form.get("useCase"); spec = form.get("spec")
        raw_cats = form.get("categories")
        if raw_cats:
            try: categories = json.loads(raw_cats)
            except Exception: categories = None

    categories = [c for c in categories if isinstance(c, str)] if isinstance(categories, list) else None
    categories = categories or None

    scan_id = uuid.uuid4().hex[:12]
    if file_bytes is not None:
        source = {"kind": "zip", "data": file_bytes, "name": filename}
    elif folder_path:
        if not config.ALLOW_FOLDER:
            raise HTTPException(400, "Local folder scanning is disabled on this deployment. "
                                     "Use a GitHub URL or a .zip upload.")
        source = {"kind": "folder", "path": folder_path}
    elif github_url:
        source = {"kind": "github", "url": github_url}
    else:
        raise HTTPException(400, "Provide a zip file, folderPath, or githubUrl.")
    SCANS[scan_id] = {"source": source, "use_case": use_case, "spec": spec,
                      "categories": categories, "report": None}
    return {"scanId": scan_id}

@app.get("/api/scan/{scan_id}/stream")
async def stream(scan_id: str):
    entry = SCANS.get(scan_id)
    if not entry:
        raise HTTPException(404, "Unknown scanId.")
    async def gen():
        async for ev in pipeline.run_scan(scan_id, entry["source"], entry["use_case"],
                                          entry.get("categories"), entry.get("spec")):
            if ev.get("type") == "report":
                entry["report"] = ev["report"]
                _persist(ev["report"])
            yield f"data: {json.dumps(ev)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.get("/api/scans")
def list_scans():
    """Past scans (persisted on disk), newest first — for the history list."""
    out = []
    for p in config.HISTORY_DIR.glob("*.json"):
        try:
            r = json.loads(p.read_text())
        except Exception:
            continue
        src = r.get("source", {}) or {}
        label = src.get("url") or src.get("path") or src.get("name") or src.get("kind", "scan")
        out.append({
            "scanId": r.get("scan_id"), "label": str(label),
            "framework": (r.get("framework") or {}).get("primary", ""),
            "overall": r.get("overall", 0), "band": (r.get("band") or {}).get("label", ""),
            "useCase": r.get("use_case"), "generatedAt": r.get("generated_at", ""),
        })
    out.sort(key=lambda x: x["generatedAt"], reverse=True)
    return out[:100]

@app.get("/api/scan/{scan_id}/report")
def report(scan_id: str):
    rep = _load_report(scan_id)
    if not rep:
        raise HTTPException(404, "Report not ready.")
    return JSONResponse(rep)

@app.get("/api/scan/{scan_id}/export")
def export_report(scan_id: str, format: str = "json"):
    stored = _load_report(scan_id)
    if not stored:
        raise HTTPException(404, "Report not ready.")
    rep = ValidationReport.model_validate(stored)
    if format == "md":
        return PlainTextResponse(export.to_markdown(rep),
            headers={"Content-Disposition": f'attachment; filename="aegis-{scan_id}.md"'})
    return PlainTextResponse(export.to_json(rep), media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="aegis-{scan_id}.json"'})

# Serve the built frontend (single-image deploys). API routes above take precedence;
# this catch-all mount serves index.html + assets. Absent in local dev (Vite serves the UI).
_DIST = pathlib.Path(__file__).resolve().parent.parent / "dist"
if _DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="static")

if __name__ == "__main__":
    import uvicorn, os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", os.getenv("AEGIS_PORT", "8000"))))

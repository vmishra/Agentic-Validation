"""Materialize a submission into a sandboxed workspace dir. Safety-first."""
from __future__ import annotations
import io, shutil, subprocess, zipfile, pathlib
import config

class IngestError(Exception):
    pass

def _workspace(scan_id: str) -> pathlib.Path:
    ws = config.SCAN_ROOT / scan_id / "workspace"
    if ws.exists():
        shutil.rmtree(ws, ignore_errors=True)
    ws.mkdir(parents=True, exist_ok=True)
    return ws

def ingest_zip(data: bytes, scan_id: str) -> pathlib.Path:
    if len(data) > config.ZIP_MAX_COMPRESSED:
        raise IngestError("Zip too large (compressed).")
    ws = _workspace(scan_id)
    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        raise IngestError("Not a valid .zip file.")
    total = 0
    infos = zf.infolist()
    if len(infos) > config.ZIP_MAX_FILES:
        raise IngestError("Zip has too many files.")
    for info in infos:
        total += info.file_size
        if total > config.ZIP_MAX_UNCOMPRESSED:
            raise IngestError("Zip too large (uncompressed).")
        target = (ws / info.filename).resolve()
        if not target.is_relative_to(ws.resolve()):
            raise IngestError("Unsafe path in zip (zip-slip).")
    zf.extractall(ws)
    return ws

def ingest_folder(path: str, scan_id: str) -> pathlib.Path:
    src = pathlib.Path(path).expanduser()
    if not src.exists() or not src.is_dir():
        raise IngestError(f"Folder not found or not a directory: {path}")
    ws = _workspace(scan_id)
    def _ignore(_d, names):
        return [n for n in names if n in config.IGNORE_DIRS]
    shutil.copytree(src, ws, dirs_exist_ok=True, ignore=_ignore, symlinks=False)
    return ws

def ingest_github(url: str, scan_id: str) -> pathlib.Path:
    if not (url.startswith("https://") and "github.com" in url):
        raise IngestError("Only public https github.com URLs are supported.")
    ws = _workspace(scan_id)
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(ws)],
            check=True, capture_output=True, timeout=config.CLONE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        raise IngestError("git clone timed out.")
    except subprocess.CalledProcessError as e:
        raise IngestError(f"git clone failed: {e.stderr.decode()[:200]}")
    shutil.rmtree(ws / ".git", ignore_errors=True)
    return ws

def cleanup(scan_id: str) -> None:
    shutil.rmtree(config.SCAN_ROOT / scan_id, ignore_errors=True)

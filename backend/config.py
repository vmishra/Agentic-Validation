"""Central config: env, model, ingest caps, ignore sets, paths."""
from __future__ import annotations
import os, pathlib, tempfile
from dotenv import load_dotenv

load_dotenv()  # loads backend/../.env when run from repo root via app.sh; harmless otherwise
load_dotenv(pathlib.Path(__file__).resolve().parent.parent / ".env")

MODEL = os.getenv("AEGIS_MODEL", "gemini-3.5-flash")

# ADK's internal google-genai client reads GOOGLE_API_KEY; mirror our GEMINI_API_KEY
# into it so the AI Studio (Developer API) path works without per-call wiring.
if os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "false")

def api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

IGNORE_DIRS = {
    # vcs / editor
    ".git", ".svn", ".hg", ".idea", ".vscode",
    # deps / virtualenvs
    "node_modules", ".venv", "venv", "env", "vendor", "site-packages",
    # build / output / caches
    "dist", "build", ".next", "out", "target", "coverage", ".turbo", ".cache",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox", ".eggs",
    ".terraform", ".gradle", ".parcel-cache", ".svelte-kit", ".nuxt",
}
IGNORE_EXTS = {
    # media / archives / fonts / binaries
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".pdf", ".zip",
    ".gz", ".tar", ".tgz", ".rar", ".7z", ".mp4", ".mov", ".mp3", ".wav",
    ".woff", ".woff2", ".ttf", ".otf", ".eot", ".so", ".dylib", ".dll",
    ".bin", ".exe", ".pyc", ".pyo", ".class", ".o", ".a", ".map", ".lock",
    # data dumps / logs (noise for code validation, big context bloat)
    ".log", ".csv", ".tsv", ".parquet", ".db", ".sqlite", ".sqlite3", ".npy", ".pkl",
}
# Specific noisy files skipped by basename: lockfiles bloat context with zero signal.
IGNORE_FILES = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "npm-shrinkwrap.json",
    "go.sum", "Cargo.lock", "poetry.lock", "Pipfile.lock", "composer.lock",
    "Gemfile.lock", "bun.lockb", ".DS_Store",
}
MAX_FILE_BYTES = 1_000_000
ZIP_MAX_COMPRESSED = 50_000_000
ZIP_MAX_UNCOMPRESSED = 300_000_000
ZIP_MAX_FILES = 20_000
CLONE_TIMEOUT_S = 60
RUN_TIMEOUT_S = int(os.getenv("AEGIS_RUN_TIMEOUT", "300"))  # backstop for very large repos

SCAN_ROOT = pathlib.Path(os.getenv("AEGIS_SCAN_ROOT", tempfile.gettempdir())) / "aegis-scans"
SCAN_ROOT.mkdir(parents=True, exist_ok=True)

# Completed reports persist here (survives restarts) so past scans can be re-opened.
HISTORY_DIR = pathlib.Path(
    os.getenv("AEGIS_HISTORY_DIR", str(pathlib.Path(__file__).resolve().parent.parent / ".aegis-history"))
)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

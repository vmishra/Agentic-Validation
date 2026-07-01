"""Walk a workspace into a bounded EvidencePack (deterministic, no LLM)."""
from __future__ import annotations
import json, pathlib
import config, detectors
from schemas import EvidencePack, DepInfo

_LANG_BY_EXT = {
    ".py": "python", ".ipynb": "notebook", ".ts": "typescript", ".tsx": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".go": "go", ".java": "java", ".kt": "kotlin", ".rb": "ruby", ".rs": "rust",
    ".cs": "csharp", ".php": "php", ".scala": "scala", ".swift": "swift",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp", ".sql": "sql",
    ".sh": "shell", ".bash": "shell", ".zsh": "shell",
    ".md": "markdown", ".mdx": "markdown", ".rst": "text",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".cfg": "config", ".ini": "config", ".env": "config",
    ".tf": "terraform", ".proto": "proto", ".gradle": "gradle",
}
# Known extension-less files worth reading (build/agent config, instructions).
_KEEP_NAMES = {
    "Dockerfile", "Makefile", "Procfile", "Containerfile",
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules", ".env.example",
}

def _iter_paths(workspace: pathlib.Path):
    for p in sorted(workspace.rglob("*")):
        if not p.is_file():
            continue
        if any(part in config.IGNORE_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in config.IGNORE_EXTS:
            continue
        if p.name in config.IGNORE_FILES:
            continue
        if p.name.endswith((".min.js", ".min.css", ".bundle.js", ".chunk.js")):
            continue
        try:
            if p.stat().st_size > config.MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        yield p

def read_files(workspace: pathlib.Path) -> dict[str, str]:
    """Read text files of any format (incl. hidden dotfiles). Binary content is
    detected by a NUL-byte sniff and skipped regardless of extension, so unknown
    or extension-less files are handled without corrupting the evidence."""
    out: dict[str, str] = {}
    for p in _iter_paths(workspace):
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if b"\x00" in data[:8192]:  # binary file — skip
            continue
        out[str(p.relative_to(workspace))] = data.decode("utf-8", errors="ignore")
    return out

def build_file_tree(workspace: pathlib.Path, max_entries: int = 400) -> str:
    lines, n = [], 0
    for p in _iter_paths(workspace):
        rel = p.relative_to(workspace)
        lines.append("  " * (len(rel.parts) - 1) + rel.name)
        n += 1
        if n >= max_entries:
            lines.append("… (truncated)")
            break
    return "\n".join(lines)

def parse_deps(files: dict[str, str]) -> DepInfo:
    for manifest in ("requirements.txt", "pyproject.toml", "package.json"):
        if manifest in files:
            pkgs: list[dict] = []
            txt = files[manifest]
            if manifest == "package.json":
                try:
                    data = json.loads(txt)
                    for sect in ("dependencies", "devDependencies"):
                        for name, ver in (data.get(sect) or {}).items():
                            pkgs.append({"name": name, "version": str(ver)})
                except Exception:
                    pass
            else:
                for line in txt.splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        nm = line.split("==")[0].split(">=")[0].split("[")[0].strip()
                        if nm:
                            pkgs.append({"name": nm, "version": line})
            return DepInfo(manifest=manifest, packages=pkgs[:200])
    return DepInfo()

def build_evidence(workspace: pathlib.Path) -> EvidencePack:
    files = read_files(workspace)
    languages: dict[str, int] = {}
    total_loc = 0
    size_bytes = 0
    for rel, text in files.items():
        loc = text.count("\n") + 1
        total_loc += loc
        size_bytes += len(text.encode("utf-8", errors="ignore"))
        lang = _LANG_BY_EXT.get(pathlib.Path(rel).suffix.lower(), "other")
        languages[lang] = languages.get(lang, 0) + loc
    signals = detectors.find_signals(files)
    signals["deps"] = parse_deps(files).model_dump()
    return EvidencePack(
        file_count=len(files), total_loc=total_loc, languages=languages, size_bytes=size_bytes,
        framework=detectors.detect_framework(files), file_tree=build_file_tree(workspace),
        signals=signals,
    )

def compact_evidence(ev: EvidencePack, max_per_signal: int = 40,
                     max_excerpt: int = 160, max_chars: int = 24000) -> str:
    """A bounded JSON view of the evidence for LLM prompts. Caps per-signal counts
    and excerpt lengths so large/varied repos never blow the model's context window."""
    sig: dict = {}
    for k, v in (ev.signals or {}).items():
        if isinstance(v, list):
            items = []
            for it in v[:max_per_signal]:
                it = dict(it)
                if isinstance(it.get("excerpt"), str):
                    it["excerpt"] = it["excerpt"][:max_excerpt]
                items.append(it)
            sig[k] = items
            if len(v) > max_per_signal:
                sig[f"{k}_truncated"] = len(v) - max_per_signal
        else:
            sig[k] = v  # e.g. deps dict
    compact = {
        "file_count": ev.file_count, "total_loc": ev.total_loc,
        "languages": ev.languages, "framework": ev.framework,
        "file_tree": ev.file_tree[:4000], "signals": sig,
    }
    s = json.dumps(compact)
    if len(s) > max_chars:  # second pass: drop excerpts to fit
        for v in sig.values():
            if isinstance(v, list):
                for it in v:
                    it.pop("excerpt", None)
        compact["file_tree"] = ev.file_tree[:1500]
        s = json.dumps(compact)[:max_chars]
    return s

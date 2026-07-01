"""Workspace-scoped read_file tool for Analyst agents (ADK FunctionTool)."""
from __future__ import annotations
import pathlib

def make_read_file(workspace: pathlib.Path):
    root = workspace.resolve()
    def read_file(path: str, start_line: int = 1, end_line: int = 400) -> str:
        """Read lines [start_line, end_line] of a file in the scanned workspace.

        Args:
            path: workspace-relative file path.
            start_line: 1-indexed first line (inclusive).
            end_line: 1-indexed last line (inclusive); capped to +400 of start.
        Returns:
            The requested slice with line numbers, or an error string.
        """
        try:
            target = (root / path).resolve()
        except Exception:
            return "Access denied: bad path."
        if not target.is_relative_to(root):
            return "Access denied: path escapes the workspace."
        if not target.is_file():
            return f"Not found: {path}"
        end = min(end_line, start_line + 400)
        lines = target.read_text(errors="ignore").splitlines()
        slice_ = lines[max(0, start_line - 1): end]
        return "\n".join(f"{start_line + i}: {ln}" for i, ln in enumerate(slice_))
    return read_file

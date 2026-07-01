import os, pathlib, pytest
import pipeline

pytestmark = pytest.mark.skipif(
    not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
    reason="no Gemini API key configured",
)

@pytest.mark.asyncio
async def test_full_scan_over_fixture():
    fixture = str(pathlib.Path(__file__).parent / "fixtures" / "adk_repo")
    types_seen, report = set(), None
    async for ev in pipeline.run_scan("live1", {"kind": "folder", "path": fixture},
                                      "An ADK agent that answers questions with web search."):
        types_seen.add(ev["type"])
        if ev["type"] == "report":
            report = ev["report"]
    assert "report" in types_seen and "done" in types_seen
    assert report and 0.0 <= report["overall"] <= 1.0
    assert len(report["categories"]) == 7
    assert any(f["category"] == "security" for f in report["findings"])

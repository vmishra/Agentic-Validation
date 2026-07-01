import os, pytest

pytestmark = pytest.mark.skipif(
    not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
    reason="no Gemini API key configured",
)

def test_read_file_tool_is_scoped(tmp_path):
    from agents.tools import make_read_file
    (tmp_path / "a.py").write_text("line1\nline2\nline3\n")
    rf = make_read_file(tmp_path)
    out = rf("a.py", 1, 2)
    assert "line1" in out and "line3" not in out
    assert "denied" in rf("../secret", 1, 1).lower()

@pytest.mark.asyncio
async def test_adk_minimal_run():
    # Verifies the installed ADK API end-to-end against gemini-3.5-flash.
    from google.adk.agents import LlmAgent
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    agent = LlmAgent(name="ping", model=os.getenv("AEGIS_MODEL", "gemini-3.5-flash"),
                     instruction="Reply with the single word: pong.")
    runner = InMemoryRunner(agent=agent, app_name="aegis-smoke")
    session = await runner.session_service.create_session(app_name="aegis-smoke", user_id="u")
    text = ""
    async for event in runner.run_async(
        user_id="u", session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text="ping")]),
    ):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    text += p.text
    assert "pong" in text.lower()

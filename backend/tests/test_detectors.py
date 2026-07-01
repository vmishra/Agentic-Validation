import detectors

def test_detect_adk_framework():
    files = {"agent.py": "from google.adk import Agent\nroot_agent = Agent(model='gemini-3.5-flash')"}
    fw = detectors.detect_framework(files)
    assert fw["primary"] == "google-adk"

def test_detect_claude_sdk():
    files = {"main.py": "from anthropic import Anthropic\nclient = Anthropic()"}
    assert detectors.detect_framework(files)["primary"] == "anthropic"

def test_find_model_ids():
    files = {"a.py": "model='gemini-3.5-flash'\nMODEL = \"gpt-4o-mini\""}
    ids = detectors.find_signals(files)["model_ids"]
    found = {s["name"] for s in ids}
    assert "gemini-3.5-flash" in found and "gpt-4o-mini" in found

def test_find_hardcoded_secret():
    # Synthetic, non-functional value used only to exercise the secret detector.
    fake = "AIza" + "Sy" + ("0" * 35)  # matches the pattern; not a real credential
    files = {"c.py": f"GEMINI_API_KEY = '{fake}'"}  # gitleaks:allow pragma: allowlist secret
    secrets = detectors.find_signals(files)["secrets"]
    assert len(secrets) >= 1 and "AIza" not in secrets[0]["excerpt"]  # value masked

def test_detect_more_frameworks():
    assert detectors.detect_framework({"a.py": "from crewai import Agent, Crew"})["primary"] == "crewai"
    assert detectors.detect_framework({"a.py": "import dspy\nclass X(dspy.Module): pass"})["primary"] == "dspy"
    assert detectors.detect_framework({"x.ts": "import { generateText } from 'ai'"})["primary"] == "vercel-ai"

def test_find_loops_and_termination():
    files = {"l.py": "while True:\n    if done: break\n"}
    loops = detectors.find_signals(files)["loops"]
    assert loops and loops[0]["meta"].get("has_termination") is True

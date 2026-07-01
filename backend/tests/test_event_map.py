from agents.coordinator import event_to_sse, reset_seen
from types import SimpleNamespace as NS

def test_dispatch_event_from_author():
    reset_seen()
    ev = NS(author="auditor_security", content=None, get_function_calls=lambda: [],
            grounding_metadata=None)
    out = event_to_sse(ev)
    assert any(e["type"] == "dispatch" and e["category"] == "security" for e in out)

def test_tool_event_from_function_call():
    reset_seen()
    fc = NS(name="google_search", args={"q": "x"})
    ev = NS(author="research", content=None, get_function_calls=lambda: [fc],
            grounding_metadata=None)
    out = event_to_sse(ev)
    assert any(e["type"] == "tool" and e["tool"] == "google_search" for e in out)

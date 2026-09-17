"""Suite-wide fixtures: make tests independent of whether Office happens to be open on this machine.

Tests that exercise the Office guard monkeypatch tundlekit.render.office_running themselves, which overrides this.
"""
import pytest


@pytest.fixture(autouse=True)
def _office_closed(monkeypatch):
    try:
        import tundlekit.render as render
    except Exception:  # render not importable in this environment: nothing to patch
        return
    monkeypatch.setattr(render, "office_running", lambda *a, **k: [])

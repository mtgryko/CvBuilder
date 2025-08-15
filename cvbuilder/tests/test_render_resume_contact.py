import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.latex import render_resume

def test_render_resume_missing_email():
    contact = {"name": "John Doe", "phone": "+1 234 567 890"}
    tex = render_resume(contact, [], [], [], [])
    assert "John Doe" in tex
    assert "mailto" not in tex


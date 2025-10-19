"""
Path: tests/test_actions_form.py
"""

import os
import sys
import asyncio

# Ensure project root is on sys.path so `src.*` imports work during tests
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from rasa_sdk.executor import CollectingDispatcher
from src.infrastructure.rasa.actions.actions import ValidateInstalarRasaForm


class MinimalTracker:
    """Lightweight tracker replacement for unit tests.

    Provides only the attributes/methods used by the form validation code:
    - latest_message (dict)
    - active_loop (dict or None)
    - slots storage and get_slot(name)
    """
    def __init__(self, latest_message=None, slots=None, active_loop=None):
        self.latest_message = latest_message or {}
        self.active_loop = active_loop
        self._slots = slots or {}

    def get_slot(self, name):
        "Get the value of a slot by name."
        return self._slots.get(name)


class DummyDispatcher(CollectingDispatcher):
    "Dummy dispatcher to capture messages sent during tests."
    pass # pylint:  disable=unnecessary-pass


def test_no_extraction_outside_form():
    "Test that no extraction occurs when form is not active."
    action = ValidateInstalarRasaForm()
    # Simulate a message mentioning git but not inside form
    latest_message = {"intent": {"name": None}, "text": "Tengo git instalado"}
    tracker = MinimalTracker(latest_message=latest_message, slots={"requested_slot": None}, active_loop=None)
    res = asyncio.run(action.extract_git_instalado(DummyDispatcher(), tracker, {}))
    assert res == {}, "Should not extract git_instalado when form not active"


def test_extraction_inside_form_requested_slot():
    "Test that extraction occurs when form is active and requested_slot matches."
    action = ValidateInstalarRasaForm()
    latest_message = {"intent": {"name": "afirmar"}, "text": "Sí, lo tengo"}
    # active_loop is a dict with name
    tracker = MinimalTracker(latest_message=latest_message, slots={"requested_slot": "git_instalado"}, active_loop={"name": "instalar_rasa_form"})
    res = asyncio.run(action.extract_git_instalado(DummyDispatcher(), tracker, {}))
    assert res == {"git_instalado": "si"}


def test_validate_proyecto_descargado_unrecognized():
    "Test that unrecognized input for proyecto_descargado slot is handled."
    action = ValidateInstalarRasaForm()
    tracker = MinimalTracker(latest_message={"text": "no se"}, slots={"requested_slot": "proyecto_descargado"}, active_loop={"name": "instalar_rasa_form"})
    dispatcher = DummyDispatcher()
    out = asyncio.run(action.validate_proyecto_descargado("tal vez", dispatcher, tracker, {}))
    assert out.get("proyecto_descargado") is None
    # expect dispatcher to have asked again
    messages = [m.get("text") or m.get("response") for m in dispatcher.messages]
    assert any("proyecto" in (m or "") for m in messages)

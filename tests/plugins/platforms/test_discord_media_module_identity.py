"""Media sends must use the adapter module the gateway loaded, not a second copy.

2026-09-25: discord.py was missing at boot, the lazy install re-bound
``discord`` in ``hermes_plugins.<slug>.adapter`` only, and adapter_media's
``from plugins.platforms.discord.adapter import discord`` got a second copy
still holding None — every file send failed while text worked.
"""

import sys
import types

from plugins.platforms.discord.adapter_media import DiscordMediaMixin, _adapter_attrs


def test_reads_the_loaded_copy_not_a_stale_alias(monkeypatch):
    live = types.ModuleType("hermes_plugins.platforms__discord.adapter")
    live.discord = object()
    live._prompt_target_id = lambda chat_id, metadata: chat_id
    stale = types.ModuleType("plugins.platforms.discord.adapter")
    stale.discord = None
    stale._prompt_target_id = live._prompt_target_id
    monkeypatch.setitem(sys.modules, live.__name__, live)
    monkeypatch.setitem(sys.modules, stale.__name__, stale)

    Adapter = type("DiscordAdapter", (DiscordMediaMixin,), {"__module__": live.__name__})
    _, discord = _adapter_attrs(Adapter(), "_prompt_target_id", "discord")
    assert discord is live.discord


def test_subclass_elsewhere_falls_back_through_the_mro(monkeypatch):
    live = types.ModuleType("hermes_plugins.platforms__discord.adapter")
    live.discord = object()
    monkeypatch.setitem(sys.modules, live.__name__, live)
    Adapter = type("DiscordAdapter", (DiscordMediaMixin,), {"__module__": live.__name__})
    Fake = type("FakeAdapter", (Adapter,), {"__module__": __name__})
    (discord,) = _adapter_attrs(Fake(), "discord")
    assert discord is live.discord

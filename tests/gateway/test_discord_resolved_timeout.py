"""Resolved Discord prompts must not be relabeled as expired by a late timeout."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from plugins.platforms.discord.adapter import (
    ClarifyChoiceView,
    ChoicePickerView,
    ExecApprovalView,
    ModelPickerView,
    SlashConfirmView,
    UpdatePromptView,
)


@pytest.mark.parametrize(
    "view_class",
    [
        ExecApprovalView,
        SlashConfirmView,
        UpdatePromptView,
        ModelPickerView,
        ClarifyChoiceView,
        ChoicePickerView,
    ],
)
def test_resolved_view_timeout_does_not_overwrite_answer(view_class):
    view = view_class.__new__(view_class)
    child = SimpleNamespace(disabled=False)
    view.children = [child]
    view.resolved = True
    view._message = SimpleNamespace(embeds=[], edit=AsyncMock())

    asyncio.run(view.on_timeout())

    assert child.disabled is False
    view._message.edit.assert_not_awaited()


@pytest.mark.parametrize(
    "view_class",
    [
        ExecApprovalView,
        SlashConfirmView,
        UpdatePromptView,
        ModelPickerView,
        ClarifyChoiceView,
    ],
)
def test_unresolved_view_timeout_still_expires(view_class):
    view = view_class.__new__(view_class)
    child = SimpleNamespace(disabled=False)
    view.children = [child]
    view.resolved = False
    view._message = None

    asyncio.run(view.on_timeout())

    assert view.resolved is True
    if view_class is ModelPickerView:
        assert view.children == []
    else:
        assert child.disabled is True

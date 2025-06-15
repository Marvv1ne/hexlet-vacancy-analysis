import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from telegram import Update
from telegram.ext import ConversationHandler
from asgiref.sync import sync_to_async

from app.telegram_bot.telegram_bot import start, subscribe, settings, set_frontend, set_backend, done, CHOOSE_PROF, CHOOSE_FRONT, CHOOSE_BACK
from app.telegram_bot.models import TgUser


def build_update(message_text, username="testuser"):
    mock_message = MagicMock()
    mock_message.text = message_text
    mock_message.reply_text = AsyncMock()

    mock_user = MagicMock()
    mock_user.username = username

    update = MagicMock()
    update.message = mock_message
    update.effective_user = mock_user

    return update, mock_message


@pytest.mark.asyncio
async def test_start():
    update, message = build_update("/start")
    context = MagicMock()

    await start(update, context)

    message.reply_text.assert_awaited_once_with("Привет testuser, введите /subscribe")


@pytest.mark.asyncio
@patch("app.telegram_bot.telegram_bot.save_to_db", new_callable=AsyncMock)
async def test_subscribe(mock_save_to_db):
    update, message = build_update("/subscribe")
    context = MagicMock()

    await subscribe(update, context)

    mock_save_to_db.assert_awaited_once_with("testuser")
    message.reply_text.assert_awaited_once_with("Вы подписаны на рассылку, введете /settings для настройки фильтра")


@pytest.mark.asyncio
async def test_settings():
    update, message = build_update("/settings")
    context = MagicMock()

    state = await settings(update, context)

    assert state == CHOOSE_PROF
    message.reply_text.assert_awaited()
    args, kwargs = message.reply_text.await_args
    assert "Choose profession" in args[0]


@pytest.mark.asyncio
async def test_set_frontend_first_choice():
    update, message = build_update("React")
    context = MagicMock()
    context.user_data = {}

    state = await set_frontend(update, context)

    assert state == CHOOSE_FRONT
    assert context.user_data["frontend"] == ["React"]
    message.reply_text.assert_awaited()


@pytest.mark.asyncio
async def test_set_frontend_second_choice():
    update, message = build_update("Vue.js")
    context = MagicMock()
    context.user_data = {"frontend": ["React"]}

    state = await set_frontend(update, context)

    assert state == CHOOSE_FRONT
    assert context.user_data["frontend"] == ["React", "Vue.js"]
    message.reply_text.assert_awaited()


@pytest.mark.asyncio
async def test_set_backend():
    update, message = build_update("Python")
    context = MagicMock()
    context.user_data = {}

    state = await set_backend(update, context)

    assert state == CHOOSE_BACK
    assert context.user_data["backend"] == ["Python"]
    message.reply_text.assert_awaited()


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_done_creates_user_and_clears_data():
    update, message = build_update("Done")
    context = MagicMock()
    context.user_data = {"frontend": ["React"], "backend": ["Python"]}

    state = await done(update, context)

    assert state == ConversationHandler.END
    message.reply_text.assert_awaited()

    exists = await sync_to_async(TgUser.objects.filter(username="testuser").exists)()
    assert exists

    
from django.test import TestCase
from asgiref.sync import sync_to_async
from unittest.mock import MagicMock, patch
from telegram import Update, Message, Chat, User, ReplyKeyboardRemove
import unittest.mock

from app.telegram_bot.models import TgUser
from app.telegram_bot.handlers import start, subscribe
from app.telegram_bot.state_machine import settings, show_settings, delete_settings, confirm_delete, select_profession, select_frontend_stack, select_backend_stack, finish_selection, cancel_selection, back_to_previose_stage, done, exit, set_interval
from app.telegram_bot.keyboards import (
    markup_filters, markup_front, markup_backend,
    markup_settings, markup_interval
)

class TestCommadHandlers(TestCase):
    def setUp(self):
        self.chat = MagicMock(spec=Chat, id=123)
        self.user = MagicMock(spec=User, username="TestUser", id=456)
        self.message = MagicMock(spec=Message, chat=self.chat, text="/start")
        self.effective_user = MagicMock()
        
        self.update = MagicMock(spec=Update, message=self.message, effective_user=self.user)
        self.context = MagicMock()

        self.start_message = MagicMock(spec=Message, text="/start", chat=self.chat)
        self.subscribe_message = MagicMock(spec=Message, text="/subscribe", chat=self.chat)
        self.settings_message = MagicMock(spec=Message, text="/settings", chat=self.chat)

        self.start_update = MagicMock(spec=Update, message=self.start_message, effective_user=self.user)
        self.subscribe_update = MagicMock(spec=Update, message=self.subscribe_message, effective_user=self.user)
        self.settings_update = MagicMock(spec=Update, message=self.settings_message, effective_user=self.user)
    
    async def test_start(self):
        await start(self.update, self.context)        
        self.message.reply_text.assert_called_once_with("Привет TestUser, введите /subscribe чтобы подписаться на рассылку вакансий")
    
    async def test_subscribe(self):
        await subscribe(self.update, self.context)
        self.message.reply_text.assert_called_once_with("Вы подписаны на рассылку вакансий, введете /settings для настройки фильтра")

        user = await sync_to_async(TgUser.objects.get, thread_sensitive=True)(username="TestUser")
        self.assertEqual(user.username, "TestUser")
    
    async def test_settings(self):
        await subscribe(self.subscribe_update, self.context)
        await settings(self.settings_update, self.context)               

        self.settings_message.reply_text.assert_called_with("Тут вы можете настроить свои фильтры", reply_markup=markup_settings)

    # Тест пустых настроек
    async def test_show_settings(self):
        await subscribe(self.subscribe_update, self.context)
        await show_settings(self.update, self.context)
        self.message.reply_text.assert_called_with('У вас еще нет натроенного фильтра вакансий')

    async def test_delete_settings_no_subscription(self):
        await subscribe(self.update, self.context)     
        await delete_settings(self.update, self.context)
        self.message.reply_text.assert_called_with("Нет сохранённых настроек для удаления.", reply_markup=markup_settings)
    
    async def test_cancel_selection(self):
        self.context.user_data = {'step': 'frontend'}
        await cancel_selection(self.update, self.context)
        self.assertEqual(self.context.user_data, {})
        self.message.reply_text.assert_called_with("Вы сбросили настройки.", reply_markup=markup_settings)

    async def test_finish_selection(self):
        self.context.user_data = {'step': 'backend', 'backend_stack': {'Python', 'Java'}}
        await finish_selection(self.update, self.context)
        self.message.reply_text.assert_called_with("Выберите интервал получения уведомлений:", reply_markup=markup_interval)
        self.assertEqual(self.context.user_data['step'], 'interval')

    async def test_exit(self):
        self.context.user_data = {'step': 'settings'}
        await exit(self.update, self.context)
        self.message.reply_text.assert_called_with("Выход из настроек фильтра", reply_markup=unittest.mock.ANY)
        self.assertEqual(self.context.user_data, {})
    
    
    async def test_set_interval(self):
        await subscribe(self.subscribe_update, self.context)
        self.context.user_data = {'step': 'backend', 'backend_stack': {'Python', 'Java'}}
        await finish_selection(self.update, self.context)
        self.message.text = 'minute'
        await set_interval(self.update, self.context)
        self.message.reply_text.assert_called_with(
            f"Ваши настройки сохранены:\n"
            f"Фильтры: Python, Java\n"
            f"Интервал: minute\n",
            reply_markup=unittest.mock.ANY)


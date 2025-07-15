from django.test import TestCase
from unittest.mock import MagicMock
from telegram import Update, Message, Chat, User
from app.telegram_bot.handlers import start

class TestCommadHandlers(TestCase):
    def setUp(self):
        self.chat = MagicMock(spec=Chat, id=123)
        self.user = MagicMock(spec=User, username="TestUser", id=456)
        self.message = MagicMock(spec=Message, chat=self.chat, text="/start")
        self.effective_user = MagicMock()
        
        self.update = MagicMock(spec=Update, message=self.message, effective_user=self.user)
        self.context = MagicMock()
    
    async def test_start_reply_async(self):
        # Оборачиваем вызов в await, т.к. start теперь async
        await start(self.update, self.context)
        
        # Проверяем ответ
        self.message.reply_text.assert_called_once_with("Привет TestUser, введите /subscribe")
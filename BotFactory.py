
import telebot
import os
import dotenv


class BotFactory:

    def __init__(self):
        dotenv.load_dotenv()
        API_KEY = os.getenv('API_KEY')
        self.bot = telebot.TeleBot(API_KEY)

    def get_bot_instance(self):
        return self.bot

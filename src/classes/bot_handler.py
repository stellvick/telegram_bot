import os
from types import NoneType

import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from utils.log_utils import LogUtils


class BotHandler:
    def __init__(self, db):
        # Banco de Dados
        self.db = db
        # Listas
        self.knownUsers = []
        self.commands = {
            'start': 'Bem vindo ao Bot de OS',
            'help': 'Mostra os comandos disponíveis',
            'menu': 'Mostra o menu principal'
        }

        # self.bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
        self.bot = telebot.TeleBot("7085043888:AAH0mibd9RzsKIpI4ZpG1liQ3GLJ1iTegds")

        # Log
        self.logger = LogUtils()
        self.logger.start()
        self.bot.set_update_listener(self.listener)

        # Comandos
        self.bot.message_handler(commands=['start'])(self.command_start)
        self.bot.message_handler(commands=['menu'])(self.main_menu)
        # self.bot.message_handler(commands=['cry'])(self.sign_handler)
        # self.bot.message_handler(commands=['category'])(self.cat_list)

        # Menus
        # self.bot.callback_query_handler(func=lambda call: True)(self.commandshandlebtn)

        # Em caso de não encontrar um comando, ele irá chamar a função echo_all
        self.bot.message_handler(func=lambda msg: True)(self.echo_all)

    def echo_all(self, message):
        self.bot.reply_to(message, message.text)

    def listener(self, messages):
        for m in messages:
            if m.content_type == 'text':
                self.logger.log_info(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

    def command_start(self, m):
        cid = m.chat.id
        if cid not in self.knownUsers:
            self.bot.send_message(cid, "Bem Vindo ao Bot de OS!")
            sent_msg = self.bot.send_message(cid, "Por favor informe o seu email!")
            self.bot.register_next_step_handler(sent_msg, self.email_handler)
        else:
            self.bot.send_message(cid, "Bem Vindo de Volta!")
            self.main_menu(m)

    def email_handler(self, message):
        email = message.text
        user = self.db.find_user(email)
        if user is None:
            self.bot.send_message(message.chat.id, "Email não cadastrado!")
            sent_msg = self.bot.send_message(message.chat.id, "Por favor informe um email correto!")
            self.bot.register_next_step_handler(sent_msg, self.email_handler)
        else:
            self.bot.send_message(message.chat.id, "Aguarde!!!")
            self.db.insert_chat_id(message.chat.id, email)
            self.get_all_users()
            self.main_menu(message)

    def command_help(self, m):
        cid = m.chat.id
        help_text = "Os comandos disponíveis são:\n"
        for key in self.commands:
            help_text += "/" + key + ": "
            help_text += self.commands[key] + "\n"
        self.bot.send_message(cid, help_text)  # send the generated help page

    def main_menu(self, message):
        reply_markup = InlineKeyboardMarkup()
        reply_markup.row_width = 1
        reply_markup.add(InlineKeyboardButton("Novo", callback_data=""))
        reply_markup.add(InlineKeyboardButton("Consultar", callback_data=""))
        reply_markup.add(InlineKeyboardButton("Editar", callback_data=""))
        self.bot.send_message(
            chat_id=message.chat.id,
            text="""Escolha uma opção""",
            reply_markup=reply_markup
        )

    def cat_list(self, message):
        keyboard = [
            [
                KeyboardButton("ACTION 🦹🏼‍♀️", callback_data=""),
                KeyboardButton("ADVENTURE ⛰", callback_data="")
            ],
            [
                KeyboardButton("BOARD 🧩", callback_data=""),
                KeyboardButton("CARD 🃏", callback_data="")
            ],
            [
                KeyboardButton("COMPETITIVE 🏆", callback_data=""),
                KeyboardButton("CASUAL 👨‍👩‍👦‍👦", callback_data="")
            ],
            [
                KeyboardButton("GAMBLE 🎰", callback_data=""),
                KeyboardButton("PUZZLE 🤔", callback_data="")
            ],
            [
                KeyboardButton("RACING 🏎", callback_data=""),
                KeyboardButton("SIMULATION 🚜", callback_data="")
            ],
            [
                KeyboardButton("SPORT 🎳", callback_data=""),
                KeyboardButton("TRIVIA ❔", callback_data="")
            ],
            [
                KeyboardButton("MAIN MENU 🔙", callback_data=self.games_main_menu)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.bot.send_message(chat_id=message.chat_id, text="""What Games Do You Like? 😍""",
                              reply_markup=reply_markup)

    def get_all_users(self):
        users = self.db.find_known_users()
        if type(users) is not NoneType:
            self.knownUsers = users

    def run(self):
        self.get_all_users()
        self.bot.infinity_polling()

    def end(self):
        self.bot.stop_polling()

import os
from types import NoneType

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from classes.user import User
from utils.log_utils import LogUtils


class BotHandler:
    def __init__(self, db):
        # Banco de Dados
        self.db = db
        # Listas
        self.knownUsers: list[User] = []
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
        self.bot.message_handler(commands=['help'])(self.command_help)
        self.bot.message_handler(commands=['menu'])(self.main_menu)

        # CallBacks
        self.bot.callback_query_handler(func=lambda call: True)(self.handle_menu)

        # Em caso de não encontrar um comando, ele irá chamar a função echo_all
        self.bot.message_handler(func=lambda msg: True)(self.echo_all)

    def echo_all(self, message):
        self.bot.reply_to(message, "Não entendi o que você disse!")

    def listener(self, messages):
        for m in messages:
            if m.content_type == 'text':
                self.logger.log_info(str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text)

    def command_start(self, m):
        cid = m.chat.id
        user = self.get_user(cid)
        if user is None:
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
        keyboard = [
            [InlineKeyboardButton("Novo", callback_data='novo')],
            [InlineKeyboardButton("Consultar", callback_data='consultar')],
            [InlineKeyboardButton("Editar", callback_data='editar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.bot.send_message(message.chat.id, "Escolha uma opção...", reply_markup=reply_markup)

    def handle_menu(self, query):
        try:
            if query.data == 'novo':
                self.bot.answer_callback_query(query.id)
                self.bot.send_message(query.message.chat.id, "Novo")
            elif query.data == 'consultar':
                self.bot.answer_callback_query(query.id)
                res = self.db.consulta(self.get_user(query.message.chat.id))
                lista = []
                for item in res:
                    lista.append(InlineKeyboardButton(item[0], callback_data=item[0]))
                # self.bot.delete_message(query.message.chat.id, query.message.message_id)
                # self.bot.send_message(query.message.chat.id, "Ultimas OS", reply_markup=InlineKeyboardMarkup(lista))
                self.bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id,
                                                   reply_markup=InlineKeyboardMarkup(lista))
            elif query.data == 'editar':
                self.bot.answer_callback_query(query.id)
                self.bot.send_message(query.message.chat.id, "Editar")
            else:
                self.bot.answer_callback_query(query.id, "Ação não encontrada!")
        except Exception as e:
            self.logger.log_error(e)

    def get_all_users(self):
        res = self.db.find_known_users()
        if type(res) is not NoneType:
            users = []
            for user in res:
                new = User(uid=user[0], chat_id=user[1])
                users.append(new)
            self.knownUsers = users

    def get_user(self, chat_id):
        for user in self.knownUsers:
            if user.chat_id == chat_id:
                return user
        return None

    def run(self):
        self.get_all_users()
        self.bot.infinity_polling()

    def end(self):
        self.bot.stop_polling()


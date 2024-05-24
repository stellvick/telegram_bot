import os
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from utils.log_utils import LogUtils


class BotHandler:
    def __init__(self):
        # Listas
        self.knownUsers = []
        self.userStep = {}
        self.commands = {
            'start': 'Get used to the bot',
            'help': 'Gives you information about the available commands',
            'sendLongText': 'A test using the \'send_chat_action\' command',
            'getImage': 'A test using multi-stage messages, custom keyboard, and media sending'
        }

        # self.bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
        self.bot = telebot.TeleBot("7085043888:AAH0mibd9RzsKIpI4ZpG1liQ3GLJ1iTegds")

        # Log
        self.logger = LogUtils()
        self.logger.start()
        self.bot.set_update_listener(self.listener)

        # Comandos
        self.bot.message_handler(commands=['start', 'hello'])(self.command_start)
        self.bot.message_handler(commands=['cry'])(self.sign_handler)
        self.bot.message_handler(commands=['games'])(self.games_main_menu)
        self.bot.message_handler(commands=['category'])(self.cat_list)

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

    def get_user_step(self, uid):
        if uid in self.userStep:
            return self.userStep[uid]
        else:
            self.knownUsers.append(uid)
            self.userStep[uid] = 0
            self.logger.log_info("New user detected, who hasn't used \"/start\" yet")
            return 0

    def command_start(self, m):
        cid = m.chat.id
        if cid not in self.knownUsers:  # if user hasn't used the "/start" command yet:
            self.knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
            self.userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" comm
            self.bot.send_message(cid, "Hello, stranger, let me scan you...")
            self.bot.send_message(cid, "Scanning complete, I know you now")
            self.command_help(m)  # show the new user the help page
        else:
            self.bot.send_message(cid, "I already know you, no need for me to scan you again!")

    def command_help(self, m):
        cid = m.chat.id
        help_text = "The following commands are available: \n"
        for key in self.commands:  # generate help text out of the commands dictionary defined at the top
            help_text += "/" + key + ": "
            help_text += self.commands[key] + "\n"
        self.bot.send_message(cid, help_text)  # send the generated help page

    def sign_handler(self, message):
        text = ("To shutdown \nChoose one: *Aries*, *Taurus*, *Gemini*, *Cancer,* *Leo*, *Virgo*, *Libra*, *Scorpio*, "
                "*Sagittarius*, *Capricorn*, *Aquarius*, and *Pisces*.")
        sent_msg = self.bot.send_message(message.chat.id, text, parse_mode="Markdown")
        self.bot.register_next_step_handler(sent_msg, self.day_handler)

    def day_handler(self, message):
        sign = message.text
        text = ("What day do you want to know?\nChoose one: *TODAY*, *TOMORROW*, *YESTERDAY*, or a date in format "
                "YYYY-MM-DD.")
        sent_msg = self.bot.send_message(
            message.chat.id, text, parse_mode="Markdown")
        self.bot.register_next_step_handler(
            sent_msg, self.end, sign.capitalize())

    def games_main_menu(self, message):
        keyboard = [
            [
                KeyboardButton("Play Solo 👤", callback_data=""),
                KeyboardButton("Play With Friends 👥", callback_data="")
            ],
            [
                KeyboardButton("CATEGORIES 🎮", callback_data="cat_button"),
                KeyboardButton("TRENDING LIST ⚡️", callback_data="trend_button")
            ],
            [
                KeyboardButton("LAST PLAYED GAMES 🔄", callback_data="prev_played_button"),
                KeyboardButton("JOIN CHANNEL 🤑", url="")
            ],
            [
                KeyboardButton("CONTACT SUPPORT 🛠", callback_data="")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Sending the message with the custom keyboard
        self.bot.send_message(
            chat_id=message.chat.id,
            text="""Alright 🏁 
                    How Would You Like to Begin: """,
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

    def run(self):
        self.bot.infinity_polling()

    def end(self):
        self.bot.stop_polling()

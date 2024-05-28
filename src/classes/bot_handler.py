from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.html_utils import strip_tags
from utils.log_utils import LogUtils
from classes.user import User
from types import NoneType
from classes.os import Os

import telebot


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

    def handle_menu(self, call):
        call_id = call.id
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        try:
            if call.data == 'novo':
                self.call_novo(call_id, chat_id, message_id)
            elif call.data == 'consultar':
                self.call_consultar(call_id, chat_id, message_id)
            elif call.data == 'editar':
                self.bot.answer_callback_query(call_id)
                self.bot.send_message(chat_id, "Editar")
            elif call.data.startswith('show'):
                self.call_show(call, call_id, chat_id, message_id)
            elif call.data.startswith('new-projeto'):
                self.create_project(call, call_id, chat_id, message_id)
            elif call.data == 'voltar':
                self.bot.answer_callback_query(call_id)
                self.bot.delete_message(chat_id=chat_id, message_id=message_id)
                self.main_menu(call.message)
            elif call.data.startswith('campo'):
                self.bot.answer_callback_query(call_id)
                campo = call.data.split('-')[1]
                user = self.get_user(chat_id)
                user.action = campo
                self.update_user(user, chat_id)
                message = f"Por favor digite o conteudo do campo {campo}:"
                self.bot.send_message(chat_id, message)
                self.bot.register_next_step_handler(call.message, self.form_handler)
            else:
                self.bot.answer_callback_query(call_id, "Ação não encontrada!")
        except Exception as e:
            print(e)
            self.logger.log_error(e)

    def form_handler(self, message):
        try:
            chat_id = message.chat.id
            user = self.get_user(chat_id)
            if user.action == "Conteudo":
                user.os.tarefas = message.text
            elif user.action == "Observação":
                user.os.observacao = message.text
            elif user.action == "RDV":
                user.os.rdv = message.text
            elif user.action == "Status":
                user.os.status = message.text
            elif user.action == "Entrada 1":
                user.os.entrada = message.text
            elif user.action == "Saída 1":
                user.os.almoco_inicio = message.text
            elif user.action == "Entrada 2":
                user.os.almoco_fim = message.text
            elif user.action == "Saída 2":
                user.os.saida = message.text
            self.update_user(user, chat_id)
            # self.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
            self.bot.edit_message_text(self.create_os_html(user.os), chat_id=chat_id, message_id=user.active,
                                       parse_mode='HTML')
        except Exception as e:
            print(e)
            self.logger.log_error(e)

    def create_project(self, call, call_id, chat_id, message_id):
        self.bot.answer_callback_query(call_id)
        projeto = call.data.split('??')[1]
        os = Os()
        os.codigo = projeto
        user = self.get_user(chat_id)
        user.active = message_id
        user.action = "start"
        user.os = os
        self.update_user(user, chat_id)
        keyboard = [
            [
                InlineKeyboardButton("Entrada 1", callback_data="campo-Entrada 1"),
                InlineKeyboardButton("Saída 1", callback_data="campo-Saída 1")
            ],
            [
                InlineKeyboardButton("Entrada 2", callback_data="campo-Entrada 2"),
                InlineKeyboardButton("Saída 2", callback_data="campo-Saída 2")
            ],
            [
                InlineKeyboardButton("Status", callback_data="campo-Status"),
                InlineKeyboardButton("RDV", callback_data="campo-RDV")
            ],
            [
                InlineKeyboardButton("Conteudo", callback_data="campo-Conteudo"),
                InlineKeyboardButton("Observação", callback_data="campo-Observação")
            ],
            [
                InlineKeyboardButton("Salvar", callback_data="salvar"),
                InlineKeyboardButton("Voltar", callback_data="voltar")
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.bot.edit_message_text(self.create_os_html(os), chat_id=chat_id, message_id=message_id,
                                   reply_markup=reply_markup, parse_mode='HTML')

    def call_novo(self, call_id, chat_id, message_id):
        self.bot.answer_callback_query(call_id)
        lista: list[str] = self.db.get_projetos(chat_id)
        keyboard = []
        for item in lista:
            keyboard.append([InlineKeyboardButton(item[0], callback_data=f"new-projeto??{item[0]}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.bot.edit_message_text("Selecione o projeto:", chat_id=chat_id, message_id=message_id,
                                   parse_mode='HTML', reply_markup=reply_markup)

    def call_consultar(self, call_id, chat_id, message_id):
        self.bot.answer_callback_query(call_id)
        res: list[Os] = self.db.consulta(self.get_user(chat_id))
        lista = []
        for item in res:
            date = item.dia.strftime("%d/%m/%Y")
            lista.append([InlineKeyboardButton(f"{item.codigo} - {date}",
                                               callback_data=f"show-{item.uid}")])
        self.bot.edit_message_text("Escolha uma OS:", chat_id=chat_id, message_id=message_id,
                                   reply_markup=InlineKeyboardMarkup(lista))

    def call_show(self, call, call_id, chat_id, message_id):
        self.bot.answer_callback_query(call_id)
        uid = int(call.data.split('-')[1])
        query = (f"SELECT * "
                 f"FROM public.registros pr "
                 f"INNER JOIN public.projetos pp ON pr.projeto_id = pp.id "
                 f"WHERE pr.id = {uid}")
        os: Os = Os().from_postgres(self.db.get(query))
        keyboard = [
            [InlineKeyboardButton("Voltar", callback_data="voltar")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.bot.delete_message(chat_id=chat_id, message_id=message_id)
        # self.bot.edit_message_text(self.create_os_html(os), chat_id=chat_id, message_id=message_id,
        #                            reply_markup=reply_markup, parse_mode='HTML')
        self.bot.send_message(chat_id, self.create_os_html(os), reply_markup=reply_markup, parse_mode='HTML')

    @staticmethod
    def create_os_html(os: Os):
        tarefas: str = strip_tags(os.tarefas) if os.tarefas is not None else ' '
        obs: str = strip_tags(os.observacao) if os.observacao is not None else ' '
        return f"<b>{os.codigo}</b>\n" \
               f"\n" \
               f"\n" \
               f"<b>Entrada 1:</b> {os.entrada if os.entrada is not None else ' '}\n" \
               f"<b>Saída 1:</b> {os.almoco_inicio if os.almoco_inicio is not None else ' '}\n" \
               f"<b>Entrada 2:</b> {os.almoco_fim if os.almoco_fim is not None else ' '}\n" \
               f"<b>Saída 2:</b> {os.saida if os.saida is not None else ' '}\n" \
               f"<b>Status:</b> {os.status if os.status is not None else ' '}\n" \
               f"<b>RDV:</b> {os.rdv if os.rdv is not None else ' '}\n" \
               f"\n" \
               f"<b>Conteudo</b>{tarefas}\n" \
               f"\n" \
               f"<b>Observação:</b> {obs}\n"

    def get_all_users(self):
        res = self.db.find_known_users()
        if type(res) is not NoneType:
            users = []
            for user in res:
                new = User(uid=user[0], chat_id=user[1])
                users.append(new)
            self.knownUsers = users

    def get_user(self, chat_id):  # type: (int) -> User
        for user in self.knownUsers:
            if user.chat_id == chat_id:
                return user
        return None

    def update_user(self, user: User, chat_id: int):
        for x in range(len(self.knownUsers)):
            if self.knownUsers[x].chat_id == chat_id:
                self.knownUsers[x] = user
                return

    def run(self):
        self.get_all_users()
        self.bot.infinity_polling()

    def end(self):
        self.bot.stop_polling()

import psycopg2 as pg

from classes.user import User
from utils.config_utils import ConfigUtils
from utils.log_utils import LogUtils as lg


class Db:
    def __init__(self):
        self.config = ConfigUtils().load_config()
        self.conn = None

    def start(self):
        try:
            with pg.connect(**self.config) as conn:
                lg().log_info('Conectado no banco de os')
                self.conn = conn
                self.conn.autocommit = True
        except (pg.DatabaseError, Exception) as error:
            lg().log_error(error)

    def exec_query(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()
            return
        except (pg.DatabaseError, Exception) as error:
            lg().log_error(error)

    def get(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchone()
        except (pg.DatabaseError, Exception) as error:
            lg().log_error(error)

    def get_all(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except (pg.DatabaseError, Exception) as error:
            lg().log_error(error)

    def find_user(self, email):
        query = f"SELECT * FROM public.users WHERE email = '{email}'"
        return self.get(query)

    def find_known_users(self):
        query = f"SELECT id, chat_id FROM public.users WHERE chat_id IS NOT NULL"
        return self.get_all(query)

    def insert_chat_id(self, chat_id, email):
        query = f"UPDATE public.users SET chat_id = {chat_id} WHERE email = '{email}'"
        self.exec_query(query)

    def consulta(self, user: User):
        query = (f"SELECT * FROM public.registros pr INNER JOIN public.projetos pp ON pr.projeto_id = pp.id "
                 f"WHERE pr.user_id = {user.uid} AND pr.dia BETWEEN CURRENT_DATE - INTERVAL '7 days' AND CURRENT_DATE "
                 f"ORDER BY pr.dia DESC")
        return self.get_all(query)



import psycopg2 as pg

from classes.os import Os
from classes.user import User
from utils.config_utils import ConfigUtils
from utils.log_utils import LogUtils as lG


class Db:
    def __init__(self):
        self.config = ConfigUtils().load_config()
        self.conn = None

    def start(self):
        try:
            with pg.connect(**self.config) as conn:
                lG().log_info('Conectado no banco de os')
                self.conn = conn
                self.conn.autocommit = True
        except (pg.DatabaseError, Exception) as error:
            lG().log_error(error)

    def exec_query(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            self.conn.commit()
            return
        except (pg.DatabaseError, Exception) as error:
            lG().log_error(error)

    def get(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchone()
        except (pg.DatabaseError, Exception) as error:
            lG().log_error(error)

    def get_all(self, query):
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except (pg.DatabaseError, Exception) as error:
            lG().log_error(error)

    def find_user(self, email):
        query = f"SELECT * FROM public.users WHERE email = '{email}'"
        return self.get(query)

    def find_known_users(self):
        query = f"SELECT id, chat_id FROM public.users WHERE chat_id IS NOT NULL"
        return self.get_all(query)

    def insert_chat_id(self, chat_id, email):
        query = f"UPDATE public.users SET chat_id = {chat_id} WHERE email = '{email}'"
        self.exec_query(query)

    def consulta(self, user):  # type: (User) -> list[Os]
        query = (f"SELECT * FROM public.registros pr INNER JOIN public.projetos pp ON pr.projeto_id = pp.id "
                 f"WHERE pr.user_id = {user.uid} AND pr.dia BETWEEN CURRENT_DATE - INTERVAL '7 days' AND CURRENT_DATE "
                 f"ORDER BY pr.dia DESC")
        res = self.get_all(query)
        dados: list[Os] = []
        for i in res:
            os = Os().from_postgres(i)
            dados.append(os)
        return dados

    def get_projetos(self, chat_id):
        query = (f"select pp.codigo "
                 f"from public.projetos_users pu "
                 f"inner join public.projetos pp on pp.id = pu.projeto_id "
                 f"inner join public.users u on pu.user_id = u.id "
                 f"where u.chat_id = {chat_id}")
        res = self.get_all(query)
        return res




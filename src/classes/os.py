from datetime import datetime


class Os:
    def __init__(self):
        self.uid: int = None
        self.entrada: datetime.time = None
        self.almoco_inicio: datetime.time = None
        self.almoco_fim: datetime.time = None
        self.saida: datetime.time = None
        self.tempo_almoco: datetime.time = None
        self.tempo_trabalhado: datetime.time = None
        self.projeto_id: int = None
        self.user_id: int = None
        self.tarefas: str = None
        self.observacao: str = None
        self.created: datetime = None
        self.modified: datetime = None
        self.dia: datetime.date = None
        self.rdv: str = None
        self.status: str = None
        self.codigo: str = None

    def from_postgres(self, item):
        self.uid = item[0]
        self.entrada = item[1]
        self.almoco_inicio = item[2]
        self.almoco_fim = item[3]
        self.saida = item[4]
        self.tempo_almoco = item[5]
        self.tempo_trabalhado = item[6]
        self.projeto_id = item[7]
        self.user_id = item[8]
        self.tarefas = item[9]
        self.observacao = item[10]
        self.created = item[11]
        self.modified = item[12]
        self.dia = item[13]
        self.rdv = item[14]
        self.status = item[15]
        self.codigo = item[17]
        return self

    def to_json(self):
        return {
            "uid": str(self.uid),
            "entrada": self.entrada.strftime("%H:%M:%S"),
            "almoco_inicio": self.almoco_inicio.strftime("%H:%M:%S"),
            "almoco_fim": self.almoco_fim.strftime("%H:%M:%S"),
            "saida": self.saida.strftime("%H:%M:%S"),
            "tempo_almoco": self.tempo_almoco.strftime("%H:%M:%S"),
            "tempo_trabalhado": self.tempo_trabalhado.strftime("%H:%M:%S"),
            "projeto_id": str(self.projeto_id),
            "user_id": str(self.user_id),
            "tarefas": self.tarefas,
            "observacao": self.observacao,
            "created": self.created.strftime("%d/%m/%Y"),
            "modified": self.modified.strftime("%d/%m/%Y"),
            "dia": self.dia.strftime("%d/%m/%Y"),
            "rdv": self.rdv,
            "status": self.status,
            "codigo": self.codigo
        }

    def from_json(self, item):
        self.uid = int(item['uid'])
        self.entrada = datetime.strptime(item['entrada'], "%H:%M:%S")
        self.almoco_inicio = datetime.strptime(item['almoco_inicio'], "%H:%M:%S")
        self.almoco_fim = datetime.strptime(item['almoco_fim'], "%H:%M:%S")
        self.saida = datetime.strptime(item['saida'], "%H:%M:%S")
        self.tempo_almoco = datetime.strptime(item['tempo_almoco'], "%H:%M:%S")
        self.tempo_trabalhado = datetime.strptime(item['tempo_trabalhado'], "%H:%M:%S")
        self.projeto_id = int(item['projeto_id'])
        self.user_id = int(item['user_id'])
        self.tarefas = item['tarefas']
        self.observacao = item['observacao']
        self.created = datetime.strptime(item['created'], "%d/%m/%Y")
        self.modified = datetime.strptime(item['modified'], "%d/%m/%Y")
        self.dia = datetime.strptime(item['dia'], "%d/%m/%Y")
        self.rdv = item['rdv']
        self.status = item['status']
        self.codigo = item['codigo']
        return self

from sqlalchemy import Enum
import enum
from db import db


class StatusEnum(enum.Enum):
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em andamento"
    CONCLUIDA = "concluida"


class NewTask(db.Model):
    __tablename__ = 'newtask'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    status = db.Column(Enum(StatusEnum), nullable=False)

    def __repr__(self):
        return f"<NewTask id={self.id} titulo='{self.titulo}' status='{self.status}'>"

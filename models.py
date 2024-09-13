from flask_login import UserMixin
from sqlalchemy import Enum
import enum
from db import db
from werkzeug.security import generate_password_hash, check_password_hash


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
    user_id = db.Column(db.Integer, db.ForeignKey(
        'newuser.id'), nullable=False)
    responsavel = db.relationship(
        'User', backref=db.backref('tasks', lazy=True))

    def __repr__(self):
        return f"<NewTask id={self.id} titulo='{self.titulo}' status='{self.status}'>"


class User(db.Model, UserMixin):
    __tablename__ = 'newuser'
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha_usuario = db.Column(db.String(60), nullable=False)

    def definir_senha(self, senha_usuario):
        self.senha_usuario = generate_password_hash(senha_usuario)

    def checar_senha(self, senha_usuario):
        return check_password_hash(self.senha_usuario, senha_usuario)

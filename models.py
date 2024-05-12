from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'efectivo' o 'bancario'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('registros', lazy=True))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    tipo_documento = db.Column(db.String(3), nullable=False)  # CC, NIT, TI
    numero_documento = db.Column(db.String(20), unique=True, nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    divisa = db.Column(db.String(3), nullable=False)  # COP, MXN, ARG, USD, EUR
    nombre_usuario = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.nombre_usuario}>"

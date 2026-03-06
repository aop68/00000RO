"""
Modelos de la aplicación.
- User: modelo local (SQLite) para gestión de usuarios y autenticación.
- Las tablas de Fabric (eventos, planes, riesgos) se acceden via pyodbc directo.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    """Usuario del sistema."""
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='viewer')  # admin, editor, viewer
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def es_admin(self):
        return self.rol == 'admin'

    @property
    def puede_editar(self):
        return self.rol in ('admin', 'editor')

    def __repr__(self):
        return f'<User {self.username}>'

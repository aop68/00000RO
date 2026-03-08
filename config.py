"""
Configuración de la aplicación de Gestión de Riesgo Operacional.
Soporta SQLite (desarrollo local) y PostgreSQL (Railway/producción).
"""
import os


class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-cambiar-en-produccion-2024')

    # --- Base de datos ---
    # Si DATABASE_URL existe (Railway), usa PostgreSQL.
    # Si no, usa SQLite local para desarrollo.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///usuarios.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Power BI Embed URLs ---
    POWERBI_EVENTOS_URL = os.environ.get('POWERBI_EVENTOS_URL', '')
    POWERBI_PLANES_URL = os.environ.get(
        'POWERBI_PLANES_URL',
        'https://app.powerbi.com/reportEmbed?reportId=126f3a9b-ba6d-4a36-bb4f-bcf5ad258468&autoAuth=true&ctid=bf108158-06e6-48aa-9486-6b14f3258d7c'
    )
    POWERBI_RIESGOS_URL = os.environ.get('POWERBI_RIESGOS_URL', '')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

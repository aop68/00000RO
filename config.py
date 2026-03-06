"""
Configuración de la aplicación de Gestión de Riesgo Operacional.
"""
import os
from urllib.parse import quote_plus


class Config:
    """Configuración base."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-cambiar-en-produccion-2024')

    # --- Base de datos local (usuarios y sesiones) ---
    SQLALCHEMY_DATABASE_URI = 'sqlite:///usuarios.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Conexión a Microsoft Fabric SQL ---
    FABRIC_SERVER = os.environ.get(
        'FABRIC_SERVER',
        'lacarbp7ga2verfegnmkpgjmnpq-kkjie75ctc5u5ct5qutmpwmuzi.database.fabric.microsoft.com,1433'
    )
    FABRIC_DATABASE = os.environ.get(
        'FABRIC_DATABASE',
        'RODB-f2a9be1-7921-48ee-828d-476972b8d27e'
    )
    FABRIC_USERNAME = os.environ.get('FABRIC_USERNAME', '')
    FABRIC_PASSWORD = os.environ.get('FABRIC_PASSWORD', '')

    # Método de autenticación: 'sql' o 'azure_ad'
    FABRIC_AUTH_METHOD = os.environ.get('FABRIC_AUTH_METHOD', 'azure_ad')

    # --- Power BI Embed URLs (configurar con tus URLs reales) ---
    POWERBI_EVENTOS_URL = os.environ.get('POWERBI_EVENTOS_URL', '')
    POWERBI_PLANES_URL = os.environ.get('POWERBI_PLANES_URL', 'https://app.powerbi.com/reportEmbed?reportId=126f3a9b-ba6d-4a36-bb4f-bcf5ad258468&autoAuth=true&ctid=bf108158-06e6-48aa-9486-6b14f3258d7c')
    POWERBI_RIESGOS_URL = os.environ.get('POWERBI_RIESGOS_URL', '')

    @staticmethod
    def get_fabric_connection_string():
        """Genera el connection string para Microsoft Fabric SQL."""
        server = Config.FABRIC_SERVER
        database = Config.FABRIC_DATABASE

        if Config.FABRIC_AUTH_METHOD == 'azure_ad':
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Authentication=ActiveDirectoryInteractive;"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
        else:
            username = Config.FABRIC_USERNAME
            password = Config.FABRIC_PASSWORD
            conn_str = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
        return conn_str

    @staticmethod
    def get_fabric_sqlalchemy_uri():
        """Genera la URI de SQLAlchemy para Microsoft Fabric."""
        conn_str = Config.get_fabric_connection_string()
        params = quote_plus(conn_str)
        return f"mssql+pyodbc:///?odbc_connect={params}"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

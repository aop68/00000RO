"""
Aplicación principal - Gestión de Riesgo Operacional.
"""
import os
from flask import Flask
from config import config
from extensions import db, login_manager
from models import User
from sqlalchemy import text


def create_app(config_name=None):
    """Factory de la aplicación Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.eventos import eventos_bp
    from routes.planes import planes_bp
    from routes.riesgos import riesgos_bp
    from routes.powerbi import powerbi_bp
    from routes.admin import admin_bp
    from routes.reportes import reportes_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(eventos_bp, url_prefix='/eventos')
    app.register_blueprint(planes_bp, url_prefix='/planes')
    app.register_blueprint(riesgos_bp, url_prefix='/riesgos')
    app.register_blueprint(powerbi_bp, url_prefix='/powerbi')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')

    # Liberar sesión de SQLAlchemy después de cada request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Crear tablas y datos iniciales
    with app.app_context():
        db.create_all()
        _init_fabric_tables(app)
        _crear_admin_default()

    return app


def _init_fabric_tables(app):
    """Crea las tablas de riesgo operacional y carga datos iniciales si no existen."""
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

    def _strip_comments(sql_text):
        """Elimina líneas de comentarios de un bloque SQL."""
        lines = sql_text.split('\n')
        cleaned = [line for line in lines if not line.strip().startswith('--')]
        return '\n'.join(cleaned).strip()

    def _execute_sql_file(filepath, label):
        """Ejecuta un archivo SQL statement por statement."""
        with open(filepath, 'r', encoding='utf-8') as f:
            sql = f.read()
        for raw_statement in sql.split(';'):
            statement = _strip_comments(raw_statement)
            if statement:
                try:
                    db.session.execute(text(statement))
                except Exception as stmt_err:
                    app.logger.warning(f'[{label}] Statement omitido: {stmt_err}')
                    db.session.rollback()
                    continue
        db.session.commit()
        app.logger.info(f'{label} ejecutado correctamente.')

    # Ejecutar schema (CREATE TABLE IF NOT EXISTS — seguro re-ejecutar)
    schema_file = os.path.join(migrations_dir, 'init_schema.sql')
    if os.path.exists(schema_file):
        try:
            _execute_sql_file(schema_file, 'Schema')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error creando schema: {e}')

    # Cargar datos iniciales solo si los catálogos están vacíos
    try:
        result = db.session.execute(text("SELECT COUNT(*) FROM cat_tipo_evento_ro02"))
        count = result.fetchone()[0]
    except Exception:
        db.session.rollback()
        count = 0

    if count == 0:
        seed_file = os.path.join(migrations_dir, 'seed_data.sql')
        if os.path.exists(seed_file):
            try:
                _execute_sql_file(seed_file, 'Seed data')
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Error cargando datos iniciales: {e}')


def _crear_admin_default():
    """Crea el usuario administrador si no existe."""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@banco.com.do',
            nombre='Administrador',
            apellido='Sistema',
            rol='admin',
            activo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

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
    """Crea las tablas de riesgo operacional y carga datos iniciales
    usando psycopg2 directamente para ejecutar scripts SQL completos."""
    import psycopg2

    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'sqlite' in db_url:
        app.logger.info('Base de datos SQLite detectada, omitiendo tablas Fabric.')
        return

    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')

    # Parsear la URL de conexión para psycopg2
    # Formato: postgresql://user:pass@host:port/dbname
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        app.logger.error(f'No se pudo conectar con psycopg2: {e}')
        return

    try:
        # 1. Ejecutar schema completo
        schema_file = os.path.join(migrations_dir, 'init_schema.sql')
        if os.path.exists(schema_file):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                cur.execute(schema_sql)
                app.logger.info('Schema de tablas Fabric creado correctamente.')
            except Exception as e:
                app.logger.error(f'Error creando schema Fabric: {e}')
                # Intentar cerrar y reconectar
                try:
                    conn.close()
                except Exception:
                    pass
                return

        # 2. Verificar si ya hay datos en los catálogos
        try:
            cur.execute("SELECT COUNT(*) FROM cat_tipo_evento_ro02")
            count = cur.fetchone()[0]
        except Exception:
            count = 0

        # 3. Cargar seed data si los catálogos están vacíos
        if count == 0:
            seed_file = os.path.join(migrations_dir, 'seed_data.sql')
            if os.path.exists(seed_file):
                with open(seed_file, 'r', encoding='utf-8') as f:
                    seed_sql = f.read()
                # Ejecutar statement por statement para mayor robustez
                ok_count = 0
                err_count = 0
                for raw_stmt in seed_sql.split(';'):
                    # Limpiar comentarios
                    lines = [l for l in raw_stmt.split('\n')
                             if not l.strip().startswith('--')]
                    stmt = '\n'.join(lines).strip()
                    if stmt:
                        try:
                            cur.execute(stmt)
                            ok_count += 1
                        except Exception as e:
                            app.logger.warning(f'Seed stmt omitido: {e}')
                            err_count += 1
                app.logger.info(
                    f'Seed data: {ok_count} OK, {err_count} errores.')
        else:
            app.logger.info(f'Catálogos ya contienen {count} registros, omitiendo seed.')

    finally:
        cur.close()
        conn.close()


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

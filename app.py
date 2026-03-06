"""
Aplicación principal - Gestión de Riesgo Operacional.
"""
import os
from flask import Flask
from config import config, Config
from extensions import db, login_manager
from models import User


def create_app(config_name=None):
    """Factory de la aplicación Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['FABRIC_CONN_STRING'] = Config.get_fabric_connection_string()

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

    # Crear tablas locales y usuario admin por defecto
    with app.app_context():
        db.create_all()
        _crear_admin_default()

    return app


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
    app.run(debug=True, host='0.0.0.0', port=5000)

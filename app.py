"""
Aplicacion principal - Gestion de Riesgo Operacional.
"""
import os
from flask import Flask
from config import config
from extensions import db, login_manager, csrf
from models import User


def create_app(config_name=None):
    """Factory de la aplicacion Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

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

    # Headers de seguridad HTTP
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net code.jquery.com cdn.datatables.net; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdn.datatables.net; "
            "font-src 'self' cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "frame-src app.powerbi.com; "
            "connect-src 'self'"
        )
        return response

    # Liberar sesion de SQLAlchemy despues de cada request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # Crear tabla de usuarios local y admin por defecto
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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

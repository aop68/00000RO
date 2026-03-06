"""
Rutas de administración: gestión de usuarios y permisos.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User
from extensions import db
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorador que requiere rol de administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.es_admin:
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    users = User.query.order_by(User.fecha_creacion.desc()).all()
    return render_template('admin/usuarios.html', usuarios=users)


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_usuario():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        password = request.form.get('password', '')
        rol = request.form.get('rol', 'viewer')

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado.', 'danger')
        elif not all([username, email, nombre, apellido, password]):
            flash('Todos los campos son obligatorios.', 'danger')
        else:
            user = User(
                username=username,
                email=email,
                nombre=nombre,
                apellido=apellido,
                rol=rol,
                activo=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'Usuario "{username}" creado exitosamente.', 'success')
            return redirect(url_for('admin.usuarios'))

    return render_template('admin/usuario_form.html', usuario=None)


@admin_bp.route('/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.nombre = request.form.get('nombre', '').strip()
        user.apellido = request.form.get('apellido', '').strip()
        user.email = request.form.get('email', '').strip()
        user.rol = request.form.get('rol', 'viewer')
        user.activo = request.form.get('activo') == 'on'

        new_password = request.form.get('password', '').strip()
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        flash(f'Usuario "{user.username}" actualizado.', 'success')
        return redirect(url_for('admin.usuarios'))

    return render_template('admin/usuario_form.html', usuario=user)


@admin_bp.route('/usuarios/toggle/<int:user_id>')
@login_required
@admin_required
def toggle_usuario(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('No puede desactivar su propia cuenta.', 'warning')
    else:
        user.activo = not user.activo
        db.session.commit()
        estado = 'activado' if user.activo else 'desactivado'
        flash(f'Usuario "{user.username}" {estado}.', 'success')
    return redirect(url_for('admin.usuarios'))

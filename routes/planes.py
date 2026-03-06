"""
Rutas CRUD para Planes de Acción.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

planes_bp = Blueprint('planes', __name__)


@planes_bp.route('/')
@login_required
def lista():
    planes = []
    error = None
    try:
        from fabric_db import get_planes
        planes = get_planes()
    except Exception as e:
        error = f"Error al conectar con la base de datos: {str(e)}"
    return render_template('planes/lista.html', planes=planes, error=error)


@planes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if not current_user.puede_editar:
        flash('No tiene permisos para crear planes de acción.', 'danger')
        return redirect(url_for('planes.lista'))

    if request.method == 'POST':
        try:
            from fabric_db import crear_plan
            datos = {
                'codigo_plan': request.form.get('codigo_plan'),
                'estatus': request.form.get('estatus'),
                'plan_accion': request.form.get('plan_accion'),
                'prioridad': request.form.get('prioridad'),
                'tipo_plan_accion': request.form.get('tipo_plan_accion'),
                'origen_plan_accion': request.form.get('origen_plan_accion'),
                'codigo_riesgo': request.form.get('codigo_riesgo'),
                'vp_responsable': request.form.get('vp_responsable'),
                'direccion_responsable': request.form.get('direccion_responsable'),
                'responsable': request.form.get('responsable'),
                'fecha_creacion_plan': request.form.get('fecha_creacion_plan') or None,
                'fecha_compromiso_inicial': request.form.get('fecha_compromiso_inicial') or None,
                'fecha_compromiso_actual': request.form.get('fecha_compromiso_actual') or None,
                'fecha_cierre': request.form.get('fecha_cierre') or None,
                'usuario_carga': current_user.username
            }
            crear_plan(datos)
            flash('Plan de acción creado exitosamente.', 'success')
            return redirect(url_for('planes.lista'))
        except Exception as e:
            flash(f'Error al crear plan: {str(e)}', 'danger')

    catalogos = _cargar_catalogos_planes()
    return render_template('planes/formulario.html', plan=None, catalogos=catalogos)


@planes_bp.route('/editar/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def editar(plan_id):
    if not current_user.puede_editar:
        flash('No tiene permisos para editar planes.', 'danger')
        return redirect(url_for('planes.lista'))

    try:
        from fabric_db import get_plan, actualizar_plan
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'danger')
        return redirect(url_for('planes.lista'))

    if request.method == 'POST':
        try:
            datos = {
                'codigo_plan': request.form.get('codigo_plan'),
                'estatus': request.form.get('estatus'),
                'plan_accion': request.form.get('plan_accion'),
                'prioridad': request.form.get('prioridad'),
                'tipo_plan_accion': request.form.get('tipo_plan_accion'),
                'origen_plan_accion': request.form.get('origen_plan_accion'),
                'codigo_riesgo': request.form.get('codigo_riesgo'),
                'vp_responsable': request.form.get('vp_responsable'),
                'direccion_responsable': request.form.get('direccion_responsable'),
                'responsable': request.form.get('responsable'),
                'fecha_creacion_plan': request.form.get('fecha_creacion_plan') or None,
                'fecha_compromiso_inicial': request.form.get('fecha_compromiso_inicial') or None,
                'fecha_compromiso_actual': request.form.get('fecha_compromiso_actual') or None,
                'fecha_cierre': request.form.get('fecha_cierre') or None,
                'usuario_modificacion': current_user.username
            }
            actualizar_plan(plan_id, datos)
            flash('Plan actualizado exitosamente.', 'success')
            return redirect(url_for('planes.lista'))
        except Exception as e:
            flash(f'Error al actualizar: {str(e)}', 'danger')

    plan = get_plan(plan_id)
    if not plan:
        flash('Plan no encontrado.', 'warning')
        return redirect(url_for('planes.lista'))

    catalogos = _cargar_catalogos_planes()
    return render_template('planes/formulario.html', plan=plan, catalogos=catalogos)


def _cargar_catalogos_planes():
    """Carga catálogos para formulario de planes."""
    catalogos = {}
    try:
        from fabric_db import get_catalogo
        catalogos['estados'] = get_catalogo('cat_estado_plan_accion')
    except Exception:
        pass
    return catalogos

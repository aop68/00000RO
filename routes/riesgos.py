"""
Rutas CRUD para Riesgos y Controles.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

riesgos_bp = Blueprint('riesgos', __name__)


@riesgos_bp.route('/')
@login_required
def lista():
    riesgos = []
    error = None
    try:
        from fabric_db import get_riesgos
        riesgos = get_riesgos()
    except Exception as e:
        error = f"Error al conectar con la base de datos: {str(e)}"
    return render_template('riesgos/lista.html', riesgos=riesgos, error=error)


@riesgos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if not current_user.puede_editar:
        flash('No tiene permisos para crear riesgos.', 'danger')
        return redirect(url_for('riesgos.lista'))

    if request.method == 'POST':
        try:
            from fabric_db import crear_riesgo
            datos = {
                'codigo_riesgo': request.form.get('codigo_riesgo'),
                'descripcion_riesgo': request.form.get('descripcion_riesgo'),
                'categoria_riesgo': request.form.get('categoria_riesgo'),
                'riesgo_nivel_1': request.form.get('riesgo_nivel_1'),
                'riesgo_nivel_2': request.form.get('riesgo_nivel_2'),
                'riesgo_nivel_3': request.form.get('riesgo_nivel_3'),
                'macroproceso': request.form.get('macroproceso'),
                'proceso': request.form.get('proceso'),
                'factor_riesgo': request.form.get('factor_riesgo'),
                'causa_raiz': request.form.get('causa_raiz'),
                'impacto_financiero_dop': request.form.get('impacto_financiero_dop') or None,
                'frecuencia_inherente': request.form.get('frecuencia_inherente'),
                'descripcion_control': request.form.get('descripcion_control'),
                'tipo_control': request.form.get('tipo_control'),
                'frecuencia_ejecucion': request.form.get('frecuencia_ejecucion'),
                'grado_manualidad': request.form.get('grado_manualidad'),
                'vp_responsable_procedimiento': request.form.get('vp_responsable_procedimiento'),
                'direccion_responsable_control': request.form.get('direccion_responsable_control'),
                'control_documentado': 1 if request.form.get('control_documentado') else 0,
                'control_en_remediacion': 1 if request.form.get('control_en_remediacion') else 0,
                'usuario_carga': current_user.username
            }
            crear_riesgo(datos)
            flash('Riesgo/Control creado exitosamente.', 'success')
            return redirect(url_for('riesgos.lista'))
        except Exception as e:
            flash(f'Error al crear: {str(e)}', 'danger')

    catalogos = _cargar_catalogos_riesgos()
    return render_template('riesgos/formulario.html', riesgo=None, catalogos=catalogos)


@riesgos_bp.route('/editar/<int:riesgo_id>', methods=['GET', 'POST'])
@login_required
def editar(riesgo_id):
    if not current_user.puede_editar:
        flash('No tiene permisos para editar riesgos.', 'danger')
        return redirect(url_for('riesgos.lista'))

    try:
        from fabric_db import get_riesgo, actualizar_riesgo
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'danger')
        return redirect(url_for('riesgos.lista'))

    if request.method == 'POST':
        try:
            datos = {
                'codigo_riesgo': request.form.get('codigo_riesgo'),
                'descripcion_riesgo': request.form.get('descripcion_riesgo'),
                'categoria_riesgo': request.form.get('categoria_riesgo'),
                'riesgo_nivel_1': request.form.get('riesgo_nivel_1'),
                'riesgo_nivel_2': request.form.get('riesgo_nivel_2'),
                'riesgo_nivel_3': request.form.get('riesgo_nivel_3'),
                'macroproceso': request.form.get('macroproceso'),
                'proceso': request.form.get('proceso'),
                'factor_riesgo': request.form.get('factor_riesgo'),
                'causa_raiz': request.form.get('causa_raiz'),
                'impacto_financiero_dop': request.form.get('impacto_financiero_dop') or None,
                'frecuencia_inherente': request.form.get('frecuencia_inherente'),
                'descripcion_control': request.form.get('descripcion_control'),
                'tipo_control': request.form.get('tipo_control'),
                'frecuencia_ejecucion': request.form.get('frecuencia_ejecucion'),
                'grado_manualidad': request.form.get('grado_manualidad'),
                'vp_responsable_procedimiento': request.form.get('vp_responsable_procedimiento'),
                'direccion_responsable_control': request.form.get('direccion_responsable_control'),
                'control_documentado': 1 if request.form.get('control_documentado') else 0,
                'control_en_remediacion': 1 if request.form.get('control_en_remediacion') else 0,
                'usuario_modificacion': current_user.username
            }
            actualizar_riesgo(riesgo_id, datos)
            flash('Riesgo/Control actualizado exitosamente.', 'success')
            return redirect(url_for('riesgos.lista'))
        except Exception as e:
            flash(f'Error al actualizar: {str(e)}', 'danger')

    riesgo = get_riesgo(riesgo_id)
    if not riesgo:
        flash('Riesgo no encontrado.', 'warning')
        return redirect(url_for('riesgos.lista'))

    catalogos = _cargar_catalogos_riesgos()
    return render_template('riesgos/formulario.html', riesgo=riesgo, catalogos=catalogos)


def _cargar_catalogos_riesgos():
    """Carga catálogos para formulario de riesgos."""
    catalogos = {}
    try:
        from fabric_db import get_catalogo
        catalogos['tipos_control'] = get_catalogo('cat_tipo_control')
        catalogos['frecuencias'] = get_catalogo('cat_frecuencia_control')
        catalogos['factores'] = get_catalogo('cat_factor_causa')
        catalogos['probabilidades'] = get_catalogo('cat_probabilidad')
        catalogos['severidades'] = get_catalogo('cat_severidad')
        catalogos['procesos'] = get_catalogo('cat_procesos')
    except Exception:
        pass
    return catalogos

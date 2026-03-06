"""
Rutas CRUD para Eventos de Riesgo Operacional.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

eventos_bp = Blueprint('eventos', __name__)


@eventos_bp.route('/')
@login_required
def lista():
    eventos = []
    error = None
    try:
        from fabric_db import get_eventos
        eventos = get_eventos()
    except Exception as e:
        error = f"Error al conectar con la base de datos: {str(e)}"
    return render_template('eventos/lista.html', eventos=eventos, error=error)


@eventos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if not current_user.puede_editar:
        flash('No tiene permisos para crear eventos.', 'danger')
        return redirect(url_for('eventos.lista'))

    if request.method == 'POST':
        try:
            from fabric_db import crear_evento
            datos = {
                'codigo_evento': request.form.get('codigo_evento'),
                'descripcion_evento': request.form.get('descripcion_evento'),
                'tipo_evento': request.form.get('tipo_evento'),
                'categoria_evento': request.form.get('categoria_evento'),
                'subcategoria_evento': request.form.get('subcategoria_evento'),
                'fecha_descubrimiento': request.form.get('fecha_descubrimiento') or None,
                'fecha_inicio_evento': request.form.get('fecha_inicio_evento') or None,
                'fecha_finalizacion_evento': request.form.get('fecha_finalizacion_evento') or None,
                'monto_perdida_bruta_dop': request.form.get('monto_perdida_bruta_dop') or None,
                'monto_recuperado_dop': request.form.get('monto_recuperado_dop') or None,
                'monto_perdida_neta_dop': request.form.get('monto_perdida_neta_dop') or None,
                'monto_usd': request.form.get('monto_usd') or None,
                'area_origen': request.form.get('area_origen'),
                'linea_negocios': request.form.get('linea_negocios'),
                'proceso_afectado': request.form.get('proceso_afectado'),
                'codigo_riesgo_asociado': request.form.get('codigo_riesgo_asociado'),
                'estado_investigacion': request.form.get('estado_investigacion'),
                'aplica_plan_accion': 1 if request.form.get('aplica_plan_accion') else 0,
                'canal_distribucion_afectado': request.form.get('canal_distribucion_afectado'),
                'medio_pago': request.form.get('medio_pago'),
                'marca_tarjeta': request.form.get('marca_tarjeta'),
                'usuario_carga': current_user.username
            }
            crear_evento(datos)
            flash('Evento creado exitosamente.', 'success')
            return redirect(url_for('eventos.lista'))
        except Exception as e:
            flash(f'Error al crear evento: {str(e)}', 'danger')

    catalogos = _cargar_catalogos_eventos()
    return render_template('eventos/formulario.html', evento=None, catalogos=catalogos)


@eventos_bp.route('/editar/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def editar(evento_id):
    if not current_user.puede_editar:
        flash('No tiene permisos para editar eventos.', 'danger')
        return redirect(url_for('eventos.lista'))

    try:
        from fabric_db import get_evento, actualizar_evento
    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'danger')
        return redirect(url_for('eventos.lista'))

    if request.method == 'POST':
        try:
            datos = {
                'codigo_evento': request.form.get('codigo_evento'),
                'descripcion_evento': request.form.get('descripcion_evento'),
                'tipo_evento': request.form.get('tipo_evento'),
                'categoria_evento': request.form.get('categoria_evento'),
                'subcategoria_evento': request.form.get('subcategoria_evento'),
                'fecha_descubrimiento': request.form.get('fecha_descubrimiento') or None,
                'fecha_inicio_evento': request.form.get('fecha_inicio_evento') or None,
                'fecha_finalizacion_evento': request.form.get('fecha_finalizacion_evento') or None,
                'monto_perdida_bruta_dop': request.form.get('monto_perdida_bruta_dop') or None,
                'monto_recuperado_dop': request.form.get('monto_recuperado_dop') or None,
                'monto_perdida_neta_dop': request.form.get('monto_perdida_neta_dop') or None,
                'monto_usd': request.form.get('monto_usd') or None,
                'area_origen': request.form.get('area_origen'),
                'linea_negocios': request.form.get('linea_negocios'),
                'proceso_afectado': request.form.get('proceso_afectado'),
                'codigo_riesgo_asociado': request.form.get('codigo_riesgo_asociado'),
                'estado_investigacion': request.form.get('estado_investigacion'),
                'aplica_plan_accion': 1 if request.form.get('aplica_plan_accion') else 0,
                'canal_distribucion_afectado': request.form.get('canal_distribucion_afectado'),
                'medio_pago': request.form.get('medio_pago'),
                'marca_tarjeta': request.form.get('marca_tarjeta'),
                'usuario_modificacion': current_user.username
            }
            actualizar_evento(evento_id, datos)
            flash('Evento actualizado exitosamente.', 'success')
            return redirect(url_for('eventos.lista'))
        except Exception as e:
            flash(f'Error al actualizar: {str(e)}', 'danger')

    evento = get_evento(evento_id)
    if not evento:
        flash('Evento no encontrado.', 'warning')
        return redirect(url_for('eventos.lista'))

    catalogos = _cargar_catalogos_eventos()
    return render_template('eventos/formulario.html', evento=evento, catalogos=catalogos)


def _cargar_catalogos_eventos():
    """Carga los catálogos necesarios para el formulario de eventos."""
    catalogos = {}
    try:
        from fabric_db import get_catalogo
        catalogos['tipos_evento'] = get_catalogo('cat_tipo_evento')
        catalogos['estados'] = get_catalogo('cat_estado_evento')
        catalogos['lineas_negocio'] = get_catalogo('cat_linea_negocio')
        catalogos['canales'] = get_catalogo('cat_canales')
        catalogos['medios_pago'] = get_catalogo('cat_medio_pago')
        catalogos['areas'] = get_catalogo('cat_areas_organizacion')
    except Exception:
        pass
    return catalogos

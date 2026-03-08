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
            datos = _extraer_datos_formulario(request.form)
            datos['usuario_carga'] = current_user.username
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
            datos = _extraer_datos_formulario(request.form)
            datos['usuario_modificacion'] = current_user.username
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


def _extraer_datos_formulario(form):
    """Extrae y normaliza los datos del formulario de eventos."""
    return {
        'codigo_evento': form.get('codigo_evento'),
        'descripcion_evento': form.get('descripcion_evento'),
        'tipo_evento': form.get('tipo_evento'),
        'categoria_evento': form.get('categoria_evento'),
        'subcategoria_evento': form.get('subcategoria_evento'),
        'estado_investigacion': form.get('estado_investigacion'),
        'nivel_riesgo_inherente': form.get('nivel_riesgo_inherente'),
        'factor_determinante': form.get('factor_determinante'),
        'causa_evento': form.get('causa_evento'),
        'consecuencia': form.get('consecuencia'),
        'tipo_perdida': form.get('tipo_perdida'),
        'tipo_registro': form.get('tipo_registro'),
        'fecha_descubrimiento': form.get('fecha_descubrimiento') or None,
        'fecha_inicio_evento': form.get('fecha_inicio_evento') or None,
        'fecha_finalizacion_evento': form.get('fecha_finalizacion_evento') or None,
        'monto_dop': form.get('monto_perdida_bruta_dop') or 0,
        'monto_recuperado_seguros': form.get('monto_recuperado_seguros') or 0,
        'monto_recuperado_otros': form.get('monto_recuperado_otros') or 0,
        'monto_moneda_origen': form.get('monto_moneda_origen') or None,
        'area_origen': form.get('area_origen'),
        'linea_negocios': form.get('linea_negocios'),
        'proceso_afectado': form.get('proceso_afectado'),
        'codigo_riesgo_asociado': form.get('codigo_riesgo_asociado'),
        'aplica_plan_accion': 1 if form.get('aplica_plan_accion') else 0,
        'canal_distribucion_afectado': form.get('canal_distribucion_afectado'),
        'medio_pago': form.get('medio_pago'),
        'marca_tarjeta': form.get('marca_tarjeta'),
        'detalle_causa_raiz': form.get('detalle_causa_raiz'),
        'descripcion_extendida': form.get('descripcion_extendida'),
    }


def _cargar_catalogos_eventos():
    """Carga los catálogos necesarios para el formulario de eventos."""
    catalogos = {}
    try:
        from fabric_db import get_catalogo
        # Catálogos jerárquicos (se pasan completos para cascada en JS)
        catalogos['tipos_evento'] = get_catalogo('cat_tipo_evento_ro02')
        catalogos['factores_causa'] = get_catalogo('cat_factor_causa')
        # Catálogos simples
        catalogos['estados'] = get_catalogo('cat_estado_evento')
        catalogos['lineas_negocio'] = get_catalogo('cat_linea_negocio')
        catalogos['areas'] = get_catalogo('cat_areas_organizacion')
        catalogos['procesos'] = get_catalogo('cat_procesos')
        catalogos['canales'] = get_catalogo('cat_canales')
        catalogos['medios_pago'] = get_catalogo('cat_medio_pago')
        catalogos['marcas_tarjetas'] = get_catalogo('cat_marcas_tarjetas')
        catalogos['naturalezas_perdida'] = get_catalogo('cat_naturaleza_perdida')
        catalogos['consecuencias'] = get_catalogo('cat_consecuencias')
        catalogos['severidades'] = get_catalogo('cat_severidad')
        catalogos['probabilidades'] = get_catalogo('cat_probabilidad')
        catalogos['incidentes_fraude'] = get_catalogo('cat_incidentes_fraude')
    except Exception:
        pass
    return catalogos

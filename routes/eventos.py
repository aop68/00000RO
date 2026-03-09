"""
Rutas CRUD para Eventos de Riesgo Operacional.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user
from sqlalchemy import text
from extensions import db

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


@eventos_bp.route('/siguiente_codigo')
@login_required
def siguiente_codigo():
    """Devuelve el siguiente código de evento para un año/mes dado."""
    anio = request.args.get('anio', '')
    mes = request.args.get('mes', '')
    if not anio or not mes:
        return jsonify({'codigo': ''})
    yy = anio[-2:]
    mm = mes.zfill(2)
    prefijo = f'E-{yy}{mm}-'
    try:
        result = db.session.execute(
            text("SELECT codigo_evento FROM eventos_riesgo_operacional WHERE codigo_evento LIKE :prefijo ORDER BY codigo_evento DESC LIMIT 1"),
            {'prefijo': prefijo + '%'}
        )
        row = result.fetchone()
        if row:
            ultimo = row[0]
            seq = int(ultimo.split('-')[-1]) + 1
        else:
            seq = 1
        codigo = f'{prefijo}{seq:03d}'
    except Exception:
        codigo = f'{prefijo}001'
    return jsonify({'codigo': codigo})


@eventos_bp.route('/reporte_ro02')
@login_required
def reporte_ro02():
    """Genera el reporte RO02 en formato TXT separado por pipes."""
    anio = request.args.get('anio', '')
    mes = request.args.get('mes', '')
    if not anio or not mes:
        flash('Debe seleccionar año y mes para generar el reporte.', 'warning')
        return redirect(url_for('eventos.lista'))

    try:
        # Obtener eventos del periodo
        result = db.session.execute(
            text("""
                SELECT * FROM eventos_riesgo_operacional
                WHERE EXTRACT(YEAR FROM fecha_descubrimiento) = :anio
                  AND EXTRACT(MONTH FROM fecha_descubrimiento) = :mes
                ORDER BY codigo_evento
            """),
            {'anio': int(anio), 'mes': int(mes)}
        )
        columns = result.keys()
        eventos = [dict(zip(columns, row)) for row in result.fetchall()]

        # Cargar catálogos para mapear nombre → código
        catalogos_map = _cargar_mapas_catalogos()

        # Generar líneas del reporte
        lineas = []
        # Encabezado
        encabezado = '|'.join([
            'NUM_SECUENCIAL', 'CODIGO_EVENTO', 'TIPO_EVENTO', 'DESCRIPCION_EVENTO',
            'CANTIDAD_EVENTOS', 'TIPO_PERDIDA', 'CONSECUENCIA', 'LINEA_NEGOCIOS',
            'PROCESO_AFECTADO', 'PRODUCTO_AFECTADO', 'SERVICIO_AFECTADO',
            'AREA_DEPARTAMENTO', 'MARCA_TARJETA', 'CANAL_DISTRIBUCION',
            'FACTOR_CAUSA', 'LOCALIDAD', 'FECHA_DESCUBRIMIENTO',
            'FECHA_INICIO', 'FECHA_FINALIZACION', 'FECHA_CIERRE',
            'TIPO_MONEDA', 'MONTO_PERDIDA_MN', 'MONTO_PERDIDA_MO',
            'CUENTA_CONTABLE', 'FECHA_CONTABILIZACION',
            'MONTO_RECUPERADO_SEGUROS', 'MONTO_RECUPERADO_OTROS',
            'FECHA_CONTAB_RECUPERACION', 'MEDIO_PAGO',
            'DETALLE_INCIDENTE_FRAUDE', 'TIPO_REGISTRO', 'ESTATUS'
        ])
        lineas.append(encabezado)

        for idx, ev in enumerate(eventos, 1):
            # Mapear tipo_perdida a código
            tp = ev.get('tipo_perdida') or ''
            tipo_perdida_cod = _mapear_tipo_perdida(tp)

            # Mapear estatus
            estatus_cod = _mapear_estatus(ev.get('estatus_contabilizacion') or '')

            # Mapear tipo_registro
            tipo_reg = ev.get('tipo_registro') or ''
            tipo_reg_cod = _mapear_tipo_registro(tipo_reg)

            campos = [
                str(idx),
                ev.get('codigo_evento') or '',
                catalogos_map.get('tipo_evento', {}).get(ev.get('tipo_evento'), ''),
                (ev.get('descripcion_evento') or '').replace('|', ' ').replace('\n', ' '),
                str(ev.get('cantidad_eventos') or 1),
                tipo_perdida_cod,
                catalogos_map.get('consecuencia', {}).get(ev.get('consecuencia'), ''),
                catalogos_map.get('linea_negocio', {}).get(ev.get('linea_negocios'), ''),
                catalogos_map.get('proceso', {}).get(ev.get('proceso_afectado'), ''),
                catalogos_map.get('proceso', {}).get(ev.get('producto_afectado'), ''),
                catalogos_map.get('proceso', {}).get(ev.get('servicio_afectado'), ''),
                catalogos_map.get('area', {}).get(ev.get('area_origen'), ''),
                catalogos_map.get('marca_tarjeta', {}).get(ev.get('marca_tarjeta'), ''),
                catalogos_map.get('canal', {}).get(ev.get('canal_distribucion_afectado'), ''),
                catalogos_map.get('factor_causa', {}).get(ev.get('factor_determinante'), ''),
                catalogos_map.get('area', {}).get(ev.get('localidad_origen'), ''),
                _fmt_fecha(ev.get('fecha_descubrimiento')),
                _fmt_fecha(ev.get('fecha_inicio_evento')),
                _fmt_fecha(ev.get('fecha_finalizacion_evento')),
                _fmt_fecha(ev.get('fecha_cierre_evento')),
                ev.get('tipo_moneda_ocurrencia') or 'DOP',
                _fmt_monto(ev.get('monto_dop')),
                _fmt_monto(ev.get('monto_moneda_origen')),
                ev.get('cuenta_contable_monto') or '',
                _fmt_fecha(ev.get('fecha_contabilizacion')),
                _fmt_monto(ev.get('monto_recuperado_seguros')),
                _fmt_monto(ev.get('monto_recuperado_otros')),
                _fmt_fecha(ev.get('fecha_contab_recuperacion')),
                catalogos_map.get('medio_pago', {}).get(ev.get('medio_pago'), ''),
                catalogos_map.get('incidente_fraude', {}).get(ev.get('tipo_registro'), ''),
                tipo_reg_cod,
                estatus_cod,
            ]
            lineas.append('|'.join(campos))

        contenido = '\n'.join(lineas)
        nombre_archivo = f'RO02_{anio}_{mes.zfill(2)}.txt'

        return Response(
            contenido,
            mimetype='text/plain',
            headers={'Content-Disposition': f'attachment; filename={nombre_archivo}'}
        )
    except Exception as e:
        flash(f'Error al generar reporte: {str(e)}', 'danger')
        return redirect(url_for('eventos.lista'))


def _cargar_mapas_catalogos():
    """Carga mapas nombre→código de todos los catálogos para el reporte."""
    mapas = {}
    tablas = {
        'tipo_evento': 'cat_tipo_evento_ro02',
        'consecuencia': 'cat_consecuencias',
        'linea_negocio': 'cat_linea_negocio',
        'proceso': 'cat_procesos',
        'area': 'cat_areas_organizacion',
        'marca_tarjeta': 'cat_marcas_tarjetas',
        'canal': 'cat_canales',
        'factor_causa': 'cat_factor_causa',
        'medio_pago': 'cat_medio_pago',
        'incidente_fraude': 'cat_incidentes_fraude',
    }
    for clave, tabla in tablas.items():
        try:
            result = db.session.execute(text(f"SELECT nombre, codigo FROM {tabla}"))
            mapas[clave] = {row[0]: row[1] for row in result.fetchall()}
        except Exception:
            mapas[clave] = {}
    return mapas


def _mapear_tipo_perdida(nombre):
    """Mapea tipo de pérdida a código RO02."""
    nombre_lower = (nombre or '').lower()
    if 'no econ' in nombre_lower:
        return 'NE'
    elif 'pendiente' in nombre_lower:
        return 'EP'
    elif 'econ' in nombre_lower:
        return 'EC'
    return ''


def _mapear_estatus(estatus):
    """Mapea estatus contabilización a código RO02 (1-5)."""
    estatus_lower = (estatus or '').lower()
    if 'descubiert' in estatus_lower or estatus == '1':
        return '1'
    elif 'contabiliz' in estatus_lower and 'pendiente' in estatus_lower or estatus == '2':
        return '2'
    elif 'completado' in estatus_lower or 'completad' in estatus_lower or estatus == '3':
        return '3'
    elif 'sin perdida' in estatus_lower or 'no genera' in estatus_lower or estatus == '4':
        return '4'
    elif 'desestim' in estatus_lower or estatus == '5':
        return '5'
    return estatus or ''


def _mapear_tipo_registro(nombre):
    """Mapea tipo registro a código RO02."""
    nombre_lower = (nombre or '').lower()
    if 'registro' in nombre_lower or 'nuevo' in nombre_lower:
        return 'N'
    elif 'actualiz' in nombre_lower:
        return 'A'
    elif 'modific' in nombre_lower or 'provisio' in nombre_lower:
        return 'M'
    elif 'reclasific' in nombre_lower:
        return 'R'
    elif 'correc' in nombre_lower:
        return 'C'
    return ''


def _fmt_fecha(valor):
    """Formatea una fecha para el reporte."""
    if valor is None:
        return ''
    return str(valor)


def _fmt_monto(valor):
    """Formatea un monto para el reporte."""
    if valor is None:
        return '0.00'
    return f'{float(valor):.2f}'


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
        'aplica_plan_accion': True if form.get('aplica_plan_accion') else False,
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

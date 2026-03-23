"""
Rutas CRUD para Eventos de Riesgo Operacional.
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user

logger = logging.getLogger(__name__)

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
        logger.error("Error al obtener eventos: %s", e)
        error = "Error al conectar con la base de datos. Intente de nuevo más tarde."
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
            logger.error("Error al crear evento: %s", e)
            flash('Error al crear evento. Verifique los datos e intente de nuevo.', 'danger')

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
        logger.error("Error de conexión al editar evento: %s", e)
        flash('Error de conexión con la base de datos.', 'danger')
        return redirect(url_for('eventos.lista'))

    if request.method == 'POST':
        try:
            datos = _extraer_datos_formulario(request.form)
            datos['usuario_modificacion'] = current_user.username
            actualizar_evento(evento_id, datos)
            flash('Evento actualizado exitosamente.', 'success')
            return redirect(url_for('eventos.lista'))
        except Exception as e:
            logger.error("Error al actualizar evento %s: %s", evento_id, e)
            flash('Error al actualizar evento. Verifique los datos e intente de nuevo.', 'danger')

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
        from fabric_db import get_siguiente_codigo
        codigo = get_siguiente_codigo(prefijo)
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
        from fabric_db import get_eventos_por_periodo
        eventos = get_eventos_por_periodo(anio, mes)

        # Cargar catálogos para mapear nombre → código
        catalogos_map = _cargar_mapas_catalogos()

        # Generar líneas del reporte (sin encabezado)
        lineas = []

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
                str(idx),                                                          # 1. Número secuencial
                ev.get('codigo_evento') or '',                                     # 2. Código del evento
                catalogos_map.get('tipo_evento', {}).get(ev.get('tipo_evento'), ''),# 3. Tipo de eventos de riesgo (T097)
                (ev.get('descripcion_evento') or '').replace('|', ' ').replace('\n', ' '),  # 4. Descripción
                str(ev.get('cantidad_eventos') or 1),                              # 5. Cantidad de eventos
                tipo_perdida_cod,                                                  # 6. Tipo de pérdida
                catalogos_map.get('consecuencia', {}).get(ev.get('consecuencia'), ''),      # 7. Consecuencia (T127)
                catalogos_map.get('linea_negocio', {}).get(ev.get('linea_negocios'), ''),   # 8. Línea de negocios (T072)
                catalogos_map.get('proceso', {}).get(ev.get('proceso_afectado'), ''),       # 9. Proceso afectado (T126)
                catalogos_map.get('producto', {}).get(ev.get('producto_afectado'), ''),     # 10. Producto afectado (T078)
                catalogos_map.get('servicio', {}).get(ev.get('servicio_afectado'), ''),     # 11. Servicio afectado (T078)
                catalogos_map.get('area', {}).get(ev.get('area_origen'), ''),               # 12. Área o departamento (T075)
                catalogos_map.get('marca_tarjeta', {}).get(ev.get('marca_tarjeta'), ''),    # 13. Marca de tarjeta (T081)
                catalogos_map.get('canal', {}).get(ev.get('canal_distribucion_afectado'), ''),  # 14. Canal distribución (T069)
                catalogos_map.get('factor_causa', {}).get(ev.get('factor_determinante'), ''),   # 15. Factor determinante (T125)
                catalogos_map.get('localidad', {}).get(ev.get('localidad_origen'), ''),     # 16. Localidad (T016)
                _fmt_fecha(ev.get('fecha_descubrimiento')),                        # 17. Fecha descubrimiento
                _fmt_fecha(ev.get('fecha_inicio_evento')),                         # 18. Fecha inicio
                _fmt_fecha(ev.get('fecha_finalizacion_evento')),                   # 19. Fecha finalización
                _fmt_fecha(ev.get('fecha_cierre_evento')),                         # 20. Fecha cierre
                ev.get('tipo_moneda_ocurrencia') or 'DOP',                         # 21. Tipo moneda (T050)
                _fmt_monto(ev.get('monto_dop')),                                   # 22. Monto pérdida MN
                _fmt_monto(ev.get('monto_moneda_origen')),                         # 23. Monto pérdida MO
                ev.get('cuenta_contable_monto') or '',                             # 24. Cuenta contable
                _fmt_fecha(ev.get('fecha_contabilizacion')),                       # 25. Fecha contabilización
                _fmt_monto(ev.get('monto_recuperado_seguros')),                    # 26. Recuperado seguros
                _fmt_monto(ev.get('monto_recuperado_otros')),                      # 27. Recuperado otros
                _fmt_fecha(ev.get('fecha_contab_recuperacion')),                   # 28. Fecha contab. recuperación
                catalogos_map.get('medio_pago', {}).get(ev.get('medio_pago'), ''),          # 29. Medio de pago (T061)
                catalogos_map.get('incidente_fraude', {}).get(ev.get('incidente_fraude'), ''),  # 30. Incidente fraudulento (T148)
                tipo_reg_cod,                                                      # 31. Tipo de registro
                estatus_cod,                                                       # 32. Estatus
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
        logger.error("Error al generar reporte RO02: %s", e)
        flash('Error al generar el reporte. Intente de nuevo más tarde.', 'danger')
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
        'localidad': 'cat_localidades',
        'producto': 'cat_productos',
        'servicio': 'cat_servicios',
        'moneda': 'cat_monedas',
    }
    from fabric_db import get_mapa_catalogo
    for clave, tabla in tablas.items():
        mapas[clave] = get_mapa_catalogo(tabla)
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
    if estatus in ('1', '2', '3', '4', '5'):
        return estatus
    if 'descubiert' in estatus_lower:
        return '1'
    elif 'pendiente' in estatus_lower:
        return '2'
    elif 'completado' in estatus_lower or 'finalizado' in estatus_lower:
        return '3'
    elif 'sin pérdida' in estatus_lower or 'sin perdida' in estatus_lower:
        return '4'
    elif 'desestim' in estatus_lower:
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
    """Formatea un monto para el reporte (solo enteros)."""
    if valor is None:
        return '0'
    return str(int(float(valor)))


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
        'incidente_fraude': form.get('incidente_fraude'),
        'fecha_descubrimiento': form.get('fecha_descubrimiento') or None,
        'fecha_inicio_evento': form.get('fecha_inicio_evento') or None,
        'fecha_finalizacion_evento': form.get('fecha_finalizacion_evento') or None,
        'fecha_cierre_evento': form.get('fecha_cierre_evento') or None,
        'monto_dop': form.get('monto_perdida_bruta_dop') or 0,
        'monto_recuperado_seguros': form.get('monto_recuperado_seguros') or 0,
        'monto_recuperado_otros': form.get('monto_recuperado_otros') or 0,
        'monto_moneda_origen': form.get('monto_moneda_origen') or None,
        'tipo_moneda_ocurrencia': form.get('tipo_moneda_ocurrencia') or 'DOP',
        'cuenta_contable_monto': form.get('cuenta_contable_monto'),
        'fecha_contabilizacion': form.get('fecha_contabilizacion') or None,
        'fecha_contab_recuperacion': form.get('fecha_contab_recuperacion') or None,
        'estatus_contabilizacion': form.get('estatus_contabilizacion'),
        'cantidad_eventos': form.get('cantidad_eventos') or 1,
        'area_origen': form.get('area_origen'),
        'localidad_origen': form.get('localidad_origen'),
        'linea_negocios': form.get('linea_negocios'),
        'proceso_afectado': form.get('proceso_afectado'),
        'producto_afectado': form.get('producto_afectado'),
        'servicio_afectado': form.get('servicio_afectado'),
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
        catalogos['localidades'] = get_catalogo('cat_localidades')
        catalogos['productos'] = get_catalogo('cat_productos')
        catalogos['servicios'] = get_catalogo('cat_servicios')
        catalogos['monedas'] = get_catalogo('cat_monedas')
        catalogos['estatus_contabilizacion'] = get_catalogo('cat_estatus_contabilizacion')
    except Exception:
        pass
    return catalogos

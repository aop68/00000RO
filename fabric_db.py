"""
Modulo de acceso a datos de riesgo operacional.
Conexion directa a Microsoft Fabric SQL via pyodbc + Azure AD.
"""
import struct
import pyodbc
from flask import current_app

# Cache global de credenciales Azure AD
_credential = None


def _get_credential():
    """Obtiene o reutiliza la credencial de Azure AD con cache persistente."""
    global _credential
    if _credential is None:
        from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions
        try:
            _credential = InteractiveBrowserCredential(
                cache_persistence_options=TokenCachePersistenceOptions(
                    allow_unencrypted_storage=False
                )
            )
        except Exception:
            # Fallback para PCs sin keyring/credential manager
            _credential = InteractiveBrowserCredential(
                cache_persistence_options=TokenCachePersistenceOptions(
                    allow_unencrypted_storage=True
                )
            )
    return _credential


def _get_access_token():
    """Obtiene un token de acceso para SQL Database."""
    credential = _get_credential()
    token = credential.get_token("https://database.windows.net/.default")
    token_bytes = token.token.encode('utf-16-le')
    return struct.pack('<I', len(token_bytes)) + token_bytes


def _get_connection():
    """Crea una conexion pyodbc a Microsoft Fabric SQL."""
    server = current_app.config.get('FABRIC_SERVER', '')
    database = current_app.config.get('FABRIC_DATABASE', '')

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Encrypt=Yes;TrustServerCertificate=No;"
    )

    token = _get_access_token()
    SQL_COPT_SS_ACCESS_TOKEN = 1256

    return pyodbc.connect(conn_str, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token})


def _execute_query(query, params=None, fetch='all'):
    """Ejecuta una consulta SQL y retorna resultados como lista de dicts."""
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch == 'none':
            conn.commit()
            return cursor.rowcount

        columns = [col[0] for col in cursor.description]
        if fetch == 'one':
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
        else:
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()


# ============================================================
# FUNCIONES PARA EVENTOS
# ============================================================

def get_eventos(filtros=None):
    """Obtiene lista de eventos de riesgo operacional."""
    query = """
        SELECT evento_id, codigo_evento, descripcion_evento, tipo_evento,
               categoria_evento, subcategoria_evento, fecha_descubrimiento,
               fecha_inicio_evento, fecha_finalizacion_evento,
               monto_dop, monto_recuperado_seguros, monto_recuperado_otros,
               perdida_neta,
               area_origen, linea_negocios, proceso_afectado,
               codigo_riesgo_asociado, estado_investigacion, aplica_plan_accion,
               canal_distribucion_afectado, medio_pago, marca_tarjeta,
               fecha_carga_sistema, usuario_carga
        FROM eventos_riesgo_operacional
        ORDER BY fecha_descubrimiento DESC
    """
    return _execute_query(query)


def get_evento(evento_id):
    """Obtiene un evento por su ID."""
    return _execute_query(
        "SELECT * FROM eventos_riesgo_operacional WHERE evento_id = ?",
        [evento_id], fetch='one'
    )


def crear_evento(datos):
    """Inserta un nuevo evento."""
    query = """
        INSERT INTO eventos_riesgo_operacional (
            codigo_evento, descripcion_evento, tipo_evento, categoria_evento,
            subcategoria_evento, estado_investigacion, nivel_riesgo_inherente,
            factor_determinante, causa_evento, consecuencia, tipo_perdida,
            tipo_registro, incidente_fraude,
            fecha_descubrimiento, fecha_inicio_evento,
            fecha_finalizacion_evento, fecha_cierre_evento,
            monto_dop, monto_recuperado_seguros,
            monto_recuperado_otros, monto_moneda_origen,
            tipo_moneda_ocurrencia, cuenta_contable_monto,
            fecha_contabilizacion, fecha_contab_recuperacion,
            estatus_contabilizacion, cantidad_eventos,
            area_origen, localidad_origen,
            linea_negocios, proceso_afectado,
            producto_afectado, servicio_afectado,
            codigo_riesgo_asociado, aplica_plan_accion,
            canal_distribucion_afectado, medio_pago, marca_tarjeta,
            detalle_causa_raiz, descripcion_extendida,
            fecha_carga_sistema, usuario_carga
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP, ?
        )
    """
    params = [
        datos.get('codigo_evento'),
        datos.get('descripcion_evento'),
        datos.get('tipo_evento'),
        datos.get('categoria_evento'),
        datos.get('subcategoria_evento'),
        datos.get('estado_investigacion'),
        datos.get('nivel_riesgo_inherente'),
        datos.get('factor_determinante'),
        datos.get('causa_evento'),
        datos.get('consecuencia'),
        datos.get('tipo_perdida'),
        datos.get('tipo_registro'),
        datos.get('incidente_fraude'),
        datos.get('fecha_descubrimiento') or None,
        datos.get('fecha_inicio_evento') or None,
        datos.get('fecha_finalizacion_evento') or None,
        datos.get('fecha_cierre_evento') or None,
        datos.get('monto_dop') or 0,
        datos.get('monto_recuperado_seguros') or 0,
        datos.get('monto_recuperado_otros') or 0,
        datos.get('monto_moneda_origen') or None,
        datos.get('tipo_moneda_ocurrencia') or 'DOP',
        datos.get('cuenta_contable_monto'),
        datos.get('fecha_contabilizacion') or None,
        datos.get('fecha_contab_recuperacion') or None,
        datos.get('estatus_contabilizacion'),
        datos.get('cantidad_eventos') or 1,
        datos.get('area_origen'),
        datos.get('localidad_origen'),
        datos.get('linea_negocios'),
        datos.get('proceso_afectado'),
        datos.get('producto_afectado'),
        datos.get('servicio_afectado'),
        datos.get('codigo_riesgo_asociado'),
        datos.get('aplica_plan_accion', False),
        datos.get('canal_distribucion_afectado'),
        datos.get('medio_pago'),
        datos.get('marca_tarjeta'),
        datos.get('detalle_causa_raiz'),
        datos.get('descripcion_extendida'),
        datos.get('usuario_carga'),
    ]
    return _execute_query(query, params, fetch='none')


def actualizar_evento(evento_id, datos):
    """Actualiza un evento existente."""
    query = """
        UPDATE eventos_riesgo_operacional SET
            codigo_evento = ?, descripcion_evento = ?,
            tipo_evento = ?, categoria_evento = ?,
            subcategoria_evento = ?,
            estado_investigacion = ?,
            nivel_riesgo_inherente = ?,
            factor_determinante = ?,
            causa_evento = ?, consecuencia = ?,
            tipo_perdida = ?, tipo_registro = ?,
            incidente_fraude = ?,
            fecha_descubrimiento = ?,
            fecha_inicio_evento = ?,
            fecha_finalizacion_evento = ?,
            fecha_cierre_evento = ?,
            monto_dop = ?,
            monto_recuperado_seguros = ?,
            monto_recuperado_otros = ?,
            monto_moneda_origen = ?,
            tipo_moneda_ocurrencia = ?,
            cuenta_contable_monto = ?,
            fecha_contabilizacion = ?,
            fecha_contab_recuperacion = ?,
            estatus_contabilizacion = ?,
            cantidad_eventos = ?,
            area_origen = ?, localidad_origen = ?,
            linea_negocios = ?,
            proceso_afectado = ?,
            producto_afectado = ?,
            servicio_afectado = ?,
            codigo_riesgo_asociado = ?,
            aplica_plan_accion = ?,
            canal_distribucion_afectado = ?,
            medio_pago = ?, marca_tarjeta = ?,
            detalle_causa_raiz = ?,
            descripcion_extendida = ?,
            fecha_modificacion_sistema = CURRENT_TIMESTAMP,
            usuario_carga = ?
        WHERE evento_id = ?
    """
    params = [
        datos.get('codigo_evento'),
        datos.get('descripcion_evento'),
        datos.get('tipo_evento'),
        datos.get('categoria_evento'),
        datos.get('subcategoria_evento'),
        datos.get('estado_investigacion'),
        datos.get('nivel_riesgo_inherente'),
        datos.get('factor_determinante'),
        datos.get('causa_evento'),
        datos.get('consecuencia'),
        datos.get('tipo_perdida'),
        datos.get('tipo_registro'),
        datos.get('incidente_fraude'),
        datos.get('fecha_descubrimiento') or None,
        datos.get('fecha_inicio_evento') or None,
        datos.get('fecha_finalizacion_evento') or None,
        datos.get('fecha_cierre_evento') or None,
        datos.get('monto_dop') or 0,
        datos.get('monto_recuperado_seguros') or 0,
        datos.get('monto_recuperado_otros') or 0,
        datos.get('monto_moneda_origen') or None,
        datos.get('tipo_moneda_ocurrencia') or 'DOP',
        datos.get('cuenta_contable_monto'),
        datos.get('fecha_contabilizacion') or None,
        datos.get('fecha_contab_recuperacion') or None,
        datos.get('estatus_contabilizacion'),
        datos.get('cantidad_eventos') or 1,
        datos.get('area_origen'),
        datos.get('localidad_origen'),
        datos.get('linea_negocios'),
        datos.get('proceso_afectado'),
        datos.get('producto_afectado'),
        datos.get('servicio_afectado'),
        datos.get('codigo_riesgo_asociado'),
        datos.get('aplica_plan_accion', False),
        datos.get('canal_distribucion_afectado'),
        datos.get('medio_pago'),
        datos.get('marca_tarjeta'),
        datos.get('detalle_causa_raiz'),
        datos.get('descripcion_extendida'),
        datos.get('usuario_modificacion'),
        evento_id,
    ]
    return _execute_query(query, params, fetch='none')


def get_siguiente_codigo(prefijo):
    """Obtiene el siguiente codigo de evento para un prefijo dado."""
    query = """
        SELECT TOP 1 codigo_evento
        FROM eventos_riesgo_operacional
        WHERE codigo_evento LIKE ?
        ORDER BY codigo_evento DESC
    """
    result = _execute_query(query, [prefijo + '%'], fetch='one')
    if result:
        ultimo = result['codigo_evento']
        seq = int(ultimo.split('-')[-1]) + 1
    else:
        seq = 1
    return f'{prefijo}{seq:03d}'


def get_eventos_por_periodo(anio, mes):
    """Obtiene eventos filtrados por anio y mes de descubrimiento."""
    query = """
        SELECT * FROM eventos_riesgo_operacional
        WHERE YEAR(fecha_descubrimiento) = ?
          AND MONTH(fecha_descubrimiento) = ?
        ORDER BY codigo_evento
    """
    return _execute_query(query, [int(anio), int(mes)])


# ============================================================
# FUNCIONES PARA PLANES DE ACCION
# ============================================================

def get_planes():
    """Obtiene lista de planes de accion."""
    query = """
        SELECT plan_id, codigo_plan, estatus, plan_accion, prioridad,
               tipo_plan_accion, origen_plan_accion, codigo_riesgo,
               vp_responsable, direccion_responsable, responsable,
               fecha_creacion_plan, fecha_compromiso_inicial,
               fecha_compromiso_actual, fecha_cierre,
               fecha_carga_sistema, usuario_carga
        FROM planes_accion
        ORDER BY fecha_creacion_plan DESC
    """
    return _execute_query(query)


def get_plan(plan_id):
    """Obtiene un plan por su ID."""
    return _execute_query(
        "SELECT * FROM planes_accion WHERE plan_id = ?",
        [plan_id], fetch='one'
    )


def crear_plan(datos):
    """Inserta un nuevo plan de accion."""
    query = """
        INSERT INTO planes_accion (
            codigo_plan, estatus, plan_accion, prioridad, tipo_plan_accion,
            origen_plan_accion, codigo_riesgo, vp_responsable,
            direccion_responsable, responsable, fecha_creacion_plan,
            fecha_compromiso_inicial, fecha_compromiso_actual, fecha_cierre,
            fecha_carga_sistema, usuario_carga
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP, ?
        )
    """
    params = [
        datos.get('codigo_plan'),
        datos.get('estatus'),
        datos.get('plan_accion'),
        datos.get('prioridad'),
        datos.get('tipo_plan_accion'),
        datos.get('origen_plan_accion'),
        datos.get('codigo_riesgo'),
        datos.get('vp_responsable'),
        datos.get('direccion_responsable'),
        datos.get('responsable'),
        datos.get('fecha_creacion_plan') or None,
        datos.get('fecha_compromiso_inicial') or None,
        datos.get('fecha_compromiso_actual') or None,
        datos.get('fecha_cierre') or None,
        datos.get('usuario_carga'),
    ]
    return _execute_query(query, params, fetch='none')


def actualizar_plan(plan_id, datos):
    """Actualiza un plan existente."""
    query = """
        UPDATE planes_accion SET
            codigo_plan = ?, estatus = ?,
            plan_accion = ?, prioridad = ?,
            tipo_plan_accion = ?,
            origen_plan_accion = ?,
            codigo_riesgo = ?,
            vp_responsable = ?,
            direccion_responsable = ?,
            responsable = ?,
            fecha_creacion_plan = ?,
            fecha_compromiso_inicial = ?,
            fecha_compromiso_actual = ?,
            fecha_cierre = ?,
            fecha_modificacion_sistema = CURRENT_TIMESTAMP,
            usuario_modificacion = ?
        WHERE plan_id = ?
    """
    params = [
        datos.get('codigo_plan'),
        datos.get('estatus'),
        datos.get('plan_accion'),
        datos.get('prioridad'),
        datos.get('tipo_plan_accion'),
        datos.get('origen_plan_accion'),
        datos.get('codigo_riesgo'),
        datos.get('vp_responsable'),
        datos.get('direccion_responsable'),
        datos.get('responsable'),
        datos.get('fecha_creacion_plan') or None,
        datos.get('fecha_compromiso_inicial') or None,
        datos.get('fecha_compromiso_actual') or None,
        datos.get('fecha_cierre') or None,
        datos.get('usuario_modificacion'),
        plan_id,
    ]
    return _execute_query(query, params, fetch='none')


# ============================================================
# FUNCIONES PARA RIESGOS Y CONTROLES
# ============================================================

def get_riesgos():
    """Obtiene lista de riesgos y controles."""
    query = """
        SELECT riesgo_control_id, codigo_riesgo, descripcion_riesgo,
               categoria_riesgo, riesgo_nivel_1, riesgo_nivel_2, riesgo_nivel_3,
               macroproceso, proceso, factor_riesgo, causa_raiz,
               impacto_financiero_dop, frecuencia_inherente,
               descripcion_control, tipo_control, frecuencia_ejecucion,
               grado_manualidad, vp_responsable_procedimiento,
               direccion_responsable_control, control_documentado,
               control_en_remediacion, fecha_carga_sistema, usuario_carga
        FROM riesgos_controles
        ORDER BY codigo_riesgo
    """
    return _execute_query(query)


def get_riesgo(riesgo_control_id):
    """Obtiene un riesgo por su ID."""
    return _execute_query(
        "SELECT * FROM riesgos_controles WHERE riesgo_control_id = ?",
        [riesgo_control_id], fetch='one'
    )


def crear_riesgo(datos):
    """Inserta un nuevo riesgo/control."""
    query = """
        INSERT INTO riesgos_controles (
            codigo_riesgo, descripcion_riesgo, categoria_riesgo,
            riesgo_nivel_1, riesgo_nivel_2, riesgo_nivel_3,
            macroproceso, proceso, factor_riesgo, causa_raiz,
            impacto_financiero_dop, frecuencia_inherente,
            descripcion_control, tipo_control, frecuencia_ejecucion,
            grado_manualidad, vp_responsable_procedimiento,
            direccion_responsable_control, control_documentado,
            control_en_remediacion, fecha_carga_sistema, usuario_carga
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            CURRENT_TIMESTAMP, ?
        )
    """
    params = [
        datos.get('codigo_riesgo'),
        datos.get('descripcion_riesgo'),
        datos.get('categoria_riesgo'),
        datos.get('riesgo_nivel_1'),
        datos.get('riesgo_nivel_2'),
        datos.get('riesgo_nivel_3'),
        datos.get('macroproceso'),
        datos.get('proceso'),
        datos.get('factor_riesgo'),
        datos.get('causa_raiz'),
        datos.get('impacto_financiero_dop') or None,
        datos.get('frecuencia_inherente'),
        datos.get('descripcion_control'),
        datos.get('tipo_control'),
        datos.get('frecuencia_ejecucion'),
        datos.get('grado_manualidad'),
        datos.get('vp_responsable_procedimiento'),
        datos.get('direccion_responsable_control'),
        datos.get('control_documentado', False),
        datos.get('control_en_remediacion', False),
        datos.get('usuario_carga'),
    ]
    return _execute_query(query, params, fetch='none')


def actualizar_riesgo(riesgo_control_id, datos):
    """Actualiza un riesgo/control existente."""
    query = """
        UPDATE riesgos_controles SET
            codigo_riesgo = ?, descripcion_riesgo = ?,
            categoria_riesgo = ?,
            riesgo_nivel_1 = ?, riesgo_nivel_2 = ?,
            riesgo_nivel_3 = ?,
            macroproceso = ?, proceso = ?,
            factor_riesgo = ?, causa_raiz = ?,
            impacto_financiero_dop = ?,
            frecuencia_inherente = ?,
            descripcion_control = ?,
            tipo_control = ?,
            frecuencia_ejecucion = ?,
            grado_manualidad = ?,
            vp_responsable_procedimiento = ?,
            direccion_responsable_control = ?,
            control_documentado = ?,
            control_en_remediacion = ?,
            fecha_modificacion_sistema = CURRENT_TIMESTAMP,
            usuario_modificacion = ?
        WHERE riesgo_control_id = ?
    """
    params = [
        datos.get('codigo_riesgo'),
        datos.get('descripcion_riesgo'),
        datos.get('categoria_riesgo'),
        datos.get('riesgo_nivel_1'),
        datos.get('riesgo_nivel_2'),
        datos.get('riesgo_nivel_3'),
        datos.get('macroproceso'),
        datos.get('proceso'),
        datos.get('factor_riesgo'),
        datos.get('causa_raiz'),
        datos.get('impacto_financiero_dop') or None,
        datos.get('frecuencia_inherente'),
        datos.get('descripcion_control'),
        datos.get('tipo_control'),
        datos.get('frecuencia_ejecucion'),
        datos.get('grado_manualidad'),
        datos.get('vp_responsable_procedimiento'),
        datos.get('direccion_responsable_control'),
        datos.get('control_documentado', False),
        datos.get('control_en_remediacion', False),
        datos.get('usuario_modificacion'),
        riesgo_control_id,
    ]
    return _execute_query(query, params, fetch='none')


# ============================================================
# FUNCIONES PARA CATALOGOS
# ============================================================

_TABLAS_PERMITIDAS = [
    'cat_areas_organizacion', 'cat_canales', 'cat_consecuencias',
    'cat_estado_evento', 'cat_estado_plan_accion', 'cat_factor_causa',
    'cat_frecuencia_control', 'cat_incidentes_fraude', 'cat_linea_negocio',
    'cat_medio_pago', 'cat_naturaleza_perdida', 'cat_probabilidad',
    'cat_procesos', 'cat_severidad', 'cat_tipo_control', 'cat_tipo_evento_ro02',
    'cat_marcas_tarjetas', 'cat_localidades', 'cat_productos', 'cat_servicios',
    'cat_monedas', 'cat_estatus_contabilizacion'
]


def get_catalogo(tabla):
    """Obtiene datos de una tabla de catalogo."""
    if tabla not in _TABLAS_PERMITIDAS:
        raise ValueError(f"Tabla de catalogo no permitida: {tabla}")
    return _execute_query(f"SELECT * FROM {tabla} ORDER BY 1")


def get_mapa_catalogo(tabla):
    """Obtiene un mapa nombre->codigo de una tabla de catalogo."""
    if tabla not in _TABLAS_PERMITIDAS:
        return {}
    try:
        rows = _execute_query(f"SELECT nombre, codigo FROM {tabla}")
        return {row['nombre']: row['codigo'] for row in rows}
    except Exception:
        return {}


# ============================================================
# FUNCIONES PARA DASHBOARD / ESTADISTICAS
# ============================================================

def get_estadisticas():
    """Obtiene estadisticas generales para el dashboard."""
    stats = {}
    queries = {
        'total_eventos': "SELECT COUNT(*) as total FROM eventos_riesgo_operacional",
        'total_planes': "SELECT COUNT(*) as total FROM planes_accion",
        'total_riesgos': "SELECT COUNT(*) as total FROM riesgos_controles",
        'planes_abiertos': "SELECT COUNT(*) as total FROM planes_accion WHERE estatus NOT IN ('Cerrado', 'Completado', 'Completada')",
        'perdida_total': "SELECT ISNULL(SUM(perdida_neta), 0) as total FROM eventos_riesgo_operacional",
    }
    for key, query in queries.items():
        try:
            result = _execute_query(query, fetch='one')
            stats[key] = result['total'] if result else 0
        except Exception:
            stats[key] = 0
    return stats

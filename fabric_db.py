"""
Módulo de conexión a la base de datos de Microsoft Fabric.
Provee funciones para ejecutar queries contra la BD de riesgo operacional.
Usa azure-identity para obtener tokens de Azure AD.
"""
import struct
import pyodbc
from flask import current_app
from azure.identity import InteractiveBrowserCredential, TokenCachePersistenceOptions

# Cache global del credential para no pedir login en cada request
_credential = None


def _get_credential():
    """Obtiene (o reutiliza) el credential de Azure AD con cache persistente."""
    global _credential
    if _credential is None:
        cache_options = TokenCachePersistenceOptions(name="giro_token_cache")
        _credential = InteractiveBrowserCredential(
            cache_persistence_options=cache_options
        )
    return _credential


def _get_access_token():
    """Obtiene un access token para SQL Database."""
    credential = _get_credential()
    token = credential.get_token("https://database.windows.net/.default")
    # Convertir al formato que espera pyodbc (SQL_COPT_SS_ACCESS_TOKEN = 1256)
    token_bytes = token.token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    return token_struct


def get_fabric_connection():
    """Obtiene una conexión a la BD de Fabric usando token de Azure AD."""
    from config import Config
    server = Config.FABRIC_SERVER
    database = Config.FABRIC_DATABASE

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
    )

    token_struct = _get_access_token()
    return pyodbc.connect(conn_str, attrs_before={1256: token_struct})


def execute_query(query, params=None, fetch='all'):
    """
    Ejecuta un query SELECT contra Fabric y retorna resultados como lista de dicts.
    fetch: 'all', 'one', o 'none' (para INSERT/UPDATE).
    """
    conn = get_fabric_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch == 'none':
            conn.commit()
            return cursor.rowcount

        columns = [column[0] for column in cursor.description]
        if fetch == 'one':
            row = cursor.fetchone()
            return dict(zip(columns, row)) if row else None
        else:
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    except pyodbc.Error as e:
        current_app.logger.error(f"Error de base de datos Fabric: {e}")
        raise
    finally:
        conn.close()


def execute_insert(query, params=None):
    """Ejecuta un INSERT/UPDATE/DELETE contra Fabric."""
    return execute_query(query, params, fetch='none')


# ============================================================
# FUNCIONES PARA EVENTOS
# ============================================================

def get_eventos(filtros=None):
    """Obtiene lista de eventos de riesgo operacional."""
    query = """
        SELECT evento_id, codigo_evento, descripcion_evento, tipo_evento,
               categoria_evento, subcategoria_evento, fecha_descubrimiento,
               fecha_inicio_evento, fecha_finalizacion_evento,
               monto_perdida_bruta_dop, monto_recuperado_dop, monto_perdida_neta_dop,
               monto_usd, area_origen, linea_negocios, proceso_afectado,
               codigo_riesgo_asociado, estado_investigacion, aplica_plan_accion,
               canal_distribucion_afectado, medio_pago, marca_tarjeta,
               fecha_carga_sistema, usuario_carga
        FROM dbo.eventos_riesgo_operacional
        ORDER BY fecha_descubrimiento DESC
    """
    return execute_query(query)


def get_evento(evento_id):
    """Obtiene un evento por su ID."""
    query = """
        SELECT * FROM dbo.eventos_riesgo_operacional
        WHERE evento_id = ?
    """
    return execute_query(query, [evento_id], fetch='one')


def crear_evento(datos):
    """Inserta un nuevo evento."""
    query = """
        INSERT INTO dbo.eventos_riesgo_operacional (
            codigo_evento, descripcion_evento, tipo_evento, categoria_evento,
            subcategoria_evento, fecha_descubrimiento, fecha_inicio_evento,
            fecha_finalizacion_evento, monto_perdida_bruta_dop, monto_recuperado_dop,
            monto_perdida_neta_dop, monto_usd, area_origen, linea_negocios,
            proceso_afectado, codigo_riesgo_asociado, estado_investigacion,
            aplica_plan_accion, canal_distribucion_afectado, medio_pago,
            marca_tarjeta, fecha_carga_sistema, usuario_carga
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
    """
    params = [
        datos.get('codigo_evento'), datos.get('descripcion_evento'),
        datos.get('tipo_evento'), datos.get('categoria_evento'),
        datos.get('subcategoria_evento'), datos.get('fecha_descubrimiento'),
        datos.get('fecha_inicio_evento'), datos.get('fecha_finalizacion_evento'),
        datos.get('monto_perdida_bruta_dop'), datos.get('monto_recuperado_dop'),
        datos.get('monto_perdida_neta_dop'), datos.get('monto_usd'),
        datos.get('area_origen'), datos.get('linea_negocios'),
        datos.get('proceso_afectado'), datos.get('codigo_riesgo_asociado'),
        datos.get('estado_investigacion'), datos.get('aplica_plan_accion'),
        datos.get('canal_distribucion_afectado'), datos.get('medio_pago'),
        datos.get('marca_tarjeta'), datos.get('usuario_carga')
    ]
    return execute_insert(query, params)


def actualizar_evento(evento_id, datos):
    """Actualiza un evento existente."""
    query = """
        UPDATE dbo.eventos_riesgo_operacional SET
            codigo_evento = ?, descripcion_evento = ?, tipo_evento = ?,
            categoria_evento = ?, subcategoria_evento = ?,
            fecha_descubrimiento = ?, fecha_inicio_evento = ?,
            fecha_finalizacion_evento = ?, monto_perdida_bruta_dop = ?,
            monto_recuperado_dop = ?, monto_perdida_neta_dop = ?,
            monto_usd = ?, area_origen = ?, linea_negocios = ?,
            proceso_afectado = ?, codigo_riesgo_asociado = ?,
            estado_investigacion = ?, aplica_plan_accion = ?,
            canal_distribucion_afectado = ?, medio_pago = ?,
            marca_tarjeta = ?, fecha_modificacion_sistema = GETDATE(),
            usuario_modificacion = ?
        WHERE evento_id = ?
    """
    params = [
        datos.get('codigo_evento'), datos.get('descripcion_evento'),
        datos.get('tipo_evento'), datos.get('categoria_evento'),
        datos.get('subcategoria_evento'), datos.get('fecha_descubrimiento'),
        datos.get('fecha_inicio_evento'), datos.get('fecha_finalizacion_evento'),
        datos.get('monto_perdida_bruta_dop'), datos.get('monto_recuperado_dop'),
        datos.get('monto_perdida_neta_dop'), datos.get('monto_usd'),
        datos.get('area_origen'), datos.get('linea_negocios'),
        datos.get('proceso_afectado'), datos.get('codigo_riesgo_asociado'),
        datos.get('estado_investigacion'), datos.get('aplica_plan_accion'),
        datos.get('canal_distribucion_afectado'), datos.get('medio_pago'),
        datos.get('marca_tarjeta'), datos.get('usuario_modificacion'),
        evento_id
    ]
    return execute_insert(query, params)


# ============================================================
# FUNCIONES PARA PLANES DE ACCIÓN
# ============================================================

def get_planes():
    """Obtiene lista de planes de acción."""
    query = """
        SELECT plan_id, codigo_plan, estatus, plan_accion, prioridad,
               tipo_plan_accion, origen_plan_accion, codigo_riesgo,
               vp_responsable, direccion_responsable, responsable,
               fecha_creacion_plan, fecha_compromiso_inicial,
               fecha_compromiso_actual, fecha_cierre,
               fecha_carga_sistema, usuario_carga
        FROM dbo.planes_accion
        ORDER BY fecha_creacion_plan DESC
    """
    return execute_query(query)


def get_plan(plan_id):
    """Obtiene un plan por su ID."""
    query = "SELECT * FROM dbo.planes_accion WHERE plan_id = ?"
    return execute_query(query, [plan_id], fetch='one')


def crear_plan(datos):
    """Inserta un nuevo plan de acción."""
    query = """
        INSERT INTO dbo.planes_accion (
            codigo_plan, estatus, plan_accion, prioridad, tipo_plan_accion,
            origen_plan_accion, codigo_riesgo, vp_responsable,
            direccion_responsable, responsable, fecha_creacion_plan,
            fecha_compromiso_inicial, fecha_compromiso_actual, fecha_cierre,
            fecha_carga_sistema, usuario_carga
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
    """
    params = [
        datos.get('codigo_plan'), datos.get('estatus'), datos.get('plan_accion'),
        datos.get('prioridad'), datos.get('tipo_plan_accion'),
        datos.get('origen_plan_accion'), datos.get('codigo_riesgo'),
        datos.get('vp_responsable'), datos.get('direccion_responsable'),
        datos.get('responsable'), datos.get('fecha_creacion_plan'),
        datos.get('fecha_compromiso_inicial'), datos.get('fecha_compromiso_actual'),
        datos.get('fecha_cierre'), datos.get('usuario_carga')
    ]
    return execute_insert(query, params)


def actualizar_plan(plan_id, datos):
    """Actualiza un plan existente."""
    query = """
        UPDATE dbo.planes_accion SET
            codigo_plan = ?, estatus = ?, plan_accion = ?, prioridad = ?,
            tipo_plan_accion = ?, origen_plan_accion = ?, codigo_riesgo = ?,
            vp_responsable = ?, direccion_responsable = ?, responsable = ?,
            fecha_creacion_plan = ?, fecha_compromiso_inicial = ?,
            fecha_compromiso_actual = ?, fecha_cierre = ?,
            fecha_modificacion_sistema = GETDATE(), usuario_modificacion = ?
        WHERE plan_id = ?
    """
    params = [
        datos.get('codigo_plan'), datos.get('estatus'), datos.get('plan_accion'),
        datos.get('prioridad'), datos.get('tipo_plan_accion'),
        datos.get('origen_plan_accion'), datos.get('codigo_riesgo'),
        datos.get('vp_responsable'), datos.get('direccion_responsable'),
        datos.get('responsable'), datos.get('fecha_creacion_plan'),
        datos.get('fecha_compromiso_inicial'), datos.get('fecha_compromiso_actual'),
        datos.get('fecha_cierre'), datos.get('usuario_modificacion'),
        plan_id
    ]
    return execute_insert(query, params)


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
        FROM dbo.riesgos_controles
        ORDER BY codigo_riesgo
    """
    return execute_query(query)


def get_riesgo(riesgo_control_id):
    """Obtiene un riesgo por su ID."""
    query = "SELECT * FROM dbo.riesgos_controles WHERE riesgo_control_id = ?"
    return execute_query(query, [riesgo_control_id], fetch='one')


def crear_riesgo(datos):
    """Inserta un nuevo riesgo/control."""
    query = """
        INSERT INTO dbo.riesgos_controles (
            codigo_riesgo, descripcion_riesgo, categoria_riesgo,
            riesgo_nivel_1, riesgo_nivel_2, riesgo_nivel_3,
            macroproceso, proceso, factor_riesgo, causa_raiz,
            impacto_financiero_dop, frecuencia_inherente,
            descripcion_control, tipo_control, frecuencia_ejecucion,
            grado_manualidad, vp_responsable_procedimiento,
            direccion_responsable_control, control_documentado,
            control_en_remediacion, fecha_carga_sistema, usuario_carga
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE(), ?)
    """
    params = [
        datos.get('codigo_riesgo'), datos.get('descripcion_riesgo'),
        datos.get('categoria_riesgo'), datos.get('riesgo_nivel_1'),
        datos.get('riesgo_nivel_2'), datos.get('riesgo_nivel_3'),
        datos.get('macroproceso'), datos.get('proceso'),
        datos.get('factor_riesgo'), datos.get('causa_raiz'),
        datos.get('impacto_financiero_dop'), datos.get('frecuencia_inherente'),
        datos.get('descripcion_control'), datos.get('tipo_control'),
        datos.get('frecuencia_ejecucion'), datos.get('grado_manualidad'),
        datos.get('vp_responsable_procedimiento'),
        datos.get('direccion_responsable_control'),
        datos.get('control_documentado'), datos.get('control_en_remediacion'),
        datos.get('usuario_carga')
    ]
    return execute_insert(query, params)


def actualizar_riesgo(riesgo_control_id, datos):
    """Actualiza un riesgo/control existente."""
    query = """
        UPDATE dbo.riesgos_controles SET
            codigo_riesgo = ?, descripcion_riesgo = ?, categoria_riesgo = ?,
            riesgo_nivel_1 = ?, riesgo_nivel_2 = ?, riesgo_nivel_3 = ?,
            macroproceso = ?, proceso = ?, factor_riesgo = ?, causa_raiz = ?,
            impacto_financiero_dop = ?, frecuencia_inherente = ?,
            descripcion_control = ?, tipo_control = ?, frecuencia_ejecucion = ?,
            grado_manualidad = ?, vp_responsable_procedimiento = ?,
            direccion_responsable_control = ?, control_documentado = ?,
            control_en_remediacion = ?,
            fecha_modificacion_sistema = GETDATE(), usuario_modificacion = ?
        WHERE riesgo_control_id = ?
    """
    params = [
        datos.get('codigo_riesgo'), datos.get('descripcion_riesgo'),
        datos.get('categoria_riesgo'), datos.get('riesgo_nivel_1'),
        datos.get('riesgo_nivel_2'), datos.get('riesgo_nivel_3'),
        datos.get('macroproceso'), datos.get('proceso'),
        datos.get('factor_riesgo'), datos.get('causa_raiz'),
        datos.get('impacto_financiero_dop'), datos.get('frecuencia_inherente'),
        datos.get('descripcion_control'), datos.get('tipo_control'),
        datos.get('frecuencia_ejecucion'), datos.get('grado_manualidad'),
        datos.get('vp_responsable_procedimiento'),
        datos.get('direccion_responsable_control'),
        datos.get('control_documentado'), datos.get('control_en_remediacion'),
        datos.get('usuario_modificacion'), riesgo_control_id
    ]
    return execute_insert(query, params)


# ============================================================
# FUNCIONES PARA CATÁLOGOS
# ============================================================

def get_catalogo(tabla):
    """Obtiene datos de una tabla de catálogo."""
    tablas_permitidas = [
        'cat_areas_organizacion', 'cat_canales', 'cat_consecuencias',
        'cat_estado_evento', 'cat_estado_plan_accion', 'cat_factor_causa',
        'cat_frecuencia_control', 'cat_incidentes_fraude', 'cat_linea_negocio',
        'cat_medio_pago', 'cat_naturaleza_perdida', 'cat_probabilidad',
        'cat_procesos', 'cat_severidad', 'cat_tipo_control', 'cat_tipo_evento'
    ]
    if tabla not in tablas_permitidas:
        raise ValueError(f"Tabla de catálogo no permitida: {tabla}")
    query = f"SELECT * FROM dbo.{tabla} ORDER BY 1"
    return execute_query(query)


# ============================================================
# FUNCIONES PARA DASHBOARD / ESTADÍSTICAS
# ============================================================

def get_estadisticas():
    """Obtiene estadísticas generales para el dashboard."""
    stats = {}
    try:
        stats['total_eventos'] = execute_query(
            "SELECT COUNT(*) as total FROM dbo.eventos_riesgo_operacional",
            fetch='one'
        )['total']
    except Exception:
        stats['total_eventos'] = 0

    try:
        stats['total_planes'] = execute_query(
            "SELECT COUNT(*) as total FROM dbo.planes_accion",
            fetch='one'
        )['total']
    except Exception:
        stats['total_planes'] = 0

    try:
        stats['total_riesgos'] = execute_query(
            "SELECT COUNT(*) as total FROM dbo.riesgos_controles",
            fetch='one'
        )['total']
    except Exception:
        stats['total_riesgos'] = 0

    try:
        stats['planes_abiertos'] = execute_query(
            "SELECT COUNT(*) as total FROM dbo.planes_accion WHERE estatus NOT IN ('Cerrado', 'Completado')",
            fetch='one'
        )['total']
    except Exception:
        stats['planes_abiertos'] = 0

    try:
        stats['perdida_total'] = execute_query(
            "SELECT ISNULL(SUM(monto_perdida_neta_dop), 0) as total FROM dbo.eventos_riesgo_operacional",
            fetch='one'
        )['total']
    except Exception:
        stats['perdida_total'] = 0

    return stats

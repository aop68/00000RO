"""
Módulo de acceso a datos de riesgo operacional.
Usa SQLAlchemy (PostgreSQL en Railway, SQLite en desarrollo local).
Reemplaza la conexión directa a Microsoft Fabric via pyodbc.
"""
from datetime import date, datetime
from flask import current_app
from extensions import db
from sqlalchemy import text


# ============================================================
# FUNCIONES PARA EVENTOS
# ============================================================

def get_eventos(filtros=None):
    """Obtiene lista de eventos de riesgo operacional."""
    query = text("""
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
        ORDER BY fecha_descubrimiento DESC NULLS LAST
    """)
    result = db.session.execute(query)
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def get_evento(evento_id):
    """Obtiene un evento por su ID."""
    query = text("SELECT * FROM eventos_riesgo_operacional WHERE evento_id = :id")
    result = db.session.execute(query, {'id': evento_id})
    columns = result.keys()
    row = result.fetchone()
    return dict(zip(columns, row)) if row else None


def crear_evento(datos):
    """Inserta un nuevo evento."""
    query = text("""
        INSERT INTO eventos_riesgo_operacional (
            codigo_evento, descripcion_evento, tipo_evento, categoria_evento,
            subcategoria_evento, estado_investigacion, nivel_riesgo_inherente,
            factor_determinante, causa_evento, consecuencia, tipo_perdida,
            tipo_registro, fecha_descubrimiento, fecha_inicio_evento,
            fecha_finalizacion_evento, monto_dop, monto_recuperado_seguros,
            monto_recuperado_otros, monto_moneda_origen,
            area_origen, linea_negocios, proceso_afectado,
            codigo_riesgo_asociado, aplica_plan_accion,
            canal_distribucion_afectado, medio_pago, marca_tarjeta,
            fecha_carga_sistema, usuario_carga
        ) VALUES (
            :codigo_evento, :descripcion_evento, :tipo_evento, :categoria_evento,
            :subcategoria_evento, :estado_investigacion, :nivel_riesgo_inherente,
            :factor_determinante, :causa_evento, :consecuencia, :tipo_perdida,
            :tipo_registro, :fecha_descubrimiento, :fecha_inicio_evento,
            :fecha_finalizacion_evento, :monto_dop, :monto_recuperado_seguros,
            :monto_recuperado_otros, :monto_moneda_origen,
            :area_origen, :linea_negocios, :proceso_afectado,
            :codigo_riesgo_asociado, :aplica_plan_accion,
            :canal_distribucion_afectado, :medio_pago, :marca_tarjeta,
            CURRENT_TIMESTAMP, :usuario_carga
        )
    """)
    params = {
        'codigo_evento': datos.get('codigo_evento'),
        'descripcion_evento': datos.get('descripcion_evento'),
        'tipo_evento': datos.get('tipo_evento'),
        'categoria_evento': datos.get('categoria_evento'),
        'subcategoria_evento': datos.get('subcategoria_evento'),
        'estado_investigacion': datos.get('estado_investigacion'),
        'nivel_riesgo_inherente': datos.get('nivel_riesgo_inherente'),
        'factor_determinante': datos.get('factor_determinante'),
        'causa_evento': datos.get('causa_evento'),
        'consecuencia': datos.get('consecuencia'),
        'tipo_perdida': datos.get('tipo_perdida'),
        'tipo_registro': datos.get('tipo_registro'),
        'fecha_descubrimiento': datos.get('fecha_descubrimiento') or None,
        'fecha_inicio_evento': datos.get('fecha_inicio_evento') or None,
        'fecha_finalizacion_evento': datos.get('fecha_finalizacion_evento') or None,
        'monto_dop': datos.get('monto_dop') or 0,
        'monto_recuperado_seguros': datos.get('monto_recuperado_seguros') or 0,
        'monto_recuperado_otros': datos.get('monto_recuperado_otros') or 0,
        'monto_moneda_origen': datos.get('monto_moneda_origen') or None,
        'area_origen': datos.get('area_origen'),
        'linea_negocios': datos.get('linea_negocios'),
        'proceso_afectado': datos.get('proceso_afectado'),
        'codigo_riesgo_asociado': datos.get('codigo_riesgo_asociado'),
        'aplica_plan_accion': datos.get('aplica_plan_accion', False),
        'canal_distribucion_afectado': datos.get('canal_distribucion_afectado'),
        'medio_pago': datos.get('medio_pago'),
        'marca_tarjeta': datos.get('marca_tarjeta'),
        'usuario_carga': datos.get('usuario_carga'),
    }
    db.session.execute(query, params)
    db.session.commit()
    return 1


def actualizar_evento(evento_id, datos):
    """Actualiza un evento existente."""
    query = text("""
        UPDATE eventos_riesgo_operacional SET
            codigo_evento = :codigo_evento, descripcion_evento = :descripcion_evento,
            tipo_evento = :tipo_evento, categoria_evento = :categoria_evento,
            subcategoria_evento = :subcategoria_evento,
            estado_investigacion = :estado_investigacion,
            nivel_riesgo_inherente = :nivel_riesgo_inherente,
            factor_determinante = :factor_determinante,
            causa_evento = :causa_evento, consecuencia = :consecuencia,
            tipo_perdida = :tipo_perdida, tipo_registro = :tipo_registro,
            fecha_descubrimiento = :fecha_descubrimiento,
            fecha_inicio_evento = :fecha_inicio_evento,
            fecha_finalizacion_evento = :fecha_finalizacion_evento,
            monto_dop = :monto_dop,
            monto_recuperado_seguros = :monto_recuperado_seguros,
            monto_recuperado_otros = :monto_recuperado_otros,
            monto_moneda_origen = :monto_moneda_origen,
            area_origen = :area_origen, linea_negocios = :linea_negocios,
            proceso_afectado = :proceso_afectado,
            codigo_riesgo_asociado = :codigo_riesgo_asociado,
            aplica_plan_accion = :aplica_plan_accion,
            canal_distribucion_afectado = :canal_distribucion_afectado,
            medio_pago = :medio_pago, marca_tarjeta = :marca_tarjeta,
            fecha_modificacion_sistema = CURRENT_TIMESTAMP,
            usuario_carga = :usuario_carga
        WHERE evento_id = :evento_id
    """)
    params = {
        'codigo_evento': datos.get('codigo_evento'),
        'descripcion_evento': datos.get('descripcion_evento'),
        'tipo_evento': datos.get('tipo_evento'),
        'categoria_evento': datos.get('categoria_evento'),
        'subcategoria_evento': datos.get('subcategoria_evento'),
        'estado_investigacion': datos.get('estado_investigacion'),
        'nivel_riesgo_inherente': datos.get('nivel_riesgo_inherente'),
        'factor_determinante': datos.get('factor_determinante'),
        'causa_evento': datos.get('causa_evento'),
        'consecuencia': datos.get('consecuencia'),
        'tipo_perdida': datos.get('tipo_perdida'),
        'tipo_registro': datos.get('tipo_registro'),
        'fecha_descubrimiento': datos.get('fecha_descubrimiento') or None,
        'fecha_inicio_evento': datos.get('fecha_inicio_evento') or None,
        'fecha_finalizacion_evento': datos.get('fecha_finalizacion_evento') or None,
        'monto_dop': datos.get('monto_dop') or 0,
        'monto_recuperado_seguros': datos.get('monto_recuperado_seguros') or 0,
        'monto_recuperado_otros': datos.get('monto_recuperado_otros') or 0,
        'monto_moneda_origen': datos.get('monto_moneda_origen') or None,
        'area_origen': datos.get('area_origen'),
        'linea_negocios': datos.get('linea_negocios'),
        'proceso_afectado': datos.get('proceso_afectado'),
        'codigo_riesgo_asociado': datos.get('codigo_riesgo_asociado'),
        'aplica_plan_accion': datos.get('aplica_plan_accion', False),
        'canal_distribucion_afectado': datos.get('canal_distribucion_afectado'),
        'medio_pago': datos.get('medio_pago'),
        'marca_tarjeta': datos.get('marca_tarjeta'),
        'usuario_carga': datos.get('usuario_modificacion'),
        'evento_id': evento_id,
    }
    db.session.execute(query, params)
    db.session.commit()
    return 1


# ============================================================
# FUNCIONES PARA PLANES DE ACCIÓN
# ============================================================

def get_planes():
    """Obtiene lista de planes de acción."""
    query = text("""
        SELECT plan_id, codigo_plan, estatus, plan_accion, prioridad,
               tipo_plan_accion, origen_plan_accion, codigo_riesgo,
               vp_responsable, direccion_responsable, responsable,
               fecha_creacion_plan, fecha_compromiso_inicial,
               fecha_compromiso_actual, fecha_cierre,
               fecha_carga_sistema, usuario_carga
        FROM planes_accion
        ORDER BY fecha_creacion_plan DESC NULLS LAST
    """)
    result = db.session.execute(query)
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def get_plan(plan_id):
    """Obtiene un plan por su ID."""
    query = text("SELECT * FROM planes_accion WHERE plan_id = :id")
    result = db.session.execute(query, {'id': plan_id})
    columns = result.keys()
    row = result.fetchone()
    return dict(zip(columns, row)) if row else None


def crear_plan(datos):
    """Inserta un nuevo plan de acción."""
    query = text("""
        INSERT INTO planes_accion (
            codigo_plan, estatus, plan_accion, prioridad, tipo_plan_accion,
            origen_plan_accion, codigo_riesgo, vp_responsable,
            direccion_responsable, responsable, fecha_creacion_plan,
            fecha_compromiso_inicial, fecha_compromiso_actual, fecha_cierre,
            fecha_carga_sistema, usuario_carga
        ) VALUES (
            :codigo_plan, :estatus, :plan_accion, :prioridad, :tipo_plan_accion,
            :origen_plan_accion, :codigo_riesgo, :vp_responsable,
            :direccion_responsable, :responsable, :fecha_creacion_plan,
            :fecha_compromiso_inicial, :fecha_compromiso_actual, :fecha_cierre,
            CURRENT_TIMESTAMP, :usuario_carga
        )
    """)
    params = {
        'codigo_plan': datos.get('codigo_plan'),
        'estatus': datos.get('estatus'),
        'plan_accion': datos.get('plan_accion'),
        'prioridad': datos.get('prioridad'),
        'tipo_plan_accion': datos.get('tipo_plan_accion'),
        'origen_plan_accion': datos.get('origen_plan_accion'),
        'codigo_riesgo': datos.get('codigo_riesgo'),
        'vp_responsable': datos.get('vp_responsable'),
        'direccion_responsable': datos.get('direccion_responsable'),
        'responsable': datos.get('responsable'),
        'fecha_creacion_plan': datos.get('fecha_creacion_plan') or None,
        'fecha_compromiso_inicial': datos.get('fecha_compromiso_inicial') or None,
        'fecha_compromiso_actual': datos.get('fecha_compromiso_actual') or None,
        'fecha_cierre': datos.get('fecha_cierre') or None,
        'usuario_carga': datos.get('usuario_carga'),
    }
    db.session.execute(query, params)
    db.session.commit()
    return 1


def actualizar_plan(plan_id, datos):
    """Actualiza un plan existente."""
    query = text("""
        UPDATE planes_accion SET
            codigo_plan = :codigo_plan, estatus = :estatus,
            plan_accion = :plan_accion, prioridad = :prioridad,
            tipo_plan_accion = :tipo_plan_accion,
            origen_plan_accion = :origen_plan_accion,
            codigo_riesgo = :codigo_riesgo,
            vp_responsable = :vp_responsable,
            direccion_responsable = :direccion_responsable,
            responsable = :responsable,
            fecha_creacion_plan = :fecha_creacion_plan,
            fecha_compromiso_inicial = :fecha_compromiso_inicial,
            fecha_compromiso_actual = :fecha_compromiso_actual,
            fecha_cierre = :fecha_cierre,
            fecha_modificacion_sistema = CURRENT_TIMESTAMP,
            usuario_modificacion = :usuario_modificacion
        WHERE plan_id = :plan_id
    """)
    params = {
        'codigo_plan': datos.get('codigo_plan'),
        'estatus': datos.get('estatus'),
        'plan_accion': datos.get('plan_accion'),
        'prioridad': datos.get('prioridad'),
        'tipo_plan_accion': datos.get('tipo_plan_accion'),
        'origen_plan_accion': datos.get('origen_plan_accion'),
        'codigo_riesgo': datos.get('codigo_riesgo'),
        'vp_responsable': datos.get('vp_responsable'),
        'direccion_responsable': datos.get('direccion_responsable'),
        'responsable': datos.get('responsable'),
        'fecha_creacion_plan': datos.get('fecha_creacion_plan') or None,
        'fecha_compromiso_inicial': datos.get('fecha_compromiso_inicial') or None,
        'fecha_compromiso_actual': datos.get('fecha_compromiso_actual') or None,
        'fecha_cierre': datos.get('fecha_cierre') or None,
        'usuario_modificacion': datos.get('usuario_modificacion'),
        'plan_id': plan_id,
    }
    db.session.execute(query, params)
    db.session.commit()
    return 1


# ============================================================
# FUNCIONES PARA RIESGOS Y CONTROLES
# ============================================================

def get_riesgos():
    """Obtiene lista de riesgos y controles."""
    query = text("""
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
    """)
    result = db.session.execute(query)
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


def get_riesgo(riesgo_control_id):
    """Obtiene un riesgo por su ID."""
    query = text("SELECT * FROM riesgos_controles WHERE riesgo_control_id = :id")
    result = db.session.execute(query, {'id': riesgo_control_id})
    columns = result.keys()
    row = result.fetchone()
    return dict(zip(columns, row)) if row else None


def crear_riesgo(datos):
    """Inserta un nuevo riesgo/control."""
    query = text("""
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
            :codigo_riesgo, :descripcion_riesgo, :categoria_riesgo,
            :riesgo_nivel_1, :riesgo_nivel_2, :riesgo_nivel_3,
            :macroproceso, :proceso, :factor_riesgo, :causa_raiz,
            :impacto_financiero_dop, :frecuencia_inherente,
            :descripcion_control, :tipo_control, :frecuencia_ejecucion,
            :grado_manualidad, :vp_responsable_procedimiento,
            :direccion_responsable_control, :control_documentado,
            :control_en_remediacion, CURRENT_TIMESTAMP, :usuario_carga
        )
    """)
    params = {
        'codigo_riesgo': datos.get('codigo_riesgo'),
        'descripcion_riesgo': datos.get('descripcion_riesgo'),
        'categoria_riesgo': datos.get('categoria_riesgo'),
        'riesgo_nivel_1': datos.get('riesgo_nivel_1'),
        'riesgo_nivel_2': datos.get('riesgo_nivel_2'),
        'riesgo_nivel_3': datos.get('riesgo_nivel_3'),
        'macroproceso': datos.get('macroproceso'),
        'proceso': datos.get('proceso'),
        'factor_riesgo': datos.get('factor_riesgo'),
        'causa_raiz': datos.get('causa_raiz'),
        'impacto_financiero_dop': datos.get('impacto_financiero_dop') or None,
        'frecuencia_inherente': datos.get('frecuencia_inherente'),
        'descripcion_control': datos.get('descripcion_control'),
        'tipo_control': datos.get('tipo_control'),
        'frecuencia_ejecucion': datos.get('frecuencia_ejecucion'),
        'grado_manualidad': datos.get('grado_manualidad'),
        'vp_responsable_procedimiento': datos.get('vp_responsable_procedimiento'),
        'direccion_responsable_control': datos.get('direccion_responsable_control'),
        'control_documentado': datos.get('control_documentado', False),
        'control_en_remediacion': datos.get('control_en_remediacion', False),
        'usuario_carga': datos.get('usuario_carga'),
    }
    db.session.execute(query, params)
    db.session.commit()
    return 1


def actualizar_riesgo(riesgo_control_id, datos):
    """Actualiza un riesgo/control existente."""
    query = text("""
        UPDATE riesgos_controles SET
            codigo_riesgo = :codigo_riesgo, descripcion_riesgo = :descripcion_riesgo,
            categoria_riesgo = :categoria_riesgo,
            riesgo_nivel_1 = :riesgo_nivel_1, riesgo_nivel_2 = :riesgo_nivel_2,
            riesgo_nivel_3 = :riesgo_nivel_3,
            macroproceso = :macroproceso, proceso = :proceso,
            factor_riesgo = :factor_riesgo, causa_raiz = :causa_raiz,
            impacto_financiero_dop = :impacto_financiero_dop,
            frecuencia_inherente = :frecuencia_inherente,
            descripcion_control = :descripcion_control,
            tipo_control = :tipo_control,
            frecuencia_ejecucion = :frecuencia_ejecucion,
            grado_manualidad = :grado_manualidad,
            vp_responsable_procedimiento = :vp_responsable_procedimiento,
            direccion_responsable_control = :direccion_responsable_control,
            control_documentado = :control_documentado,
            control_en_remediacion = :control_en_remediacion,
            fecha_modificacion_sistema = CURRENT_TIMESTAMP,
            usuario_modificacion = :usuario_modificacion
        WHERE riesgo_control_id = :riesgo_control_id
    """)
    params = {
        'codigo_riesgo': datos.get('codigo_riesgo'),
        'descripcion_riesgo': datos.get('descripcion_riesgo'),
        'categoria_riesgo': datos.get('categoria_riesgo'),
        'riesgo_nivel_1': datos.get('riesgo_nivel_1'),
        'riesgo_nivel_2': datos.get('riesgo_nivel_2'),
        'riesgo_nivel_3': datos.get('riesgo_nivel_3'),
        'macroproceso': datos.get('macroproceso'),
        'proceso': datos.get('proceso'),
        'factor_riesgo': datos.get('factor_riesgo'),
        'causa_raiz': datos.get('causa_raiz'),
        'impacto_financiero_dop': datos.get('impacto_financiero_dop') or None,
        'frecuencia_inherente': datos.get('frecuencia_inherente'),
        'descripcion_control': datos.get('descripcion_control'),
        'tipo_control': datos.get('tipo_control'),
        'frecuencia_ejecucion': datos.get('frecuencia_ejecucion'),
        'grado_manualidad': datos.get('grado_manualidad'),
        'vp_responsable_procedimiento': datos.get('vp_responsable_procedimiento'),
        'direccion_responsable_control': datos.get('direccion_responsable_control'),
        'control_documentado': datos.get('control_documentado', False),
        'control_en_remediacion': datos.get('control_en_remediacion', False),
        'usuario_modificacion': datos.get('usuario_modificacion'),
        'riesgo_control_id': riesgo_control_id,
    }
    db.session.execute(query, params)
    db.session.commit()
    return 1


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
        'cat_procesos', 'cat_severidad', 'cat_tipo_control', 'cat_tipo_evento_ro02',
        'cat_marcas_tarjetas'
    ]
    if tabla not in tablas_permitidas:
        raise ValueError(f"Tabla de catálogo no permitida: {tabla}")
    query = text(f"SELECT * FROM {tabla} ORDER BY 1")
    result = db.session.execute(query)
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


# ============================================================
# FUNCIONES PARA DASHBOARD / ESTADÍSTICAS
# ============================================================

def get_estadisticas():
    """Obtiene estadísticas generales para el dashboard."""
    stats = {}
    try:
        result = db.session.execute(text("SELECT COUNT(*) as total FROM eventos_riesgo_operacional"))
        stats['total_eventos'] = result.fetchone()[0]
    except Exception:
        stats['total_eventos'] = 0

    try:
        result = db.session.execute(text("SELECT COUNT(*) as total FROM planes_accion"))
        stats['total_planes'] = result.fetchone()[0]
    except Exception:
        stats['total_planes'] = 0

    try:
        result = db.session.execute(text("SELECT COUNT(*) as total FROM riesgos_controles"))
        stats['total_riesgos'] = result.fetchone()[0]
    except Exception:
        stats['total_riesgos'] = 0

    try:
        result = db.session.execute(text(
            "SELECT COUNT(*) as total FROM planes_accion WHERE estatus NOT IN ('Cerrado', 'Completado', 'Completada')"
        ))
        stats['planes_abiertos'] = result.fetchone()[0]
    except Exception:
        stats['planes_abiertos'] = 0

    try:
        result = db.session.execute(text(
            "SELECT COALESCE(SUM(perdida_neta), 0) as total FROM eventos_riesgo_operacional"
        ))
        stats['perdida_total'] = result.fetchone()[0]
    except Exception:
        stats['perdida_total'] = 0

    return stats

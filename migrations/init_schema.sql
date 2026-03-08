-- ============================================================================
-- GIRO - Esquema PostgreSQL
-- Migrado desde Microsoft Fabric SQL Server
-- ============================================================================

-- ============================================================================
-- TABLAS DE CATÁLOGOS (crear primero por dependencias)
-- ============================================================================

CREATE TABLE IF NOT EXISTS cat_tipo_evento_ro02 (
    evento_ro02_id  SERIAL          PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(200)    NOT NULL,
    nivel           INT             NOT NULL,
    codigo_padre    VARCHAR(10),
    activo          BOOLEAN         DEFAULT TRUE,
    fecha_registro  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cat_linea_negocio (
    linea_negocio_id SERIAL         PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(100)    NOT NULL,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_naturaleza_perdida (
    naturaleza_id   INT             PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(100)    NOT NULL,
    descripcion     TEXT,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_areas_organizacion (
    area_id         INT             PRIMARY KEY,
    codigo          VARCHAR(20)     NOT NULL UNIQUE,
    nombre          VARCHAR(150)    NOT NULL,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_procesos (
    proceso_id      SERIAL          PRIMARY KEY,
    codigo          VARCHAR(20)     NOT NULL UNIQUE,
    nombre          VARCHAR(200)    NOT NULL,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_severidad (
    severidad_id    INT             PRIMARY KEY,
    nombre          VARCHAR(20)     NOT NULL UNIQUE,
    valor_numerico  INT             NOT NULL,
    rango_perdida_min DECIMAL(18,2),
    rango_perdida_max DECIMAL(18,2),
    descripcion     TEXT,
    color_hex       VARCHAR(7)
);

CREATE TABLE IF NOT EXISTS cat_probabilidad (
    probabilidad_id INT             PRIMARY KEY,
    nombre          VARCHAR(20)     NOT NULL UNIQUE,
    valor_numerico  INT             NOT NULL,
    frecuencia_esperada VARCHAR(100),
    porcentaje_min  DECIMAL(5,2),
    porcentaje_max  DECIMAL(5,2),
    descripcion     TEXT
);

CREATE TABLE IF NOT EXISTS cat_tipo_control (
    tipo_control_id INT             PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(100)    NOT NULL,
    descripcion     TEXT,
    momento_aplicacion VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS cat_frecuencia_control (
    frecuencia_id   INT             PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL UNIQUE,
    periodicidad_dias INT,
    descripcion     VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS matriz_riesgo (
    matriz_id       SERIAL          PRIMARY KEY,
    probabilidad    INT             NOT NULL,
    impacto         INT             NOT NULL,
    nivel_riesgo    VARCHAR(20)     NOT NULL,
    puntaje_riesgo  INT             NOT NULL,
    color_hex       VARCHAR(7),
    accion_requerida TEXT,
    UNIQUE (probabilidad, impacto)
);

CREATE TABLE IF NOT EXISTS umbrales_materializacion (
    umbral_id       INT             PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL,
    monto_usd       DECIMAL(18,2)   NOT NULL,
    requiere_reporte_super BOOLEAN  DEFAULT FALSE,
    plazo_reporte_dias INT,
    nivel_aprobacion VARCHAR(100),
    descripcion     TEXT
);

CREATE TABLE IF NOT EXISTS cat_estado_evento (
    estado_id       INT             PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL UNIQUE,
    descripcion     TEXT,
    orden           INT,
    color_hex       VARCHAR(7),
    permite_edicion BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_estado_plan_accion (
    estado_id       INT             PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL UNIQUE,
    descripcion     TEXT,
    orden           INT,
    color_hex       VARCHAR(7)
);

CREATE TABLE IF NOT EXISTS cat_canales (
    canal_id        SERIAL          PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(100)    NOT NULL,
    descripcion     TEXT,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_medio_pago (
    medio_pago_id   SERIAL          PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(100)    NOT NULL,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_marcas_tarjetas (
    marca_id        INT             PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(100)    NOT NULL,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_factor_causa (
    factor_id       SERIAL          PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(200)    NOT NULL,
    nivel           INT             NOT NULL,
    codigo_padre    VARCHAR(10),
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_consecuencias (
    consecuencia_id SERIAL          PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(200)    NOT NULL,
    activo          BOOLEAN         DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS cat_incidentes_fraude (
    incidente_id    INT             PRIMARY KEY,
    codigo          VARCHAR(10)     NOT NULL UNIQUE,
    nombre          VARCHAR(200)    NOT NULL,
    activo          BOOLEAN         DEFAULT TRUE
);

-- ============================================================================
-- TABLAS PRINCIPALES
-- ============================================================================

CREATE TABLE IF NOT EXISTS eventos_riesgo_operacional (
    evento_id                   SERIAL          PRIMARY KEY,
    codigo_evento               VARCHAR(50)     NOT NULL UNIQUE,
    descripcion_evento          TEXT,
    descripcion_extendida       TEXT,
    etiquetas                   VARCHAR(500),
    nueva_etiqueta              VARCHAR(100),
    estado_investigacion        VARCHAR(50),
    tipo_registro               VARCHAR(50),
    codigo_riesgo_asociado      VARCHAR(50),
    descripcion_riesgo          TEXT,
    nivel_riesgo_inherente      VARCHAR(20),
    factor_determinante         VARCHAR(100),
    causa_evento                TEXT,
    detalle_causa_raiz          TEXT,
    consecuencia                TEXT,
    tipo_evento                 VARCHAR(100)    NOT NULL,
    categoria_evento            VARCHAR(100),
    subcategoria_evento         VARCHAR(100),
    cantidad_eventos            INT             DEFAULT 1,
    aplica_plan_accion          BOOLEAN         DEFAULT FALSE,
    area_origen                 VARCHAR(100),
    localidad_origen            VARCHAR(100),
    linea_negocios              VARCHAR(100),
    proceso_afectado            VARCHAR(200),
    producto_afectado           VARCHAR(100),
    servicio_afectado           VARCHAR(100),
    canal_distribucion_afectado VARCHAR(100),
    medio_pago                  VARCHAR(50),
    marca_tarjeta               VARCHAR(50),
    fecha_descubrimiento        DATE,
    fecha_inicio_evento         DATE,
    hora_inicio                 TIME,
    fecha_finalizacion_evento   DATE,
    hora_finalizacion           TIME,
    fecha_cierre_evento         DATE,
    anio                        INT,
    mes_evento                  VARCHAR(20),
    tipo_perdida                VARCHAR(50),
    tipo_moneda_ocurrencia      VARCHAR(10)     DEFAULT 'DOP',
    monto_dop                   DECIMAL(18,2)   DEFAULT 0,
    monto_moneda_origen         DECIMAL(18,2),
    cuenta_contable_monto       VARCHAR(50),
    monto_recuperado_seguros    DECIMAL(18,2)   DEFAULT 0,
    monto_recuperado_otros      DECIMAL(18,2)   DEFAULT 0,
    perdida_neta                DECIMAL(18,2)   GENERATED ALWAYS AS (monto_dop - monto_recuperado_seguros - monto_recuperado_otros) STORED,
    estatus_contabilizacion     VARCHAR(50),
    fecha_contabilizacion       DATE,
    fecha_contab_recuperacion   DATE,
    canal_reporte               VARCHAR(50),
    reportado_por               VARCHAR(100),
    nombre_quien_reporta        VARCHAR(150),
    area_gestor_riesgos         VARCHAR(100),
    gestor_riesgos              VARCHAR(100),
    fecha_carga_sistema         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion_sistema  TIMESTAMP,
    usuario_carga               VARCHAR(100),
    archivo_origen              VARCHAR(255),
    CONSTRAINT chk_montos CHECK (
        monto_dop >= 0 AND
        monto_recuperado_seguros >= 0 AND
        monto_recuperado_otros >= 0
    )
);

CREATE TABLE IF NOT EXISTS planes_accion (
    plan_id                     SERIAL          PRIMARY KEY,
    codigo_plan                 VARCHAR(50)     NOT NULL UNIQUE,
    estatus                     VARCHAR(50)     NOT NULL,
    descripcion_causa           TEXT,
    plan_accion                 TEXT,
    prioridad                   VARCHAR(20),
    tipo_plan_accion            VARCHAR(50),
    origen_plan_accion          VARCHAR(100),
    categoria_riesgo            VARCHAR(100),
    vp_responsable              VARCHAR(100),
    direccion_responsable       VARCHAR(100),
    responsable                 VARCHAR(100),
    fecha_creacion_plan         DATE,
    fecha_compromiso_inicial    DATE,
    fecha_compromiso_actual     DATE,
    fecha_cierre                DATE,
    factor_riesgo               VARCHAR(100),
    codigo_riesgo               VARCHAR(50),
    descripcion_riesgo          TEXT,
    codigo_control              VARCHAR(50),
    descripcion_control         TEXT,
    riesgo_residual             VARCHAR(20),
    estatus_apetito             VARCHAR(50),
    codigo_evento               VARCHAR(50)     REFERENCES eventos_riesgo_operacional(codigo_evento) ON UPDATE CASCADE ON DELETE SET NULL,
    procedimiento               VARCHAR(200),
    aprobacion_plan             BOOLEAN         DEFAULT FALSE,
    fecha_carga_sistema         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion_sistema  TIMESTAMP,
    usuario_carga               VARCHAR(100),
    usuario_modificacion        VARCHAR(100),
    numero_actualizaciones      INT             DEFAULT 0
);

CREATE TABLE IF NOT EXISTS riesgos_controles (
    riesgo_control_id                   SERIAL          PRIMARY KEY,
    codigo_riesgo                       VARCHAR(50)     NOT NULL UNIQUE,
    descripcion_riesgo                  TEXT,
    descripcion_extendida_riesgo        TEXT,
    vp_responsable_procedimiento        VARCHAR(100),
    direccion_responsable_procedimiento VARCHAR(100),
    gerencia_responsable_procedimiento  VARCHAR(100),
    categoria_riesgo                    VARCHAR(100),
    macroproceso                        VARCHAR(100),
    proceso                             VARCHAR(200),
    criticidad_proceso                  VARCHAR(20),
    factor_riesgo                       VARCHAR(100),
    causa_raiz                          TEXT,
    riesgo_relacionado                  VARCHAR(50),
    servicio_asociado                   VARCHAR(100),
    producto_asociado                   VARCHAR(100),
    proceso_afectado                    VARCHAR(200),
    riesgo_nivel_1                      VARCHAR(100),
    riesgo_nivel_2                      VARCHAR(100),
    riesgo_nivel_3                      VARCHAR(100),
    estrategia_tratamiento              VARCHAR(100),
    impacto_financiero_dop              DECIMAL(18,2),
    impacto_reputacional                VARCHAR(50),
    impacto_legal_regulatorio           VARCHAR(50),
    frecuencia_inherente                VARCHAR(50),
    nombre_doc_procedimiento            VARCHAR(255),
    descripcion_control                 TEXT,
    descripcion_extendida_control       TEXT,
    evidencia_ejecucion_control         TEXT,
    vp_responsable_control              VARCHAR(100),
    direccion_responsable_control       VARCHAR(100),
    responsable_ejecutar_control        VARCHAR(100),
    posicion_responsable_ejecutar       VARCHAR(100),
    tipo_control                        VARCHAR(50),
    control_documentado                 BOOLEAN         DEFAULT FALSE,
    control_en_remediacion              BOOLEAN         DEFAULT FALSE,
    frecuencia_ejecucion                VARCHAR(50),
    criticidad_control                  VARCHAR(20),
    grado_manualidad                    VARCHAR(50),
    razon_actualizacion_control         TEXT,
    fecha_ultima_autoevaluacion         DATE,
    fecha_ultima_evaluacion             DATE,
    fecha_carga_sistema                 TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion_sistema          TIMESTAMP,
    usuario_carga                       VARCHAR(100),
    usuario_modificacion                VARCHAR(100),
    numero_actualizaciones              INT             DEFAULT 0
);

-- ============================================================================
-- ÍNDICES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_eventos_tipo       ON eventos_riesgo_operacional (tipo_evento);
CREATE INDEX IF NOT EXISTS idx_eventos_estado     ON eventos_riesgo_operacional (estado_investigacion);
CREATE INDEX IF NOT EXISTS idx_eventos_fecha      ON eventos_riesgo_operacional (fecha_inicio_evento);
CREATE INDEX IF NOT EXISTS idx_eventos_area       ON eventos_riesgo_operacional (area_origen);
CREATE INDEX IF NOT EXISTS idx_eventos_linea      ON eventos_riesgo_operacional (linea_negocios);
CREATE INDEX IF NOT EXISTS idx_eventos_perdida    ON eventos_riesgo_operacional (perdida_neta);

CREATE INDEX IF NOT EXISTS idx_planes_evento      ON planes_accion (codigo_evento);
CREATE INDEX IF NOT EXISTS idx_planes_estatus     ON planes_accion (estatus);
CREATE INDEX IF NOT EXISTS idx_planes_responsable ON planes_accion (responsable);
CREATE INDEX IF NOT EXISTS idx_planes_compromiso  ON planes_accion (fecha_compromiso_actual);

CREATE INDEX IF NOT EXISTS idx_riesgos_proceso    ON riesgos_controles (proceso);
CREATE INDEX IF NOT EXISTS idx_riesgos_categoria  ON riesgos_controles (categoria_riesgo);
CREATE INDEX IF NOT EXISTS idx_riesgos_area       ON riesgos_controles (direccion_responsable_procedimiento);

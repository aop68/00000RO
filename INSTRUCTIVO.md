# GIRO - Gestión Integral de Riesgo Operacional

## Instructivo de Instalación y Uso

---

## 1. Descripción General

**GIRO** es una aplicación web desarrollada en Flask (Python) para la gestión integral de riesgo operacional bancario. Se conecta a una base de datos SQL en Microsoft Fabric y permite:

- Gestionar la **Matriz de Eventos de Riesgo** (crear, editar, visualizar)
- Gestionar la **Matriz de Planes de Acción** (crear, editar, visualizar)
- Gestionar la **Matriz de Riesgos y Controles** (crear, editar, visualizar)
- Visualizar **Dashboards de Power BI** embebidos
- Generar **Reportes Regulatorios** para la Superintendencia de Bancos (SIB)
- **Administrar usuarios** y permisos de acceso

---

## 2. Requisitos Previos

### Software necesario:
- **Python 3.10 o superior** - [Descargar](https://www.python.org/downloads/)
- **ODBC Driver 18 for SQL Server** - [Descargar](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
- **Git** (opcional, para control de versiones)

### Acceso requerido:
- Credenciales de acceso a la base de datos en Microsoft Fabric
- URLs de embed de Power BI (para los dashboards)

---

## 3. Instalación

### Paso 1: Copiar la carpeta del proyecto
Copie la carpeta `riesgo_operacional` completa al servidor o equipo donde se ejecutará.

### Paso 2: Crear un entorno virtual
Abra una terminal en la carpeta del proyecto y ejecute:

```bash
cd riesgo_operacional
python -m venv venv
```

### Paso 3: Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Paso 4: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 5: Configurar variables de entorno
Cree un archivo `.env` en la raíz del proyecto (o configure las variables en el sistema):

```env
# Clave secreta (cambiar en producción)
SECRET_KEY=su-clave-secreta-aqui-cambiar-en-produccion

# Conexión a Microsoft Fabric
FABRIC_SERVER=lacarbp7ga2verfegnmkpgjmnpq-kkjie75ctc5u5ct5qutmpwmuzi.database.fabric.microsoft.com,1433
FABRIC_DATABASE=RODB-f2a9be1-7921-48ee-828d-476972b8d27e
FABRIC_AUTH_METHOD=azure_ad

# Si usa autenticación SQL (no Azure AD):
# FABRIC_AUTH_METHOD=sql
# FABRIC_USERNAME=su_usuario
# FABRIC_PASSWORD=su_password

# URLs de Power BI (configurar cuando estén disponibles)
POWERBI_EVENTOS_URL=
POWERBI_PLANES_URL=
POWERBI_RIESGOS_URL=

# Modo de la aplicación
FLASK_CONFIG=production
```

### Paso 6: Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

---

## 4. Primer Acceso

### Credenciales por defecto:
- **Usuario:** `admin`
- **Contraseña:** `admin123`

**IMPORTANTE:** Cambie la contraseña del administrador después del primer inicio de sesión.

### Crear nuevos usuarios:
1. Inicie sesión con la cuenta de administrador
2. Vaya a **Administración > Gestión de Usuarios**
3. Haga clic en **Nuevo Usuario**
4. Complete el formulario y asigne el rol correspondiente

---

## 5. Roles y Permisos

| Rol | Visualizar | Crear/Editar | Gestionar Usuarios |
|-----|:----------:|:------------:|:------------------:|
| **Admin** | Si | Si | Si |
| **Editor** | Si | Si | No |
| **Viewer** | Si | No | No |

---

## 6. Módulos de la Aplicación

### 6.1 Matriz de Eventos de Riesgo
- Registro de eventos de pérdida operacional
- Clasificación según Basel II (7 categorías)
- Registro de montos de pérdida en DOP y USD
- Seguimiento del estado de investigación

### 6.2 Planes de Acción
- Seguimiento de planes de mitigación
- Control de fechas de compromiso
- Seguimiento por prioridad (Alta/Media/Baja)
- Vinculación con riesgos asociados

### 6.3 Riesgos y Controles
- Taxonomía jerárquica de riesgos (3 niveles)
- Asociación de controles (Preventivo/Detectivo/Correctivo)
- Evaluación de grado de manualidad
- Estado de documentación y remediación

### 6.4 Dashboards (Power BI)
- Panel de Eventos de Riesgo
- Panel de Planes de Acción
- Panel de Riesgos y Controles
- *Requiere configurar las URLs de embed*

### 6.5 Reportes Regulatorios (SIB)
Reportes para la Superintendencia de Bancos:
- **RO-01:** Base de Datos de Eventos de Pérdida
- **RO-02:** Autoevaluación de Riesgos y Controles (RCSA)
- **RO-03:** Indicadores Clave de Riesgo (KRI)
- **RO-04:** Planes de Acción y Seguimiento
- **RO-05:** Requerimiento de Capital por Riesgo Operacional
- **RO-06:** Informe de Continuidad de Negocio

*Nota: La generación automática de reportes se implementará progresivamente.*

---

## 7. Despliegue en Producción

### Opción A: Con Gunicorn (Linux)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

### Opción B: Con Waitress (Windows)
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 --call "app:create_app"
```

### Opción C: Con IIS (Windows Server)
1. Instale wfastcgi: `pip install wfastcgi`
2. Configure IIS con FastCGI apuntando al entorno virtual
3. Consulte la documentación de Microsoft para detalles

### Recomendaciones de producción:
- Cambie `SECRET_KEY` a un valor aleatorio seguro
- Configure HTTPS con un certificado SSL
- Use un servidor WSGI como Gunicorn o Waitress
- Configure la base de datos SQLite de usuarios en una ubicación persistente
- Habilite logging a archivo

---

## 8. Estructura del Proyecto

```
riesgo_operacional/
├── app.py                 # Aplicación principal Flask
├── config.py              # Configuración (BD, variables)
├── extensions.py          # Extensiones Flask
├── models.py              # Modelo de usuarios (SQLite)
├── fabric_db.py           # Conexión y queries a Fabric SQL
├── requirements.txt       # Dependencias Python
├── routes/                # Blueprints (rutas)
│   ├── auth.py            # Login / Logout
│   ├── main.py            # Dashboard principal
│   ├── eventos.py         # CRUD Eventos
│   ├── planes.py          # CRUD Planes de Acción
│   ├── riesgos.py         # CRUD Riesgos y Controles
│   ├── powerbi.py         # Paneles Power BI
│   ├── admin.py           # Gestión de usuarios
│   └── reportes.py        # Reportes regulatorios SIB
├── templates/             # Templates HTML (Jinja2)
│   ├── base.html          # Template base con sidebar
│   ├── login.html         # Página de login
│   ├── index.html         # Dashboard principal
│   ├── eventos/           # Templates de eventos
│   ├── planes/            # Templates de planes
│   ├── riesgos/           # Templates de riesgos
│   ├── powerbi/           # Templates de Power BI
│   ├── admin/             # Templates de administración
│   └── reportes/          # Templates de reportes
├── static/                # Archivos estáticos
│   ├── css/style.css      # Estilos personalizados
│   └── js/main.js         # JavaScript personalizado
└── INSTRUCTIVO.md         # Este documento
```

---

## 9. Base de Datos

### Base de datos local (SQLite):
- Archivo: `instance/usuarios.db`
- Contiene: tabla de usuarios del sistema
- Se crea automáticamente al iniciar la aplicación

### Base de datos Fabric (SQL Server):
- Servidor: configurado en `config.py`
- Tablas principales: `eventos_riesgo_operacional`, `planes_accion`, `riesgos_controles`, `matriz_riesgo`
- Catálogos: tablas con prefijo `cat_`
- Framework: Basel II/III, COSO, ISO 31000

---

## 10. Solución de Problemas

### Error de conexión a Fabric
- Verifique que el ODBC Driver 18 esté instalado
- Confirme las credenciales y método de autenticación
- Verifique conectividad de red al servidor

### Error "No module named..."
- Asegúrese de que el entorno virtual esté activado
- Ejecute `pip install -r requirements.txt`

### La aplicación no inicia
- Verifique que Python 3.10+ esté instalado
- Revise los logs en la terminal para errores específicos

---

## 11. Soporte y Mejoras Futuras

Esta aplicación está diseñada para ser extensible. Áreas de mejora planificadas:
- Generación automática de reportes regulatorios (RO-01 a RO-06)
- Exportación de datos a Excel
- Indicadores clave de riesgo (KRI)
- Notificaciones por correo electrónico
- Integración con Active Directory
- Auditoría de cambios

---

*Versión 1.0 | Gestión de Riesgo Operacional*

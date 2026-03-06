"""
Rutas para Reportes Regulatorios (SIB - Superintendencia de Bancos).
Los botones están preparados pero la generación se implementará a futuro.
"""
from flask import Blueprint, render_template, flash
from flask_login import login_required

reportes_bp = Blueprint('reportes', __name__)

# Definición de los reportes regulatorios de Riesgo Operacional
REPORTES_SIB = [
    {
        'codigo': 'RO-01',
        'nombre': 'Base de Datos de Eventos de Pérdida',
        'descripcion': 'Reporte de eventos de pérdida por riesgo operacional registrados en el período.',
        'periodicidad': 'Trimestral',
        'estado': 'pendiente',
        'icono': 'bi-exclamation-triangle'
    },
    {
        'codigo': 'RO-02',
        'nombre': 'Autoevaluación de Riesgos y Controles (RCSA)',
        'descripcion': 'Matriz de autoevaluación de riesgos operacionales y controles asociados.',
        'periodicidad': 'Semestral',
        'estado': 'pendiente',
        'icono': 'bi-shield-check'
    },
    {
        'codigo': 'RO-03',
        'nombre': 'Indicadores Clave de Riesgo (KRI)',
        'descripcion': 'Reporte de indicadores clave de riesgo operacional y sus umbrales.',
        'periodicidad': 'Trimestral',
        'estado': 'pendiente',
        'icono': 'bi-speedometer2'
    },
    {
        'codigo': 'RO-04',
        'nombre': 'Planes de Acción y Seguimiento',
        'descripcion': 'Estado de los planes de acción de mitigación de riesgo operacional.',
        'periodicidad': 'Trimestral',
        'estado': 'pendiente',
        'icono': 'bi-list-check'
    },
    {
        'codigo': 'RO-05',
        'nombre': 'Requerimiento de Capital por Riesgo Operacional',
        'descripcion': 'Cálculo del capital regulatorio requerido por riesgo operacional.',
        'periodicidad': 'Trimestral',
        'estado': 'pendiente',
        'icono': 'bi-bank'
    },
    {
        'codigo': 'RO-06',
        'nombre': 'Informe de Continuidad de Negocio',
        'descripcion': 'Estado del plan de continuidad del negocio y pruebas realizadas.',
        'periodicidad': 'Anual',
        'estado': 'pendiente',
        'icono': 'bi-arrow-repeat'
    },
]


@reportes_bp.route('/')
@login_required
def index():
    return render_template('reportes/index.html', reportes=REPORTES_SIB)


@reportes_bp.route('/generar/<codigo>')
@login_required
def generar(codigo):
    reporte = next((r for r in REPORTES_SIB if r['codigo'] == codigo), None)
    if not reporte:
        flash('Reporte no encontrado.', 'warning')
    else:
        flash(
            f'La generación del reporte {codigo} - {reporte["nombre"]} '
            f'estará disponible próximamente.',
            'info'
        )
    return render_template('reportes/index.html', reportes=REPORTES_SIB)

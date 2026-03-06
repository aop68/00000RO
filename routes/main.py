"""
Ruta principal: dashboard / página de inicio.
"""
from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    stats = {}
    error_conexion = False
    try:
        from fabric_db import get_estadisticas
        stats = get_estadisticas()
    except Exception as e:
        error_conexion = True
        stats = {
            'total_eventos': '-',
            'total_planes': '-',
            'total_riesgos': '-',
            'planes_abiertos': '-',
            'perdida_total': '-'
        }
    return render_template('index.html', stats=stats, error_conexion=error_conexion)

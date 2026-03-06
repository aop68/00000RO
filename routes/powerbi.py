"""
Rutas para paneles embebidos de Power BI.
"""
from flask import Blueprint, render_template, current_app
from flask_login import login_required

powerbi_bp = Blueprint('powerbi', __name__)


@powerbi_bp.route('/eventos')
@login_required
def eventos():
    url = current_app.config.get('POWERBI_EVENTOS_URL', '')
    return render_template('powerbi/panel.html',
                           titulo='Dashboard de Eventos',
                           embed_url=url,
                           seccion='eventos')


@powerbi_bp.route('/planes')
@login_required
def planes():
    url = current_app.config.get('POWERBI_PLANES_URL', '')
    return render_template('powerbi/panel.html',
                           titulo='Dashboard de Planes de Acción',
                           embed_url=url,
                           seccion='planes')


@powerbi_bp.route('/riesgos')
@login_required
def riesgos():
    url = current_app.config.get('POWERBI_RIESGOS_URL', '')
    return render_template('powerbi/panel.html',
                           titulo='Dashboard de Riesgos y Controles',
                           embed_url=url,
                           seccion='riesgos')

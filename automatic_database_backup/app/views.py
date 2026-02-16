from flask import Blueprint, render_template, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({
        'service': 'Automatic Database Backup',
        'version': '1.0.0',
        'status': 'running'
    })

@main_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'database': 'connected'  # TODO: добавить проверку БД
    })

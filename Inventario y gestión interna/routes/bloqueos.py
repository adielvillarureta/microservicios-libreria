from flask import Blueprint, jsonify

bloqueos_bp = Blueprint('bloqueos', __name__)


@bloqueos_bp.route('/bloqueos', methods=['GET'])
@bloqueos_bp.route('/api/bloqueos', methods=['GET'])
def listar_bloqueos():
    return jsonify([])
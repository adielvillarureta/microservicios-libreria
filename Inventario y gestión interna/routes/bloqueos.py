from flask import Blueprint, jsonify
from models.usuarioSistema import UsuarioSistema

bloqueos_bp = Blueprint('bloqueos', __name__)

@bloqueos_bp.route('/bloqueos', methods=['GET'])
def listar_bloqueos():
    # Aquí puedes implementar la lógica real de bloqueos
    # Por ahora devolvemos una lista vacía
    return jsonify([])
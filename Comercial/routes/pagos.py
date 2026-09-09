from flask import Blueprint, request, jsonify
from app import db
from models.pedido import Pedido

pagos_bp = Blueprint('pagos', __name__)

@pagos_bp.route('/api/pagos/procesar', methods=['POST'])
def procesar_pago():
    data = request.get_json()
    pedido_id = data.get('pedido_id')
    metodo_pago = data.get('metodo_pago')
    
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        return jsonify({'success': False, 'error': 'Pedido no encontrado'})
    
    pedido.estado = 'confirmado'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Pago procesado correctamente'})
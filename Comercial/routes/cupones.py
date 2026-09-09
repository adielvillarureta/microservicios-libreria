from flask import Blueprint, request, jsonify
from app import db
from models.cupon import Cupon
from datetime import datetime

cupones_bp = Blueprint('cupones', __name__)

@cupones_bp.route('/api/cupones/validar', methods=['POST'])
def validar_cupon():
    data = request.get_json()
    codigo = data.get('codigo', '').upper()
    total = data.get('total', 0)
    
    cupon = Cupon.query.filter_by(codigo=codigo, activo=True).first()
    
    if not cupon:
        return jsonify({'success': False, 'error': 'Cupón no válido'})
    
    if cupon.fecha_expiracion and cupon.fecha_expiracion < datetime.utcnow():
        return jsonify({'success': False, 'error': 'Cupón expirado'})
    
    if cupon.usos_actuales >= cupon.usos_maximos:
        return jsonify({'success': False, 'error': 'Cupón agotado'})
    
    if total < cupon.minimo_compra:
        return jsonify({'success': False, 'error': f'Compra mínima de S/ {cupon.minimo_compra}'})
    
    if cupon.tipo == 'porcentaje':
        descuento = total * (cupon.valor / 100)
    elif cupon.tipo == 'fijo':
        descuento = cupon.valor
    else:
        descuento = 0
    
    cupon.usos_actuales += 1
    db.session.commit()
    
    return jsonify({'success': True, 'descuento': descuento})
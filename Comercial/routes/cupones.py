from flask import Blueprint, flash, redirect, render_template, request, jsonify
from extensions import db
from models.cupones import Cupon
from datetime import datetime

cupones_bp = Blueprint('cupones', __name__)


@cupones_bp.route('/cupones')
def listar_cupones():
    cupones = Cupon.query.order_by(Cupon.fecha_creacion.desc()).all()
    return render_template('cupones.html', cupones=cupones)


@cupones_bp.route('/cupon/nuevo', methods=['GET', 'POST'])
def nuevo_cupon():
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').upper().strip()
        tipo = request.form.get('tipo', 'porcentaje')
        try:
            valor = float(request.form.get('valor', 0))
            minimo = float(request.form.get('minimo_compra', 0))
            usos_maximos = int(request.form.get('usos_maximos', 100))
        except ValueError:
            flash('Valores numéricos inválidos', 'danger')
            return render_template('cupon_nuevo.html')

        if not codigo:
            flash('El código del cupón es obligatorio', 'danger')
            return render_template('cupon_nuevo.html')

        if Cupon.query.filter_by(codigo=codigo).first():
            flash('Ya existe un cupón con ese código', 'danger')
            return render_template('cupon_nuevo.html')

        fecha_exp = request.form.get('fecha_expiracion')
        activo = request.form.get('activo') == 'on'
        cupon = Cupon(
            codigo=codigo,
            tipo=tipo,
            valor=valor,
            minimo_compra=minimo,
            usos_maximos=usos_maximos,
            activo=activo
        )
        if fecha_exp:
            try:
                cupon.fecha_expiracion = datetime.strptime(fecha_exp, '%Y-%m-%d')
            except ValueError:
                cupon.fecha_expiracion = None
        db.session.add(cupon)
        db.session.commit()
        flash(f'Cupón {codigo} creado correctamente', 'success')
        return redirect('/cupones')

    return render_template('cupon_nuevo.html')


@cupones_bp.route('/cupon/eliminar/<int:cupon_id>')
def eliminar_cupon(cupon_id):
    cupon = Cupon.query.get_or_404(cupon_id)
    codigo = cupon.codigo
    db.session.delete(cupon)
    db.session.commit()
    flash(f'Cupón {codigo} eliminado', 'success')
    return redirect('/cupones')


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
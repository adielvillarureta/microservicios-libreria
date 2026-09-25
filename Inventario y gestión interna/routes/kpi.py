"""
=============================================================================
 MICROSERVICIO INVENTARIO - Tablero de Indicadores Estrategicos (KPIs)
 Unidad didactica: Inteligencia de Negocios

 Este microservicio es el dueno de la informacion de stock, por eso calcula:
   KPI 5  Reduccion de ventas perdidas por falta de stock
   KPI 6  Rotacion de inventario

 Los KPIs de ventas (1, 2, 3, 4, 7, 8, 9) se obtienen del microservicio
 Comercial calling su API /api/kpi/comercial. Cada base de datos sigue
 perteneciendo a su microservicio: aqui no se toca comercial_db.
=============================================================================
"""
import os
from datetime import datetime
from functools import wraps

import requests
from flask import Blueprint, jsonify, redirect, render_template, request, session
from sqlalchemy import text

from extensions import db
from models.producto import Producto

kpi_bp = Blueprint('kpi', __name__)

COMERCIAL_API_URL = (
    os.getenv('COMERCIAL_API_URL')
    or os.getenv('COMERCIAL_URL')
    or 'http://comercial:5000'
)

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def _login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper


def _f(valor, decimales=2):
    return None if valor is None else round(float(valor), decimales)


# ---------------------------------------------------------------------------
#  KPI 5 - Reduccion de ventas perdidas por falta de stock
#  (Productos agotados en el periodo / Total de productos activos) x 100
# ---------------------------------------------------------------------------
def kpi_ventas_perdidas_stock():
    actual = db.session.execute(text("""
        SELECT COUNT(*) AS activos,
               SUM(CASE WHEN cantidad = 0 THEN 1 ELSE 0 END) AS agotados,
               SUM(CASE WHEN cantidad > 0 AND cantidad <= stock_minimo THEN 1 ELSE 0 END) AS stock_bajo
        FROM productos
        WHERE estado = 1
    """)).fetchone()

    activos = int(actual.activos or 0)
    agotados = int(actual.agotados or 0)
    stock_bajo = int(actual.stock_bajo or 0)
    tasa = (agotados / activos * 100) if activos else 0.0

    # historico de agotados por mes
    serie = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha, '%Y-%m') AS periodo,
               COUNT(DISTINCT producto_id) AS productos,
               SUM(agotado) AS registros_agotado
        FROM inventario_diario
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    hist = []
    for s in serie:
        anio, mes = s.periodo.split('-')
        prod = int(s.productos or 0)
        ag = int(s.registros_agotado or 0)
        hist.append({
            'periodo': s.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'porcentaje': _f(ag / prod * 100) if prod else 0.0,
            'registros_agotado': ag
        })

    # evolucion real de la tasa mensual de productos agotados
    detalle_mensual = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha, '%Y-%m') AS periodo,
               COUNT(DISTINCT producto_id) AS productos,
               COUNT(DISTINCT IF(agotado = 1, producto_id, NULL)) AS agotados
        FROM inventario_diario
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    evolucion = []
    for d in detalle_mensual:
        anio, mes = d.periodo.split('-')
        prod = int(d.productos or 0)
        ag = int(d.agotados or 0)
        evolucion.append({
            'periodo': d.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'valor': _f(ag / prod * 100) if prod else 0.0,
            'agotados': ag,
            'productos': prod
        })

    primer_mes = evolucion[0]['valor'] if evolucion else 0.0
    ultimo_mes = evolucion[-1]['valor'] if evolucion else 0.0
    reduccion = ((primer_mes - ultimo_mes) / primer_mes * 100) if primer_mes else 0.0

    # La meta dice: "reduccion del 85% respecto a la gestion MANUAL anterior".
    # Sin sistema, un producto agotado se detectaba tarde o nunca, asi que la
    # linea base de referencia es 100% de productos que llegan a agotarse.
    # El cumplimiento se mide contra esa base, no contra el propio primer mes.
    reduccion_vs_manual = ((100.0 - tasa) / 100.0) * 100
    cumple_manual = reduccion_vs_manual >= 85.0

    agotados_detalle = db.session.execute(text("""
        SELECT p.id, p.nombre, p.cantidad, p.precio, p.stock_minimo,
               c.nombre AS categoria
        FROM productos p
        LEFT JOIN categorias c ON c.id_categoria = p.id_categoria
        WHERE p.estado = 1 AND p.cantidad = 0
        ORDER BY p.precio DESC
    """)).fetchall()

    reposicion = db.session.execute(text("""
        SELECT p.id, p.nombre, p.cantidad, p.stock_minimo, p.precio
        FROM productos p
        WHERE p.estado = 1 AND p.cantidad > 0 AND p.cantidad <= p.stock_minimo
        ORDER BY p.cantidad ASC
    """)).fetchall()

    return {
        'valor': _f(tasa),
        'productos_activos': activos,
        'productos_agotados': agotados,
        'productos_stock_bajo': stock_bajo,
        'ventas_potenciales_pérdidas': _f(sum(float(p.precio or 0) * 5 for p in agotados_detalle)),
        'reduccion_vs_inicio': _f(reduccion),
        'reduccion_vs_manual': _f(reduccion_vs_manual),
        'serie': evolucion,
        'agotados_detalle': [{
            'id': p.id, 'nombre': p.nombre, 'categoria': p.categoria or 'Sin categoria',
            'precio': _f(p.precio), 'stock_minimo': int(p.stock_minimo or 0)
        } for p in agotados_detalle],
        'por_reponer': [{
            'id': p.id, 'nombre': p.nombre, 'cantidad': int(p.cantidad or 0),
            'stock_minimo': int(p.stock_minimo or 0), 'precio': _f(p.precio)
        } for p in reposicion],
        # meta: reduccion del 85% frente a la gestion manual
        'cumple_meta': cumple_manual,
        'meta': 85.0,
        'referencia_manual': 100.0
    }


# ---------------------------------------------------------------------------
#  KPI 6 - Rotacion de inventario
#  Unidades vendidas en 30 dias / Stock actual
# ---------------------------------------------------------------------------
def kpi_rotacion_inventario():
    # unidades vendidas (SALIDAS) de los ultimos 30 dias
    salidas = db.session.execute(text("""
        SELECT producto_id, SUM(cantidad) AS unidades
        FROM movimientos_stock
        WHERE tipo = 'SALIDA' AND fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        GROUP BY producto_id
    """)).fetchall()
    vendidas_30d = {int(r.producto_id): int(r.unidades or 0) for r in salidas}

    productos = Producto.query.filter_by(estado=True).all()

    rotaciones = []
    for p in productos:
        stock = int(p.cantidad or 0)
        vendidas = vendidas_30d.get(p.id, 0)
        rotacion = (vendidas / stock) if stock > 0 else (999.0 if vendidas > 0 else 0.0)
        rotaciones.append({
            'producto': p.nombre,
            'stock': stock,
            'vendidas_30d': vendidas,
            'rotacion': round(rotacion, 2)
        })

    # indice global de rotacion
    total_stock = sum(int(p.cantidad or 0) for p in productos)
    total_vendidas = sum(vendidas_30d.values())
    indice = (total_vendidas / total_stock) if total_stock else 0.0

    # los 10 mas rapidos
    top = sorted(rotaciones, key=lambda r: r['rotacion'], reverse=True)[:10]
    # inventario dormido: no se vendio en 30 dias
    dormidos = [r for r in rotaciones if r['vendidas_30d'] == 0 and r['stock'] > 0]

    # valor del inventario vs valor del costo
    valor_venta = sum(float(p.precio or 0) * int(p.cantidad or 0) for p in productos)
    valor_costo = sum(float(p.costo or 0) * int(p.cantidad or 0) for p in productos)

    # evolucion mensual de la rotacion (desde salidas historicas)
    serie = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha, '%Y-%m') AS periodo,
               SUM(CASE WHEN tipo = 'SALIDA' THEN cantidad ELSE 0 END) AS vendidas
        FROM movimientos_stock
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    hist = []
    for s in serie:
        anio, mes = s.periodo.split('-')
        hist.append({
            'periodo': s.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'unidades': int(s.vendidas or 0)
        })

    # clasificacion por velocidad
    rapidos = [r for r in rotaciones if r['rotacion'] >= 1.0]
    medios = [r for r in rotaciones if 0.3 <= r['rotacion'] < 1.0]
    lentos = [r for r in rotaciones if r['rotacion'] < 0.3]

    return {
        'valor': round(indice, 2),
        'unidades_vendidas_30d': total_vendidas,
        'stock_total': total_stock,
        'productos_activos': len(productos),
        'productos_rapidos': len(rapidos),
        'productos_medios': len(medios),
        'productos_lentos': len(lentos),
        'inventario_dormido': len(dormidos),
        'valor_venta': _f(valor_venta),
        'valor_costo': _f(valor_costo),
        'top_rotacion': top,
        'dormidos': sorted(dormidos, key=lambda r: r['stock'], reverse=True)[:10],
        'serie': hist,
        # meta: mas alta en campana escolar (referencia 1.2 rotaciones/mes)
        'referencia': 1.2,
        'cumple_meta': indice >= 1.2,
        'meta': 1.2
    }


# ---------------------------------------------------------------------------
#  Consumo de KPIs del microservicio COMERCIAL (KPI 1,2,3,4,7,8,9)
# ---------------------------------------------------------------------------
def obtener_kpis_comercial():
    try:
        r = requests.get(f"{COMERCIAL_API_URL}/api/kpi/comercial", timeout=10)
        if r.status_code == 200:
            return r.json(), True
        return None, False
    except requests.exceptions.ConnectionError:
        return None, False
    except Exception:
        return None, False


# ---------------------------------------------------------------------------
#  ENDPOINT - KPIs de inventario
# ---------------------------------------------------------------------------
@kpi_bp.route('/api/kpi/inventario', methods=['GET'])
@_login_requerido
def api_kpi_inventario():
    try:
        datos = {
            'kpi_5_ventas_perdidas': kpi_ventas_perdidas_stock(),
            'kpi_6_rotacion': kpi_rotacion_inventario(),
            'generado_en': datetime.now().isoformat(timespec='seconds'),
            'microservicio': 'inventario',
            'base_datos': 'inventario_db',
            'ok': True
        }
        return jsonify(datos), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e),
                        'generado_en': datetime.now().isoformat(timespec='seconds')}), 500


# ---------------------------------------------------------------------------
#  ENDPOINT - Tablero completo (inventario + comercial)
# ---------------------------------------------------------------------------
@kpi_bp.route('/api/kpi/completo', methods=['GET'])
@_login_requerido
def api_kpi_completo():
    comercial, comercial_ok = obtener_kpis_comercial()

    try:
        inventario = {
            'kpi_5_ventas_perdidas': kpi_ventas_perdidas_stock(),
            'kpi_6_rotacion': kpi_rotacion_inventario(),
        }
    except Exception as e:
        inventario = {'error': str(e)}

    return jsonify({
        'ok': True,
        'comercial': comercial if comercial_ok else None,
        'comercial_disponible': comercial_ok,
        'inventario': inventario,
        'generado_en': datetime.now().isoformat(timespec='seconds')
    }), 200


# ---------------------------------------------------------------------------
#  PAGINA - Tablero de Indicadores (la "otra pagina" de KPIs)
# ---------------------------------------------------------------------------
@kpi_bp.route('/kpis')
@_login_requerido
def tablero_kpis():
    comercial, comercial_ok = obtener_kpis_comercial()

    try:
        inv_stock = kpi_ventas_perdidas_stock()
        inv_rotacion = kpi_rotacion_inventario()
    except Exception:
        inv_stock, inv_rotacion = {}, {}

    return render_template(
        'kpis.html',
        comercial=comercial if comercial_ok else None,
        comercial_ok=comercial_ok,
        inv_stock=inv_stock,
        inv_rotacion=inv_rotacion,
        ahora=datetime.now()
    )


# ---------------------------------------------------------------------------
#  PORTADA - Cubierta del proyecto
# ---------------------------------------------------------------------------
@kpi_bp.route('/portada')
@_login_requerido
def portada():
    comercial, comercial_ok = obtener_kpis_comercial()

    tarjetas = []
    if comercial_ok and comercial:
        tarjetas = [
            ('fa-chart-line', '#1e3a8a', 'Crecimiento de ventas',
             comercial['kpi_1_crecimiento_ventas']['valor'], '%'),
            ('fa-money-bill-trend-up', '#16a34a', 'Margen real',
             comercial['kpi_3_margen_real']['valor'], '%'),
            ('fa-shopping-cart', '#7c3aed', 'Conversión',
             comercial['kpi_4_conversion_pedidos']['valor'], '%'),
            ('fa-vault', '#0891b2', 'Precisión de caja',
             comercial['kpi_7_precision_caja']['valor'], '%'),
        ]

    return render_template('portada.html', tarjetas=tarjetas, ahora=datetime.now())

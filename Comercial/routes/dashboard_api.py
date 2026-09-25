"""
=============================================================================
 MICROSERVICIO COMERCIAL - Resumen para el panel de Inventario
 Unidad didactica: Inteligencia de Negocios

 El microservicio de Inventario no tiene acceso a comercial_db (cada base
 pertenece a su microservicio). Este endpoint le entrega ya calculados los
 indicadores de ventas, pedidos y clientes que el panel de Inventario
 necesita para mostrar informacion real y no ceros.
=============================================================================
"""
from datetime import datetime

from flask import Blueprint, jsonify
from sqlalchemy import text

from extensions import db

dashboard_bp = Blueprint('dashboard_api', __name__)

MESES_CORTOS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

AZUL = '#1e3a8a'
VERDE = '#10b981'
ROJO = '#dc3545'
VIOLETA = '#8b5cf6'


@dashboard_bp.route('/api/dashboard/resumen', methods=['GET'])
def api_resumen_dashboard():
    try:
        hoy = db.session.execute(text("""
            SELECT COALESCE(SUM(total_venta),0) AS total, COUNT(*) AS n
            FROM ventas
            WHERE estado = 1 AND DATE(fecha_venta) = CURDATE()
        """)).fetchone()

        mes = db.session.execute(text("""
            SELECT COALESCE(SUM(total_venta),0) AS total, COUNT(*) AS n
            FROM ventas
            WHERE estado = 1 AND fecha_venta >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
        """)).fetchone()

        pedidos = db.session.execute(text("""
            SELECT SUM(CASE WHEN estado = 'pendiente' THEN 1 ELSE 0 END) AS pendientes,
                   SUM(CASE WHEN estado IN ('confirmado','preparando','enviado','listo_tienda')
                            THEN 1 ELSE 0 END) AS en_proceso
            FROM pedidos
        """)).fetchone()

        clientes = db.session.execute(text("""
            SELECT COUNT(*) AS total,
                   SUM(CASE WHEN fecha_registro >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                            THEN 1 ELSE 0 END) AS nuevos_30d
            FROM clientes
        """)).fetchone()

        # --- serie de ventas por mes ---
        ventas_mes = db.session.execute(text("""
            SELECT DATE_FORMAT(fecha_venta, '%Y-%m') AS periodo,
                   COUNT(*) AS n,
                   COALESCE(SUM(total_venta),0) AS total
            FROM ventas WHERE estado = 1
            GROUP BY periodo ORDER BY periodo
        """)).fetchall()

        etiquetas, valores, transacciones = [], [], []
        for v in ventas_mes:
            anio, mes_num = v.periodo.split('-')
            etiquetas.append(f"{MESES_CORTOS[int(mes_num) - 1]} {anio[2:]}")
            valores.append(round(float(v.total or 0), 2))
            transacciones.append(int(v.n))

        graph_ventas = {
            "data": [{
                "type": "bar",
                "name": "Ventas (S/)",
                "x": etiquetas,
                "y": valores,
                "marker": {"color": AZUL}
            }, {
                "type": "scatter",
                "name": "Transacciones",
                "x": etiquetas,
                "y": transacciones,
                "mode": "lines+markers",
                "line": {"color": VERDE, "width": 2, "dash": "dot"},
                "yaxis": "y2"
            }],
            "layout": {
                "title": {"text": "Evolucion de ventas por mes", "font": {"size": 15}},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"family": "Inter, sans-serif"},
                "barmode": "group",
                "margin": {"t": 55, "b": 35, "l": 55, "r": 50},
                "legend": {"orientation": "h", "y": 1.12},
                "xaxis": {"tickangle": -30},
                "yaxis": {"title": "S/", "side": "left"},
                "yaxis2": {
                    "title": "Transacciones", "side": "right",
                    "overlaying": "y", "showgrid": False
                }
            }
        }

        # --- top productos (se cruza con inventario por producto_id) ---
        top = db.session.execute(text("""
            SELECT d.nombre_producto, SUM(d.cantidad) AS unidades,
                   SUM(d.subtotal) AS ingresos
            FROM detalle_ventas d
            JOIN ventas v ON v.id = d.venta_id
            WHERE v.estado = 1
            GROUP BY nombre_producto
            ORDER BY ingresos DESC
            LIMIT 8
        """)).fetchall()

        top_productos = [{
            'nombre': t.nombre_producto,
            'total_vendido': int(t.unidades),
            'ingresos': round(float(t.ingresos or 0), 2)
        } for t in top]

        graph_top = {
            "data": [{
                "type": "bar",
                "orientation": "h",
                "name": "Unidades",
                "y": [t['nombre'][:26] for t in reversed(top_productos)],
                "x": [t['total_vendido'] for t in reversed(top_productos)],
                "marker": {"color": VERDE}
            }],
            "layout": {
                "title": {"text": "Top productos por unidades", "font": {"size": 15}},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"family": "Inter, sans-serif", "size": 11},
                "margin": {"t": 50, "b": 25, "l": 150, "r": 20}
            }
        }

        # --- ventas por metodo de pago (categoria equivalente) ---
        metodos = db.session.execute(text("""
            SELECT COALESCE(metodo_pago,'Sin metodo') AS metodo,
                   COALESCE(SUM(total_venta),0) AS total
            FROM ventas WHERE estado = 1
            GROUP BY metodo ORDER BY total DESC
        """)).fetchall()

        colores = [AZUL, VERDE, VIOLETA, '#f59e0b', '#06b6d4']
        graph_cat = {
            "data": [{
                "type": "pie",
                "name": "Metodo de pago",
                "labels": [m.metodo for m in metodos],
                "values": [round(float(m.total or 0), 2) for m in metodos],
                "marker": {"colors": colores},
                "textinfo": "label+percent",
                "hoverinfo": "label+value+percent"
            }],
            "layout": {
                "title": {"text": "Ventas por metodo de pago", "font": {"size": 15}},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "font": {"family": "Inter, sans-serif"},
                "legend": {"orientation": "h", "y": -0.15},
                "margin": {"t": 50, "b": 70, "l": 30, "r": 30}
            }
        }

        # --- estado de pedidos ---
        estados = db.session.execute(text("""
            SELECT estado, COUNT(*) AS n FROM pedidos
            GROUP BY estado ORDER BY n DESC
        """)).fetchall()

        paleta = ['#f59e0b', AZUL, VIOLETA, '#06b6d4', VERDE, ROJO, '#94a3b8', '#ec4899']
        graph_estados = {
            "data": [{
                "type": "bar",
                "name": "Pedidos",
                "x": [e.estado for e in estados],
                "y": [int(e.n) for e in estados],
                "marker": {"color": paleta[:len(estados)]}
            }],
            "layout": {
                "title": {"text": "Pedidos por estado", "font": {"size": 15}},
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "font": {"family": "Inter, sans-serif"},
                "margin": {"t": 50, "b": 60, "l": 45, "r": 20},
                "xaxis": {"tickangle": -25}
            }
        }

        return jsonify({
            'ok': True,
            'comercial_ok': True,
            'ventas_hoy': round(float(hoy.total or 0), 2),
            'n_ventas_hoy': int(hoy.n or 0),
            'ventas_mes': round(float(mes.total or 0), 2),
            'n_ventas_mes': int(mes.n or 0),
            'pedidos_pendientes': int(pedidos.pendientes or 0),
            'pedidos_proceso': int(pedidos.en_proceso or 0),
            'clientes': int(clientes.total or 0),
            'clientes_nuevos': int(clientes.nuevos_30d or 0),
            'top_productos': top_productos,
            'graph_ventas': graph_ventas,
            'graph_top': graph_top,
            'graph_cat': graph_cat,
            'graph_estados': graph_estados,
            'generado_en': datetime.now().isoformat(timespec='seconds')
        }), 200

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

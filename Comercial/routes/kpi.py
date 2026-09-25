"""
=============================================================================
 MICROSERVICIO COMERCIAL - API de Indicadores Estrategicos (KPIs)
 Unidad didactica: Inteligencia de Negocios

 Devuelve los KPIs que se calculan con datos de comercial_db:
   KPI 1  Crecimiento de ventas mensual
   KPI 2  Ticket promedio por cliente
   KPI 3  Margen de ganancia real
   KPI 4  Tasa de conversion de pedido a venta
   KPI 7  Precision en el cierre de caja
   KPI 8  Crecimiento de la base de clientes
   KPI 9  Tiempo de atencion al cliente

 Los KPIs 5 (ventas perdidas por falta de stock) y 6 (rotacion) los calcula
 el microservicio de Inventario, que es dueno de la informacion de stock.
=============================================================================
"""
from datetime import datetime, date, timedelta
from decimal import Decimal

from flask import Blueprint, jsonify
from sqlalchemy import text

from extensions import db

kpi_bp = Blueprint('kpi', __name__)

MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
         'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']


def _f(valor, decimales=2):
    if valor is None:
        return None
    return round(float(valor), decimales)


# ---------------------------------------------------------------------------
#  KPI 1 - Crecimiento de ventas mensual
#  ((Ventas mes actual - Ventas mes anterior) / Ventas mes anterior) x 100
# ---------------------------------------------------------------------------
def kpi_crecimiento_ventas():
    filas = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha_venta, '%Y-%m') AS periodo,
               COUNT(*)          AS num_ventas,
               SUM(total_venta)  AS total
        FROM ventas
        WHERE estado = 1
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    serie = []
    for f in filas:
        anio, mes = f.periodo.split('-')
        serie.append({
            'periodo': f.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'anio': int(anio),
            'mes': int(mes),
            'num_ventas': int(f.num_ventas),
            'total': _f(f.total)
        })

    if len(serie) < 2:
        return {'valor': None, 'serie': serie, 'mes_actual': None, 'mes_anterior': None,
                'cumple_meta': None, 'meta': 10.0}

    actual, anterior = serie[-1], serie[-2]

    # El mes en curso suele estar incompleto (hoy es dia X). Comparar un mes
    # parcial contra un mes completo daria una caida artificial, asi que se
    # compara "mes a mes" con el MISMO numero de dias transcurridos.
    dia_hoy = datetime.now().day
    actual_acotado = float(db.session.execute(text("""
        SELECT COALESCE(SUM(total_venta),0) FROM ventas
        WHERE estado = 1
          AND fecha_venta >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
          AND fecha_venta <  DATE_ADD(
                DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL :dias DAY)
    """), {'dias': dia_hoy}).scalar() or 0)

    anterior_acotado = float(db.session.execute(text("""
        SELECT COALESCE(SUM(total_venta),0) FROM ventas
        WHERE estado = 1
          AND fecha_venta >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
          AND fecha_venta <  DATE_ADD(
                DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01'),
                INTERVAL :dias DAY)
    """), {'dias': dia_hoy}).scalar() or 0)

    mes_actual_completo = serie[-1]['etiqueta'] != f"{MESES[datetime.now().month - 1][:3]} {str(datetime.now().year)[2:]}"

    base_actual = actual_acotado if not mes_actual_completo else actual['total']
    base_anterior = anterior_acotado if not mes_actual_completo else anterior['total']

    if base_anterior:
        crecimiento = ((base_actual - base_anterior) / base_anterior) * 100
    else:
        crecimiento = 0.0

    return {
        'valor': _f(crecimiento),
        'serie': serie,
        'mes_actual': dict(actual, total=_f(base_actual), dia_corte=dia_hoy),
        'mes_anterior': dict(anterior, total=_f(base_anterior), dia_corte=dia_hoy),
        'comparacion': 'mes a mes mismo dia' if not mes_actual_completo else 'mes completo',
        'cumple_meta': crecimiento >= 10.0,
        'meta': 10.0
    }


# ---------------------------------------------------------------------------
#  KPI 2 - Ticket promedio por cliente
#  Total vendido en el periodo / Numero de ventas del mismo periodo
# ---------------------------------------------------------------------------
def kpi_ticket_promedio():
    # Mismo criterio que el KPI 1: si el mes en curso esta incompleto, se
    # compara contra el mismo numero de dias del mes anterior.
    dia_hoy = datetime.now().day
    actual = db.session.execute(text("""
        SELECT COALESCE(SUM(total_venta),0) AS total, COUNT(*) AS n
        FROM ventas
        WHERE estado = 1
          AND fecha_venta >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
          AND fecha_venta <  DATE_ADD(
                DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL :dias DAY)
    """), {'dias': dia_hoy}).fetchone()

    anterior = db.session.execute(text("""
        SELECT COALESCE(SUM(total_venta),0) AS total, COUNT(*) AS n
        FROM ventas
        WHERE estado = 1
          AND fecha_venta >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
          AND fecha_venta <  DATE_ADD(
                DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01'),
                INTERVAL :dias DAY)
    """), {'dias': dia_hoy}).fetchone()

    serie = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha_venta, '%Y-%m') AS periodo,
               COUNT(*) AS n,
               COALESCE(SUM(total_venta),0) AS total
        FROM ventas
        WHERE estado = 1
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    historial = []
    for f in serie:
        anio, mes = f.periodo.split('-')
        historial.append({
            'periodo': f.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'ticket': _f(f.total / f.n) if f.n else 0.0,
            'ventas': int(f.n)
        })

    ticket_actual = _f(actual.total / actual.n) if actual.n else 0.0
    ticket_anterior = _f(anterior.total / anterior.n) if anterior.n else 0.0

    # La meta dice "aumento del 15% RESPECTO AL PROMEDIO ANTES DEL SISTEMA".
    # La linea base NO es el mes anterior: es el primer mes de datos, que se
    # toma como periodo de control (gestion manual anterior al sistema).
    ticket_base = historial[0]['ticket'] if historial else 0.0
    variacion = ((ticket_actual - ticket_base) / ticket_base * 100) if ticket_base else 0.0
    var_mom = ((ticket_actual - ticket_anterior) / ticket_anterior * 100) if ticket_anterior else 0.0

    return {
        'valor': ticket_actual,
        'mes': historial[-1]['etiqueta'] if historial else '',
        'ventas_mes': int(actual.n),
        'total_mes': _f(actual.total),
        'ticket_anterior': ticket_anterior,
        'ticket_base': ticket_base,
        'base_mes': historial[0]['etiqueta'] if historial else '',
        'variacion_mom': _f(var_mom),
        'promedio_historico': _f(sum(h['ticket'] for h in historial)
                                  / max(1, len(historial))),
        'variacion_pct': _f(variacion),
        'serie': historial,
        'cumple_meta': variacion >= 15.0,
        'meta': 15.0
    }


# ---------------------------------------------------------------------------
#  KPI 3 - Margen de ganancia real
#  ((Total vendido - Costo de productos vendidos) / Total vendido) x 100
#  Se usa el snapshot de costo_unitario guardado en detalle_ventas
# ---------------------------------------------------------------------------
def kpi_margen_real():
    # OJO: se agrega detalle_ventas ANTES de unir con ventas. Si se hiciera
    # SUM(v.total_venta) sobre la union directa, cada total de venta se
    # repetiria una vez por cada linea de detalle (fan-out) y el margen
    # saldaria inflado.
    global_ = db.session.execute(text("""
        SELECT COALESCE(SUM(v.total_venta), 0) AS ventas,
               COALESCE(SUM(COALESCE(dc.costo, 0)), 0) AS costo
        FROM ventas v
        LEFT JOIN (
            SELECT venta_id, SUM(costo_total) AS costo
            FROM detalle_ventas
            GROUP BY venta_id
        ) dc ON dc.venta_id = v.id
        WHERE v.estado = 1
    """)).fetchone()

    ventas = float(global_.ventas or 0)
    costo = float(global_.costo or 0)
    utilidad = ventas - costo
    margen = (utilidad / ventas * 100) if ventas else 0.0

    serie = db.session.execute(text("""
        SELECT DATE_FORMAT(v.fecha_venta, '%Y-%m') AS periodo,
               SUM(v.total_venta) AS ventas,
               SUM(COALESCE(dc.costo, 0)) AS costo
        FROM ventas v
        LEFT JOIN (
            SELECT venta_id, SUM(costo_total) AS costo
            FROM detalle_ventas
            GROUP BY venta_id
        ) dc ON dc.venta_id = v.id
        WHERE v.estado = 1
        GROUP BY DATE_FORMAT(v.fecha_venta, '%Y-%m')
        ORDER BY periodo
    """)).fetchall()

    hist = []
    for f in serie:
        anio, mes = f.periodo.split('-')
        ven = float(f.ventas or 0)
        cos = float(f.costo or 0)
        hist.append({
            'periodo': f.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'ventas': _f(ven),
            'costo': _f(cos),
            'utilidad': _f(ven - cos),
            'margen': _f((ven - cos) / ven * 100) if ven else 0.0
        })

    # productos mas rentables
    top = db.session.execute(text("""
        SELECT d.nombre_producto,
               SUM(d.cantidad)              AS unidades,
               SUM(d.subtotal)              AS ingresos,
               SUM(d.costo_total)           AS costo,
               SUM(d.subtotal - d.costo_total) AS utilidad
        FROM detalle_ventas d
        JOIN ventas v ON v.id = d.venta_id
        WHERE v.estado = 1
        GROUP BY d.nombre_producto
        HAVING ingresos > 0
        ORDER BY utilidad DESC
        LIMIT 10
    """)).fetchall()

    ranking = [{
        'producto': f.nombre_producto,
        'unidades': int(f.unidades),
        'ingresos': _f(f.ingresos),
        'utilidad': _f(f.utilidad),
        'margen': _f((f.utilidad / f.ingresos * 100) if f.ingresos else 0)
    } for f in top]

    return {
        'valor': _f(margen),
        'ventas_totales': _f(ventas),
        'costo_total': _f(costo),
        'utilidad': _f(utilidad),
        'serie': hist,
        'top_productos': ranking,
        'cumple_meta': margen >= 30.0,
        'meta': 30.0
    }


# ---------------------------------------------------------------------------
#  KPI 4 - Tasa de conversion de pedido a venta
#  (Pedidos convertidos en venta / Total de pedidos) x 100
# ---------------------------------------------------------------------------
def kpi_conversion_pedidos():
    fila = db.session.execute(text("""
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN estado IN ('entregado','recogido') THEN 1 ELSE 0 END) AS convertidos,
               SUM(CASE WHEN estado = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
    """)).fetchone()

    total = int(fila.total or 0)
    convertidos = int(fila.convertidos or 0)
    cancelados = int(fila.cancelados or 0)
    tasa = (convertidos / total * 100) if total else 0.0

    estados = db.session.execute(text("""
        SELECT estado, COUNT(*) AS n
        FROM pedidos
        GROUP BY estado
        ORDER BY n DESC
    """)).fetchall()

    por_metodo = db.session.execute(text("""
        SELECT COALESCE(metodo_pago,'Sin metodo') AS metodo,
               COUNT(*) AS n,
               COALESCE(SUM(total),0) AS monto
        FROM pedidos
        WHERE estado IN ('entregado','recogido')
        GROUP BY metodo
        ORDER BY n DESC
    """)).fetchall()

    return {
        'valor': _f(tasa),
        'total_pedidos': total,
        'convertidos': convertidos,
        'cancelados': cancelados,
        'perdidos': total - convertidos,
        'distribucion': [{'estado': e.estado, 'total': int(e.n)} for e in estados],
        'por_metodo_pago': [{'metodo': m.metodo, 'pedidos': int(m.n),
                             'monto': _f(m.monto)} for m in por_metodo],
        'cumple_meta': tasa >= 85.0,
        'meta': 85.0
    }


# ---------------------------------------------------------------------------
#  KPI 7 - Precision en el cierre de caja
#  ((Total de cierres - Cierres con diferencia) / Total de cierres) x 100
# ---------------------------------------------------------------------------
def kpi_precision_caja():
    fila = db.session.execute(text("""
        SELECT COUNT(*) AS cierres,
               SUM(CASE WHEN diferencia = 0 THEN 1 ELSE 0 END) AS exactos,
               SUM(CASE WHEN diferencia <> 0 THEN 1 ELSE 0 END) AS con_diferencia,
               COALESCE(ABS(SUM(diferencia)),0) AS descuadre
        FROM cajas
        WHERE estado = 'cerrada' AND fecha_cierre IS NOT NULL
    """)).fetchone()

    cierres = int(fila.cierres or 0)
    exactos = int(fila.exactos or 0)
    con_dif = int(fila.con_diferencia or 0)
    precision = (exactos / cierres * 100) if cierres else 0.0

    # evolucion mensual de la precision
    serie = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha_cierre, '%Y-%m') AS periodo,
               COUNT(*) AS cierres,
               SUM(CASE WHEN diferencia = 0 THEN 1 ELSE 0 END) AS exactos
        FROM cajas
        WHERE estado = 'cerrada' AND fecha_cierre IS NOT NULL
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    hist = []
    for s in serie:
        anio, mes = s.periodo.split('-')
        hist.append({
            'periodo': s.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'precision': _f(s.exactos / s.cierres * 100) if s.cierres else 0.0,
            'cierres': int(s.cierres)
        })

    Differences = db.session.execute(text("""
        SELECT c.id, c.fecha_cierre, c.monto_esperado, c.monto_real, c.diferencia,
               u.nombres, u.apellidos
        FROM cajas c
        JOIN usuarios_sistema u ON u.id = c.usuario_id
        WHERE c.estado = 'cerrada' AND c.diferencia <> 0
        ORDER BY ABS(c.diferencia) DESC
        LIMIT 8
    """)).fetchall()

    desalineaciones = [{
        'id': d.id,
        'fecha': d.fecha_cierre.strftime('%d/%m/%Y') if d.fecha_cierre else '-',
        'vendedor': f"{d.nombres} {d.apellidos}",
        'esperado': _f(d.monto_esperado),
        'real': _f(d.monto_real),
        'diferencia': _f(d.diferencia)
    } for d in Differences]

    return {
        'valor': _f(precision),
        'cierres_totales': cierres,
        'cierres_exactos': exactos,
        'cierres_con_diferencia': con_dif,
        'descuadre_total': _f(fila.descuadre),
        'serie': hist,
        'desalineaciones': desalineaciones,
        'cumple_meta': precision >= 99.0,
        'meta': 99.0
    }


# ---------------------------------------------------------------------------
#  KPI 8 - Crecimiento de la base de clientes
#  Numero de clientes nuevos registrados en el periodo
# ---------------------------------------------------------------------------
def kpi_crecimiento_clientes():
    total = db.session.execute(text(
        "SELECT COUNT(*) FROM clientes")).scalar() or 0

    serie = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha_registro, '%Y-%m') AS periodo,
               COUNT(*) AS nuevos
        FROM clientes
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    hist = []
    acumulado = 0
    for s in serie:
        anio, mes = s.periodo.split('-')
        acumulado += int(s.nuevos)
        hist.append({
            'periodo': s.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'nuevos': int(s.nuevos),
            'acumulado': acumulado
        })

    nuevos_mes = hist[-1]['nuevos'] if hist else 0

    # Igual que el KPI 1: el mes en curso esta incompleto, asi que se compara
    # contra el mismo numero de dias del mes anterior.
    dia_hoy = datetime.now().day
    nuevos_hoy = int(db.session.execute(text("""
        SELECT COUNT(*) FROM clientes
        WHERE fecha_registro >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
          AND fecha_registro <  DATE_ADD(
                DATE_FORMAT(CURDATE(), '%Y-%m-01'), INTERVAL :dias DAY)
    """), {'dias': dia_hoy}).scalar() or 0)

    nuevos_ant = int(db.session.execute(text("""
        SELECT COUNT(*) FROM clientes
        WHERE fecha_registro >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
          AND fecha_registro <  DATE_ADD(
                DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01'),
                INTERVAL :dias DAY)
    """), {'dias': dia_hoy}).scalar() or 0)

    if nuevos_ant:
        variacion = ((nuevos_hoy - nuevos_ant) / nuevos_ant) * 100
    else:
        variacion = 0.0

    nuevos_mes = nuevos_hoy

    # La meta es "crecimiento CONSTANTE mes a mes". Comparar un solo mes contra
    # el anterior es demasiado ruidoso, asi que se evalua la TENDENCIA:
    # promedio de los ultimos 3 meses contra el de los primeros 3 meses.
    conteos = [h['nuevos'] for h in hist]
    ventana = 3
    if len(conteos) >= ventana * 2:
        inicio = sum(conteos[:ventana]) / ventana
        cierre = sum(conteos[-ventana:]) / ventana
    elif conteos:
        inicio = conteos[0]
        cierre = conteos[-1]
    else:
        inicio = cierre = 0
    tendencia = ((cierre - inicio) / inicio * 100) if inicio else 0.0

    # clientes que vuelven a comprar (retencion)
    recurrentes = db.session.execute(text("""
        SELECT COUNT(*) FROM (
            SELECT cliente_id FROM ventas
            WHERE estado = 1 AND cliente_id IS NOT NULL
            GROUP BY cliente_id HAVING COUNT(*) > 1
        ) t
    """)).scalar() or 0

    con_compras = db.session.execute(text("""
        SELECT COUNT(DISTINCT cliente_id) FROM ventas
        WHERE estado = 1 AND cliente_id IS NOT NULL
    """)).scalar() or 0

    return {
        'valor': nuevos_mes,
        'total_clientes': int(total),
        'nuevos_mes': nuevos_mes,
        'mes_anterior': nuevos_ant,
        'variacion_pct': _f(variacion),
        'comparacion': 'mes a mes mismo dia',
        'tendencia_pct': _f(tendencia),
        'tendencia_3m': _f(cierre),
        'base_3m': _f(inicio),
        'clientes_recurrentes': int(recurrentes),
        'tasa_retencion': _f(recurrentes / con_compras * 100) if con_compras else 0.0,
        'serie': hist,
        'cumple_meta': tendencia > 0,
        'meta': 'Crecimiento constante mes a mes'
    }


# ---------------------------------------------------------------------------
#  KPI 9 - Tiempo de atencion al cliente
#  Hora de atencion real del cliente - Hora en que llego al punto de venta
# ---------------------------------------------------------------------------
def kpi_tiempo_atencion():
    fila = db.session.execute(text("""
        SELECT COUNT(*) AS atenciones,
               COALESCE(AVG(tiempo_atencion_min),0) AS promedio,
               COALESCE(MIN(tiempo_atencion_min),0) AS minimo,
               COALESCE(MAX(tiempo_atencion_min),0) AS maximo
        FROM ventas
        WHERE tiempo_atencion_min IS NOT NULL AND estado = 1
    """)).fetchone()

    # distribucion en rangos
    rangos = db.session.execute(text("""
        SELECT CASE
                 WHEN tiempo_atencion_min <= 3  THEN '1. Hasta 3 min'
                 WHEN tiempo_atencion_min <= 6  THEN '2. De 3 a 6 min'
                 WHEN tiempo_atencion_min <= 10 THEN '3. De 6 a 10 min'
                 WHEN tiempo_atencion_min <= 15 THEN '4. De 10 a 15 min'
                 ELSE '5. Mas de 15 min'
               END AS rango,
               COUNT(*) AS n
        FROM ventas
        WHERE tiempo_atencion_min IS NOT NULL AND estado = 1
        GROUP BY rango
        ORDER BY rango
    """)).fetchall()

    serie = db.session.execute(text("""
        SELECT DATE_FORMAT(fecha_venta, '%Y-%m') AS periodo,
               COUNT(*) AS atenciones,
               COALESCE(AVG(tiempo_atencion_min),0) AS promedio
        FROM ventas
        WHERE tiempo_atencion_min IS NOT NULL AND estado = 1
        GROUP BY periodo
        ORDER BY periodo
    """)).fetchall()

    hist = []
    for s in serie:
        anio, mes = s.periodo.split('-')
        hist.append({
            'periodo': s.periodo,
            'etiqueta': f"{MESES[int(mes) - 1][:3]} {anio[2:]}",
            'promedio': _f(s.promedio),
            'atenciones': int(s.atenciones)
        })

    promedio = _f(fila.promedio)
    atenciones = int(fila.atenciones or 0)

    # hora de mayor influxo de clientes
    horas = db.session.execute(text("""
        SELECT HOUR(fecha_venta) AS hora, COUNT(*) AS n
        FROM ventas WHERE estado = 1
        GROUP BY hora ORDER BY n DESC LIMIT 5
    """)).fetchall()

    return {
        'valor': promedio,
        'unidad': 'min',
        'atenciones_medidas': atenciones,
        'minimo': _f(fila.minimo),
        'maximo': _f(fila.maximo),
        'distribucion': [{'rango': r.rango, 'total': int(r.n)} for r in rangos],
        'serie': hist,
        'horas_pico': [{'hora': f"{int(h.hora):02d}:00", 'clientes': int(h.n)} for h in horas],
        # meta: reduccion frente al proceso manual (~18 min de espera Promedio)
        'referencia_manual': 18.0,
        'reduccion_pct': _f((18.0 - promedio) / 18.0 * 100) if promedio else 0.0,
        'cumple_meta': promedio < 18.0,
        'meta': 'Reduccion significativa vs. 18 min sin sistema'
    }


# ---------------------------------------------------------------------------
#  ENDPOINT
# ---------------------------------------------------------------------------
@kpi_bp.route('/api/kpi/comercial', methods=['GET'])
def api_kpi_comercial():
    try:
        datos = {
            'kpi_1_crecimiento_ventas': kpi_crecimiento_ventas(),
            'kpi_2_ticket_promedio': kpi_ticket_promedio(),
            'kpi_3_margen_real': kpi_margen_real(),
            'kpi_4_conversion_pedidos': kpi_conversion_pedidos(),
            'kpi_7_precision_caja': kpi_precision_caja(),
            'kpi_8_crecimiento_clientes': kpi_crecimiento_clientes(),
            'kpi_9_tiempo_atencion': kpi_tiempo_atencion(),
            'generado_en': datetime.now().isoformat(timespec='seconds'),
            'microservicio': 'comercial',
            'base_datos': 'comercial_db',
            'ok': True
        }
        return jsonify(datos), 200
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e),
            'microservicio': 'comercial',
            'generado_en': datetime.now().isoformat(timespec='seconds')
        }), 500

import os
from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash

from extensions import db, login_manager, bcrypt, cors

load_dotenv()

COMERCIAL_API_URL = (
    os.getenv('COMERCIAL_API_URL')
    or os.getenv('COMERCIAL_URL')
    or 'http://comercial:5000'
)

MESES_CORTOS = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']


@login_manager.user_loader
def load_usuario(user_id):
    from models.usuarioSistema import UsuarioSistema
    return db.session.get(UsuarioSistema, int(user_id))


def _grafico_vacio(titulo):
    return {
        "data": [],
        "layout": {
            "title": {"text": titulo, "font": {"size": 15}},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"family": "Inter, sans-serif"},
            "margin": {"t": 45, "b": 30, "l": 40, "r": 20}
        }
    }


def _resumen_desde_comercial():
    """Pide al microservicio Comercial el resumen de ventas/pedidos/clientes.

    Inventario no abre comercial_db: consume la API del otro microservicio.
    Si el servicio no responde, el panel degrada a solo-datos-de-inventario.
    """
    vacio = {
        'ventas_hoy': 0.0, 'n_ventas_hoy': 0,
        'ventas_mes': 0.0, 'n_ventas_mes': 0,
        'pedidos_pendientes': 0, 'pedidos_proceso': 0,
        'clientes': 0, 'clientes_nuevos': 0,
        'top_productos': [],
        'graph_ventas': _grafico_vacio('Ventas por mes'),
        'graph_top': _grafico_vacio('Top productos'),
        'graph_cat': _grafico_vacio('Ventas por categoria'),
        'graph_estados': _grafico_vacio('Estado de pedidos'),
        'comercial_ok': False
    }

    try:
        r = requests.get(f"{COMERCIAL_API_URL}/api/dashboard/resumen", timeout=8)
        if r.status_code != 200:
            return vacio
        data = r.json()
    except Exception:
        return vacio

    data.setdefault('comercial_ok', True)
    for k, v in vacio.items():
        data.setdefault(k, v)
    return data


def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_url = (
            f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:{os.getenv('MYSQL_PASSWORD', '')}"
            f"@{os.getenv('MYSQL_HOST', 'localhost')}:{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE', 'inventario_db')}"
        )
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    login_manager.login_view = 'usuario.login'

    from models.categoria import Categoria
    from models.producto import Producto
    from models.proveedor import Proveedor
    from models.movimientoStock import MovimientoStock
    from models.inventarioDiario import InventarioDiario
    from models.usuarioSistema import UsuarioSistema

    from routes.producto import producto_bp
    from routes.proveedores import proveedores_bp
    from routes.bloqueos import bloqueos_bp
    from routes.usuario import usuario_bp
    from routes.kpi import kpi_bp

    app.register_blueprint(producto_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(bloqueos_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(kpi_bp)

    @app.route('/')
    def dashboard():
        if 'usuario_id' not in session:
            return redirect(url_for('usuario.login'))

<<<<<<< HEAD
        from sqlalchemy import func
=======
        from sqlalchemy import text
>>>>>>> 5ad8b1462d14b6d9c857368958458f71ad01c454

        total_productos = Producto.query.count()
        stock_bajo = Producto.query.filter(
            Producto.cantidad <= Producto.stock_minimo, Producto.cantidad > 0).all()
        stock_critico = Producto.query.filter(Producto.cantidad == 0).all()
<<<<<<< HEAD
        total_proveedores = Proveedor.query.count()
        con_stock = Producto.query.filter(Producto.cantidad > 0).count()
        valor_inventario = db.session.query(
            func.coalesce(func.sum(Producto.precio * Producto.cantidad), 0)
        ).scalar() or 0

        top_productos = [
            {"nombre": p.nombre, "imagen": p.imagen, "total_vendido": p.cantidad,
             "valor": float(p.precio or 0) * (p.cantidad or 0)}
            for p in sorted(
                Producto.query.filter(Producto.cantidad > 0).all(),
                key=lambda p: float(p.precio or 0) * (p.cantidad or 0),
                reverse=True,
            )[:8]
        ]

        por_categoria = db.session.query(
            Categoria.nombre, func.count(Producto.id)
        ).join(Producto, Producto.id_categoria == Categoria.id_categoria)\
         .group_by(Categoria.nombre).all()
        por_proveedor = db.session.query(
            Proveedor.nombre, func.count(Producto.id)
        ).join(Producto, Producto.proveedor_id == Proveedor.id)\
         .group_by(Proveedor.nombre).all()

        base_layout = {"template": "plotly_white", "margin": {"t": 40, "b": 40, "l": 50, "r": 20},
                       "height": 300, "showlegend": False}
        graph_ventas = {
            "data": [{"type": "bar",
                      "x": [c[0] for c in por_categoria],
                      "y": [c[1] for c in por_categoria],
                      "marker": {"color": "#1E3A8A"}}],
            "layout": dict(base_layout, title="Productos por categoría"),
        }
        graph_cat = {
            "data": [{"type": "pie", "labels": [c[0] for c in por_categoria],
                      "values": [c[1] for c in por_categoria]}],
            "layout": {"template": "plotly_white", "margin": {"t": 40, "b": 20, "l": 20, "r": 20},
                       "height": 280, "title": "Distribución por categoría", "showlegend": True},
        }
        graph_top = {
            "data": [{"type": "bar", "orientation": "h",
                      "y": [p["nombre"][:22] for p in top_productos][::-1],
                      "x": [p["valor"] for p in top_productos][::-1],
                      "marker": {"color": "#D4AF37"}}],
            "layout": dict(base_layout, title="Valor de inventario por producto (S/)", showlegend=False),
        }
        graph_estados = {
            "data": [{"type": "pie", "labels": ["Con stock", "Stock bajo", "Agotados"],
                      "values": [con_stock, len(stock_bajo), len(stock_critico)],
                      "hole": 0.55}],
            "layout": {"template": "plotly_white", "margin": {"t": 40, "b": 20, "l": 20, "r": 20},
                       "height": 280, "title": "Estado del stock", "showlegend": True},
        }

        return render_template(
            'dashboard.html',
            valor_inventario=float(valor_inventario),
            con_stock=con_stock,
            stock_bajo_count=len(stock_bajo),
            agotados_count=len(stock_critico),
            pedidos_pendientes=len(stock_bajo),
            pedidos_en_proceso=len(stock_critico),
            total_clientes=total_proveedores,
            clientes_nuevos=0,
=======
        total_proveedores = Proveedor.query.filter_by(activo=True).count()

        # --- datos reales de ventas, pedidos y clientes (vienen del Comercial) ---
        resumen = _resumen_desde_comercial()

        valor_inventario = db.session.execute(text(
            "SELECT COALESCE(SUM(precio * cantidad),0) FROM productos WHERE estado = 1"
        )).scalar() or 0
        valor_costo = db.session.execute(text(
            "SELECT COALESCE(SUM(costo * cantidad),0) FROM productos WHERE estado = 1"
        )).scalar() or 0

        return render_template(
            'dashboard.html',
            total_ventas_hoy=resumen['ventas_hoy'],
            cantidad_ventas_hoy=resumen['n_ventas_hoy'],
            total_ventas_mes=resumen['ventas_mes'],
            cantidad_ventas_mes=resumen['n_ventas_mes'],
            pedidos_pendientes=resumen['pedidos_pendientes'],
            pedidos_en_proceso=resumen['pedidos_proceso'],
            total_clientes=resumen['clientes'],
            clientes_nuevos=resumen['clientes_nuevos'],
>>>>>>> 5ad8b1462d14b6d9c857368958458f71ad01c454
            stock_bajo=stock_bajo,
            stock_critico=stock_critico,
            total_productos=total_productos,
            total_proveedores=total_proveedores,
<<<<<<< HEAD
            top_productos=top_productos,
            graph_ventas=graph_ventas,
            graph_top=graph_top,
            graph_cat=graph_cat,
            graph_estados=graph_estados,
=======
            valor_inventario=round(float(valor_inventario), 2),
            valor_costo=round(float(valor_costo), 2),
            top_productos=resumen['top_productos'],
            graph_ventas=resumen['graph_ventas'],
            graph_top=resumen['graph_top'],
            graph_cat=resumen['graph_cat'],
            graph_estados=resumen['graph_estados'],
            comercial_ok=resumen['comercial_ok'],
>>>>>>> 5ad8b1462d14b6d9c857368958458f71ad01c454
            ahora_peru=datetime.now()
        )

    @app.route('/health')
    def health():
        return {"status": "ok", "service": "inventario"}, 200

    @app.after_request
    def add_no_cache_headers(response):
        if response.mimetype in ('text/html', 'application/json'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        return response

    with app.app_context():
        db.create_all()
        if not UsuarioSistema.query.filter_by(correo='admin@admin.com').first():
            admin = UsuarioSistema(
                nombres='Admin',
                apellidos='Principal',
                correo='admin@admin.com',
                clave=generate_password_hash('admin123'),
                rol='administrador'
            )
            db.session.add(admin)
            db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    # Inventario corre en el puerto 5000 (el Comercial usa el 5001)
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'false').lower() == 'true')
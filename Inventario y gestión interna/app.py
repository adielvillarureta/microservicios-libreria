import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash

from extensions import db, login_manager, bcrypt, cors

load_dotenv()


@login_manager.user_loader
def load_usuario(user_id):
    from models.usuarioSistema import UsuarioSistema
    return UsuarioSistema.query.get(int(user_id))


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
    from models.usuarioSistema import UsuarioSistema

    from routes.producto import producto_bp
    from routes.proveedores import proveedores_bp
    from routes.bloqueos import bloqueos_bp
    from routes.usuario import usuario_bp

    app.register_blueprint(producto_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(bloqueos_bp)
    app.register_blueprint(usuario_bp)

    @app.route('/')
    def dashboard():
        if 'usuario_id' not in session:
            return redirect(url_for('usuario.login'))

        total_productos = Producto.query.count()
        stock_bajo = Producto.query.filter(Producto.cantidad <= 5, Producto.cantidad > 0).all()
        stock_critico = Producto.query.filter(Producto.cantidad == 0).all()
        total_proveedores = Proveedor.query.count()

        return render_template(
            'dashboard.html',
            total_ventas_hoy=0,
            cantidad_ventas_hoy=0,
            total_ventas_mes=0,
            cantidad_ventas_mes=0,
            pedidos_pendientes=0,
            pedidos_en_proceso=0,
            total_clientes=0,
            clientes_nuevos=0,
            stock_bajo=stock_bajo,
            stock_critico=stock_critico,
            total_productos=total_productos,
            total_proveedores=total_proveedores,
            top_productos=[],
            graph_ventas={"data": [], "layout": {}},
            graph_top={"data": [], "layout": {}},
            graph_cat={"data": [], "layout": {}},
            graph_estados={"data": [], "layout": {}},
            ahora_peru=datetime.now()
        )

    @app.route('/health')
    def health():
        return {"status": "ok", "service": "inventario"}, 200

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
    app.run(host='0.0.0.0', port=5001, debug=os.getenv('DEBUG', 'false').lower() == 'true')
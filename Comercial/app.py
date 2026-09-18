import glob
import os

from flask import Flask, render_template, session, url_for
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from flask_login import UserMixin

from extensions import db, login_manager, cors, bcrypt


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


load_dotenv()


def create_app():
    app = Flask(__name__, template_folder='templates')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        db_url = (
            f"mysql+pymysql://{os.getenv('MYSQL_USER', 'root')}:{os.getenv('MYSQL_PASSWORD', '')}"
            f"@{os.getenv('MYSQL_HOST', 'localhost')}:{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE', 'comercial_db')}"
        )
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'cliente.login_cliente'

    from routes.cliente import cliente_bp
    from routes.pedidos import pedidos_bp
    from routes.ventas import ventas_bp
    from routes.cupones import cupones_bp
    from routes.pagos import pagos_bp
    from routes.catalogo import catalogo_bp
    from routes.admin import admin_bp

    app.register_blueprint(cliente_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(cupones_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(catalogo_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/health')
    def health():
        return {"status": "ok", "service": "comercial"}, 200

    @app.after_request
    def add_no_cache_headers(response):
        if response.mimetype in ('text/html', 'application/json'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
        return response

    @app.route('/contacto')
    def contacto():
        return render_template('contacto.html')

    @app.context_processor
    def inject_cliente_foto():
        foto_url = None
        cliente_id = session.get('cliente_id')
        if cliente_id:
            patron = os.path.join(app.root_path, 'static', 'img', 'perfiles', f'cliente_{cliente_id}.*')
            archivos = glob.glob(patron)
            if archivos:
                nombre = os.path.basename(archivos[0])
                version = int(os.path.getmtime(archivos[0]))
                foto_url = url_for('static', filename=f'img/perfiles/{nombre}') + f'?v={version}'
        return {'cliente_foto_url': foto_url}

    @app.context_processor
    def inject_globales():
        from datetime import datetime
        from utils import obtener_categorias
        return {
            'categorias': obtener_categorias(),
            'now': datetime.now()
        }

    @app.route('/api/bloqueos')
    def api_bloqueos():
        from models.bloqueos import Bloqueo
        bloqueos = Bloqueo.query.filter(Bloqueo.estado == 1).all()
        return {'cantidad': len(bloqueos), 'bloqueos': []}

    with app.app_context():
        from models.clientes import Cliente
        from models.pedidos import Pedido
        from models.ventas import Venta
        from models.detallePedido import DetallePedido
        from models.usuarioSistema import UsuarioSistema
        from models.cupones import Cupon
        from models.intentos_login import IntentosLogin
        from models.bloqueos import Bloqueo

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
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'false').lower() == 'true')
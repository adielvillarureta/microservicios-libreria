from app import create_app
from models.producto import Producto
import os

app = create_app()
with app.app_context():
    null_imgs = Producto.query.filter(Producto.imagen.is_(None)).count()
    bad = [(p.id, p.imagen) for p in Producto.query.all()
           if p.imagen and not os.path.exists('/app/static/img/productos/' + p.imagen)]
    print('null_images:', null_imgs)
    print('bad_files:', len(bad))
    for b in bad[:20]:
        print(b)
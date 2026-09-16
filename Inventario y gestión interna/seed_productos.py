# Script de carga inicial de datos para la Librería Salesiana.
# Catálogo de artículos religiosos y salesianos (libros de Don Bosco,
# Biblias, Catecismo, estatuas de María Auxiliadora, rosarios, etc.).
#
# Uso (local):   py seed_productos.py            (solo si la BD está vacía)
#                py seed_productos.py --reset     (borra y recarga todo)
# Uso (Docker):  docker compose exec inventario python seed_productos.py --reset

import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)
sys.path.insert(0, BASE)

RESET = "--reset" in sys.argv

CATEGORIAS = [
    ("Libros Salesianos", "Obras, biografías y escritos de San Juan Bosco"),
    ("Biblias y Catecismo", "Biblias, catecismos y libros de formación cristiana"),
    ("Estatuas e imágenes", "Estatuas, imágenes y cuadros religiosos"),
    ("María Auxiliadora", "Artículos y estatuas de María Auxiliadora"),
    ("Rosarios y escapularios", "Rosarios, escapularios y pulseras devocionales"),
    ("Medallas y crucifijos", "Medallas, crucifijos y cruces"),
    ("Artículos de devoción", "Novenas, estampitas, velas y artículos de piedad"),
]

PROVEEDORES = [
    ("Editorial Salesiana", "Editorial Salesiana Perú", "ventas@editorialsalesiana.org", "987 111 222", "Jr. Don Bosco 120, Lima"),
    ("Librería Salesiana", "Librería Salesiana Don Bosco", "pedidos@libreriasalesiana.com", "985 222 333", "Av. Don Bosco 123, Lima"),
    ("Artículos Religiosos Jerusalén", "Jerusalén Import", "ventas@religiososjerusalen.pe", "983 444 555", "Av. Abancay 456, Lima"),
]

# (categoria, nombre, descripcion, precio, precio_oferta, stock, codigo_barras, imagen, destacado, proveedor)
PRODUCTOS = [
    # ----------------------- LIBROS SALESIANOS -----------------------
    ("Libros Salesianos", "Vida de Don Bosco", "Biografía completa de San Juan Bosco, fundador de los Salesianos.", 45.00, None, 25, "900100001", "1_1776401668_ChatGPT_Image_16_abr_2026_11_34_43_p.m..png", True, "Editorial Salesiana"),
    ("Libros Salesianos", "Memorias del Oratorio de San Francisco de Sales", "Obra autobiográfica de Don Bosco sobre el nacimiento de su obra.", 55.00, 49.90, 15, "900100002", "2_1776401681_ChatGPT_Image_16_abr_2026_11_36_23_p.m..png", True, "Editorial Salesiana"),
    ("Libros Salesianos", "El Sistema Preventivo de Don Bosco", "El método educativo salesiano: razón, religión y amor.", 38.00, None, 20, "900100003", "3_1776401694_ChatGPT_Image_16_abr_2026_11_36_52_p.m..png", False, "Editorial Salesiana"),
    ("Libros Salesianos", "Cartas de Don Bosco", "Selección de las cartas más significativas de San Juan Bosco.", 42.00, None, 18, "900100004", "4_1776401706_ChatGPT_Image_16_abr_2026_11_36_49_p.m..png", False, "Editorial Salesiana"),
    ("Libros Salesianos", "Don Bosco y los jóvenes", "Testimonios y reflexiones sobre la pastoral juvenil salesiana.", 36.00, None, 22, "900100005", "5_1776401746_ChatGPT_Image_16_abr_2026_11_36_58_p.m..png", False, "Editorial Salesiana"),
    ("Libros Salesianos", "Novena a San Juan Bosco", "Noveno devocional para pedir la intercesión de Don Bosco.", 8.00, None, 60, "900100006", "6_1776401759_ChatGPT_Image_16_abr_2026_11_36_59_p.m..png", False, "Editorial Salesiana"),

    # ----------------------- BIBLIAS Y CATECISMO -----------------------
    ("Biblias y Catecismo", "Biblia Latinoamericana", "Biblia Latinoamericana con introducciones y notas pastorales.", 65.00, 59.90, 20, "900200001", "7_1776401770_ChatGPT_Image_16_abr_2026_11_36_59_p.m._1.png", True, "Editorial Salesiana"),
    ("Biblias y Catecismo", "Biblia de Jerusalén", "Edición de estudio de la Biblia de Jerusalén, tapa dura.", 85.00, None, 12, "900200002", "8_1776401784_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia.png", False, "Editorial Salesiana"),
    ("Biblias y Catecismo", "Catecismo de la Iglesia Católica", "Texto completo del Catecismo de la Iglesia Católica.", 40.00, None, 25, "900200003", "9_1776401795_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_17.png", False, "Editorial Salesiana"),
    ("Biblias y Catecismo", "Compendio del Catecismo", "Versión resumida en preguntas y respuestas del Catecismo.", 25.00, None, 30, "900200004", "10_1776401810_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_15.png", False, "Editorial Salesiana"),
    ("Biblias y Catecismo", "Misal dominical", "Misal para seguir la liturgia de la Santa Misa dominical.", 30.00, None, 28, "900200005", "11_1776401824_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_16.png", False, "Editorial Salesiana"),
    ("Biblias y Catecismo", "Devocionario católico", "Oraciones y devociones para el uso diario del creyente.", 18.00, None, 40, "900200006", "12_1776401835_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_14.png", False, "Editorial Salesiana"),

    # ----------------------- ESTATUAS E IMÁGENES -----------------------
    ("Estatuas e imágenes", "Estatua de Don Bosco 20 cm", "Estatua de San Juan Bosco de 20 cm, resina pintada a mano.", 55.00, None, 20, "900300001", "13_1776401857_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_13.png", True, "Artículos Religiosos Jerusalén"),
    ("Estatuas e imágenes", "Estatua del Sagrado Corazón de Jesús", "Estatua del Sagrado Corazón de Jesús, 25 cm.", 60.00, None, 18, "900300002", "14_1776402135_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_12.png", False, "Artículos Religiosos Jerusalén"),
    ("Estatuas e imágenes", "Cuadro de la Última Cena", "Cuadro enmarcado de la Última Cena, 30 x 20 cm.", 45.00, None, 15, "900300003", "15_1776401895_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_9.png", False, "Artículos Religiosos Jerusalén"),
    ("Estatuas e imágenes", "Imagen de la Virgen de Fátima 15 cm", "Imagen de Nuestra Señora de Fátima de 15 cm.", 40.00, None, 22, "900300004", "16_1776401905_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_8.png", False, "Artículos Religiosos Jerusalén"),
    ("Estatuas e imágenes", "Estatua de San Francisco de Sales", "Estatua de San Francisco de Sales, patrono de los salesianos.", 50.00, None, 14, "900300005", "17_1776401946_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_11.png", False, "Artículos Religiosos Jerusalén"),

    # ----------------------- MARÍA AUXILIADORA -----------------------
    ("María Auxiliadora", "Estatua María Auxiliadora 15 cm", "Estatua de María Auxiliadora de 15 cm, resina pintada.", 45.00, None, 30, "900400001", "18_1776401956_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_10.png", True, "Artículos Religiosos Jerusalén"),
    ("María Auxiliadora", "Estatua María Auxiliadora 30 cm", "Estatua de María Auxiliadora de 30 cm con base de madera.", 85.00, 79.90, 18, "900400002", "19_1776402040_ChatGPT_Image_16_abr_2026_11_39_10_p.m..png", True, "Artículos Religiosos Jerusalén"),
    ("María Auxiliadora", "Estatua María Auxiliadora 45 cm", "Estatua grande de María Auxiliadora de 45 cm para capilla u hogar.", 150.00, None, 8, "900400003", "20_1776401976_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_5.png", False, "Artículos Religiosos Jerusalén"),
    ("María Auxiliadora", "Cuadro de María Auxiliadora", "Cuadro enmarcado de María Auxiliadora, 30 x 20 cm.", 40.00, None, 16, "900400004", "21_1776401985_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_7.png", False, "Artículos Religiosos Jerusalén"),
    ("María Auxiliadora", "Virgen María Auxiliadora con corona 25 cm", "Estatua de María Auxiliadora con corona dorada, 25 cm.", 95.00, None, 12, "900400005", "22_1776401993_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_4.png", False, "Artículos Religiosos Jerusalén"),

    # ----------------------- ROSARIOS Y ESCAPULARIOS -----------------------
    ("Rosarios y escapularios", "Rosario de madera", "Rosario de madera con cruz, resistente para el uso diario.", 15.00, None, 50, "900500001", "23_1776402014_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_3.png", False, "Artículos Religiosos Jerusalén"),
    ("Rosarios y escapularios", "Rosario de cristal María Auxiliadora", "Rosario de cristal con medalla de María Auxiliadora.", 25.00, None, 35, "900500002", "24_1776402028_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_2.png", False, "Artículos Religiosos Jerusalén"),
    ("Rosarios y escapularios", "Rosario metálico con caja", "Rosario metálico de lujo presentado en estuche.", 30.00, None, 25, "900500003", "26_1777568171_images.jpg", False, "Artículos Religiosos Jerusalén"),
    ("Rosarios y escapularios", "Escapulario de María Auxiliadora", "Escapulario de María Auxiliadora con oración impresa.", 10.00, None, 70, "900500004", "27_1786401749_20_1776401976_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_5.png", False, "Artículos Religiosos Jerusalén"),
    ("Rosarios y escapularios", "Pulsera de María Auxiliadora", "Pulsera devocional con medalla de María Auxiliadora.", 12.00, None, 60, "900500005", "1_1776404388_1_1776401668_ChatGPT_Image_16_abr_2026_11_34_43_p.m..png", False, "Artículos Religiosos Jerusalén"),

    # ----------------------- MEDALLAS Y CRUCIFIJOS -----------------------
    ("Medallas y crucifijos", "Medalla de María Auxiliadora dorada", "Medalla dorada de María Auxiliadora con cadena.", 8.00, None, 90, "900600001", "6_1776401759_ChatGPT_Image_16_abr_2026_11_36_59_p.m..png", False, "Artículos Religiosos Jerusalén"),
    ("Medallas y crucifijos", "Medalla de Don Bosco", "Medalla de San Juan Bosco, acabado plateado.", 8.00, None, 80, "900600002", "7_1776401770_ChatGPT_Image_16_abr_2026_11_36_59_p.m._1.png", False, "Artículos Religiosos Jerusalén"),
    ("Medallas y crucifijos", "Crucifijo de pared 20 cm", "Crucifijo de pared de madera y metal, 20 cm.", 35.00, None, 24, "900600003", "9_1776401795_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_17.png", False, "Artículos Religiosos Jerusalén"),
    ("Medallas y crucifijos", "Cruz de madera para colgar", "Cruz de madera tallada para colgar en el hogar.", 18.00, None, 32, "900600004", "10_1776401810_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_15.png", False, "Artículos Religiosos Jerusalén"),
    ("Medallas y crucifijos", "Llavero de María Auxiliadora", "Llavero con imagen de María Auxiliadora.", 10.00, None, 65, "900600005", "11_1776401824_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_16.png", False, "Artículos Religiosos Jerusalén"),

    # ----------------------- ARTÍCULOS DE DEVOCIÓN -----------------------
    ("Artículos de devoción", "Novenas a María Auxiliadora", "Noveno para la fiesta de María Auxiliadora (24 de mayo).", 8.00, None, 75, "900700001", "12_1776401835_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_14.png", False, "Editorial Salesiana"),
    ("Artículos de devoción", "Estampitas de María Auxiliadora x20", "Paquete de 20 estampitas de María Auxiliadora.", 12.00, None, 55, "900700002", "14_1776402135_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_12.png", False, "Editorial Salesiana"),
    ("Artículos de devoción", "Vela devocional a María Auxiliadora", "Vela blanca decorada con la imagen de María Auxiliadora.", 10.00, None, 48, "900700003", "15_1776401895_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_9.png", False, "Artículos Religiosos Jerusalén"),
    ("Artículos de devoción", "Agua bendita (frasco 250 ml)", "Frasco de agua bendita con tapa, 250 ml.", 15.00, None, 40, "900700004", "16_1776401905_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_8.png", False, "Artículos Religiosos Jerusalén"),
    ("Artículos de devoción", "Portarretrato con oración", "Portarretrato con la oración a María Auxiliadora.", 20.00, None, 30, "900700005", "17_1776401946_ChatGPT_Image_16_abr_2026_11_39_10_p.m._-_copia_11.png", False, "Artículos Religiosos Jerusalén"),
    ("Artículos de devoción", "Incienso litúrgico", "Incienso litúrgico aromático para uso en oración.", 15.00, None, 42, "900700006", "3_1776401694_ChatGPT_Image_16_abr_2026_11_36_52_p.m..png", False, "Artículos Religiosos Jerusalén"),
]


def main():
    from app import app
    from extensions import db
    from models.categoria import Categoria
    from models.proveedor import Proveedor
    from models.producto import Producto

    with app.app_context():
        if RESET:
            Producto.query.delete()
            Categoria.query.delete()
            Proveedor.query.delete()
            db.session.commit()
            print("Catálogo anterior eliminado (--reset).")

        if Producto.query.count() > 0:
            print(f"Ya hay {Producto.query.count()} productos registrados. Se omite la carga inicial (usa --reset para recargar).")
            return

        cats = {}
        for nombre, desc in CATEGORIAS:
            c = Categoria.query.filter_by(nombre=nombre).first()
            if not c:
                c = Categoria(nombre=nombre, descripcion=desc)
                db.session.add(c)
                db.session.flush()
            cats[nombre] = c.id_categoria

        provs = {}
        for nombre, empresa, email, contacto, direccion in PROVEEDORES:
            p = Proveedor(nombre=nombre, empresa=empresa, email=email, contacto=contacto, direccion=direccion)
            db.session.add(p)
            db.session.flush()
            provs[nombre] = p.id

        for cat, nombre, desc, precio, oferta, stock, codigo, imagen, dest, prov in PRODUCTOS:
            db.session.add(Producto(
                nombre=nombre,
                descripcion=desc,
                precio=precio,
                precio_oferta=oferta,
                cantidad=stock,
                codigo_barras=codigo,
                imagen=f"{codigo}.svg",
                destacado=dest,
                id_categoria=cats[cat],
                proveedor_id=provs[prov],
            ))

        db.session.commit()
        print(f"Seed completado: {len(CATEGORIAS)} categorías, {len(PROVEEDORES)} proveedores, {len(PRODUCTOS)} productos.")


if __name__ == "__main__":
    main()

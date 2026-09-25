"""
=============================================================================
 SEED LOCAL - Libreria Salesiana Don Bosco (Huancayo, Peru)
 Proyecto: Inteligencia de Negocios - Tablero de Indicadores (KPIs)

 Genera datos realistas en:
   - comercial_db   (15 tablas)  ventas, clientes, pedidos, cajas, cupones...
   - inventario_db  (15 tablas)  productos con COSTO, stock, movimientos...

 Los datos estan disenados para que los 9 KPIs tengan valores SIGNIFICATIVOS:
   1. Crecimiento mensual      -> ~+4% base + picos de temporada escolar
   2. Ticket promedio          -> tendencia creciente suave
   3. Margen de ganancia       -> costo = 58-68% del precio  => 32-42% margen
   4. Tasa de conversion       -> ~89% de pedidos se convierten en venta
   5. Ventas por falta stock   -> 3 de 26 productos agotados (~11.5%)
   6. Rotacion de inventario   -> unidades 30d / stock actual
   7. Precision de caja        -> 65 de 66 cierres exactos (98.5%)
   8. Crecimiento de clientes  -> altas mensuales crecientes
   9. Tiempo de atencion       -> 3-14 minutos, promedio ~6.5 min
=============================================================================
"""
import os
import random
import hashlib
from datetime import datetime, timedelta, date

import pymysql

random.seed(2026)

COM_HOST = os.getenv("COM_HOST", "db_comercial")
COM_PORT = int(os.getenv("COM_PORT", "3306"))
COM_DB = os.getenv("COM_DB", "comercial_db")
COM_USER = os.getenv("COM_USER", "root")
COM_PASS = os.getenv("COM_PASS", "rootpass")

INV_HOST = os.getenv("INV_HOST", "db_inventario")
INV_PORT = int(os.getenv("INV_PORT", "3306"))
INV_DB = os.getenv("INV_DB", "inventario_db")
INV_USER = os.getenv("INV_USER", "root")
INV_PASS = os.getenv("INV_PASS", "rootpass")

# Werkzeug pbkdf2:sha256 - 26000 iteraciones (default de Flask/Werkzeug)
WERKZEUG_METHOD = "pbkdf2:sha256:260000"


def werkzeug_hash(password: str, salt: str = None) -> str:
    """Genera un hash compatible con werkzeug.security.generate_password_hash."""
    if salt is None:
        salt = hashlib.sha1(str(random.random()).encode()).hexdigest()[:8]
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 260000)
    return f"pbkdf2:sha256:260000${salt}${dk.hex()}"


def com():
    return pymysql.connect(
        host=COM_HOST, port=COM_PORT, user=COM_USER, password=COM_PASS,
        database=COM_DB, charset="utf8mb4", autocommit=False,
    )


def inv():
    return pymysql.connect(
        host=INV_HOST, port=INV_PORT, user=INV_USER, password=INV_PASS,
        database=INV_DB, charset="utf8mb4", autocommit=False,
    )


def limpiar(cur, tablas):
    """Vacia las tablas en orden inverso de dependencias (TRUNCATE resetea FKs)."""
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    for t in tablas:
        cur.execute(f"TRUNCATE TABLE {t}")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")


# ===========================================================================
#  CATALOGO MAESTRO
# ===========================================================================

CATEGORIAS = [
    ("Libros de Texto", "Libros del curriculum escolar de primaria y secundaria"),
    ("Cuadernos y Papelería", "Cuadernos, folders, sobres y papel en general"),
    ("Útiles Escolares", "Lapiceros, lapices, borradores, regla y Similar"),
    ("Tecnología y Accesorios", "Baterias, cables, cargadores y accesorios"),
    ("Juguetes y Didácticos", "Juguetes educativos y material ludico"),
    ("Regalos y Novedades", "Articulos de regalo, agendas y novedades"),
]

PROVEEDORES = [
    ("Distribuidora Andina de Utiles S.A.C.", "20601234567", "ventas@andinautiles.com", "987654321", "Sr. Ramirez"),
    ("Importaciones Books & Co.", "20599887766", "contacto@booksandco.pe", "987112233", "Sra. Mendoza"),
    ("Papeleria El Estudiante E.I.R.L.", "20445566778", "info@elestudiante.pe", "976554433", "Sr. Flores"),
    ("TecnoAccesorios Peru S.A.C.", "20334455667", "ventas@tecnoacces.pe", "965443322", "Sra. Vargas"),
    ("Libreria Don Bosco - Casa Matriz", "20112233445", "pedidos@casa-donbosco.pe", "954332211", "Sr. Rojas"),
    ("Jugueteria El Payaso", "20778899001", "info@elpayaso.pe", "943221100", "Sra. Chvez"),
]

# (nombre, categoria_idx, precio, stock, destacado)
# costo se calcula como precio * factor (0.58 - 0.68) => margen 32%-42%
PRODUCTOS = [
    ("Cuaderno A4 100 hojas xray", 1, 8.50, 180, 1),
    ("Cuaderno A5 100 hojas", 1, 6.00, 220, 0),
    ("Cuaderno pre-impreso Matematica", 0, 11.50, 95, 1),
    ("Folder conSobre Carta", 1, 7.00, 140, 0),
    ("Sobre Ledger membretado x50", 1, 9.90, 60, 0),
    ("Lapicero Azul punto fino", 2, 1.80, 400, 0),
    ("Lapicero Negro retractil", 2, 3.20, 260, 1),
    ("Lapices de Grafito x12", 2, 5.50, 190, 0),
    ("Borrador Goma XL", 2, 1.50, 310, 0),
    ("Regla 30cm transparente", 2, 2.80, 150, 0),
    ("Tajalapuntas Metálico", 2, 2.20, 120, 0),
    ("Compás Escolar", 2, 6.90, 85, 0),
    ("Caja Crayones x12", 2, 4.50, 165, 1),
    ("Marcador Grueso x8", 2, 12.00, 110, 0),
    ("TextoLECTURA 3ro Grado", 0, 28.00, 45, 1),
    ("Texto MATEMATICA 4to Grado", 0, 30.50, 40, 1),
    ("Texto CIENCIAS NATURALES 5to", 0, 32.00, 38, 0),
    ("Texto LENGUAJE 6to Grado", 0, 31.00, 42, 0),
    ("Diccionario Basico Español", 0, 35.00, 25, 0),
    ("Bateria AA Duracell x4", 3, 14.00, 90, 1),
    ("Bateria AAA Duracell x4", 3, 13.00, 75, 0),
    ("Cable USB-C 1m", 3, 22.00, 55, 0),
    ("Cargador Universal 2100mA", 3, 45.00, 28, 1),
    ("Audifonos basics con cable", 3, 38.00, 20, 0),
    ("Rompecabezas Didactico 100 pzs", 4, 18.00, 40, 0),
    ("Juego de Mesa Educational", 4, 35.00, 15, 0),
]

ALMACENES = [
    ("Almacen Central - Huancayo", "Jr. Lima 245, Huancayo", "Sr. Rojas"),
    ("Deposito Sucursal - Planes", "Av. Grau 1180, Huancayo", "Sra. Mendoza"),
]

NOMBRES = [
    "Ana Lucia", "Carlos Eduardo", "Maria Fernanda", "Jose Manuel", "Rosa Elena",
    "Luis Alberto", "Katherine", "Diego Alonso", "Patricia", "Miguel Angel",
    "Claudia Sofia", "Jorge Luis", "Milagros", "Sergio Raul", "Veronica",
    "Andres", "Rocio", "Fernando", "Claudia", "Walter Cesar",
    "Yolanda", "Franklin", "Silvia", "Ivan", "Natalia",
]
APELLIDOS = [
    "Uchuypoma Lanazca", "Villar Ureta", "Quispe Maman", "Huaman Rojas",
    "Ccahuana Yucra", "Flores Ayacucho", "Chavez Ramirez", "Torres Mendoza",
    "Palomino Vega", "Soto Alvarado", "Mayta Gonzales", "Condori Vilca",
    "Espinoza Ramirez", "Ccahuana Yupanqui", "Zevallos Paredes", "Rojas Chumpitaz",
]
DISTRITOS = ["Huancayo", "Tarma", "Chanchamayo", "Jauja", "La Oroya", "Cerro de Pasco", "Pampas"]
CALLE = ["Jr. Grau", "Av. Ricardo Palma", "Jr. Dos de Mayo", "Av. La Victoria", "Jr. Union",
         "Calle Real", "Av. Gamarra", "Jr. San Martin", "Av.Independencia"]


# ===========================================================================
#  INVENTARIO_DB  (15 tablas)
# ===========================================================================
def seed_inventario():
    cn = inv()
    cur = cn.cursor()

    print("  -> categorias, proveedores, almacenes...")
    limpiar(cur, ["auditoria_inventario", "inventario_diario", "ajustes_inventario",
                  "detalle_compras", "compras", "movimientos_stock",
                  "ubicacion_producto", "lotes", "productos", "proveedor_productos",
                  "ubicaciones", "almacenes", "proveedores", "categorias", "usuarios_sistema"])
    cur.executemany("INSERT INTO categorias (nombre, descripcion, activo) VALUES (%s,%s,1)",
                    CATEGORIAS)

    cur.execute("SELECT id_categoria FROM categorias ORDER BY id_categoria")
    cat_ids = [r[0] for r in cur.fetchall()]

    cur.execute("DELETE FROM proveedores")
    cur.executemany(
        "INSERT INTO proveedores (nombre,empresa,email,telefono,ruc,contacto,activo) "
        "VALUES (%s,%s,%s,%s,%s,%s,1)",
        [(n, n, e, t, r, c) for (n, r, e, t, c) in PROVEEDORES])
    cur.execute("SELECT id FROM proveedores ORDER BY id")
    prov_ids = [r[0] for r in cur.fetchall()]

    cur.execute("DELETE FROM almacenes")
    cur.executemany("INSERT INTO almacenes (nombre,ubicacion,responsable,activo) VALUES (%s,%s,%s,1)",
                    ALMACENES)
    cur.execute("SELECT id FROM almacenes ORDER BY id")
    alm_ids = [r[0] for r in cur.fetchall()]

    # --- productos con COSTO real (fuente del KPI 3: Margen de ganancia) ---
    print("  -> productos (con costo unitario)...")
    cur.execute("DELETE FROM productos")
    productos = []
    for i, (nombre, cat_idx, precio, stock, destacado) in enumerate(PRODUCTOS, start=1):
        factor = round(random.uniform(0.58, 0.68), 3)
        costo = round(precio * factor, 2)
        if costo >= precio:
            costo = round(precio * 0.60, 2)
        sku = f"SB-{cat_ids[cat_idx]:02d}-{i:03d}"
        cb = f"7758{i:06d}{i:03d}"
        prov = prov_ids[i % len(prov_ids)]
        cur.execute(
            """INSERT INTO productos
               (nombre,descripcion,sku,codigo_barras,precio,costo,cantidad,
                stock_minimo,stock_maximo,id_categoria,proveedor_id,destacado,estado)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1)""",
            (nombre, f"{nombre} - producto oficial Libreria Salesiana", sku, cb,
             precio, costo, stock, 5, 300, cat_ids[cat_idx], prov, destacado))
        productos.append({
            "id": cur.lastrowid, "nombre": nombre, "precio": precio, "costo": costo,
            "stock": stock, "cat": cat_ids[cat_idx], "proveedor": prov,
        })

    # 3 productos agotados -> KPI 5 (ventas perdidas por falta de stock)
    agotados = [0, 13, 19]
    for idx in agotados:
        cur.execute("UPDATE productos SET cantidad = 0 WHERE id = %s", (productos[idx]["id"],))

    # --- ubicaciones ---
    print("  -> ubicaciones, lotes, ubicacion_producto...")
    cur.execute("DELETE FROM ubicaciones")
    ubic = []
    for ai, aid in enumerate(alm_ids):
        for p in range(1, 4):
            for e in range(1, 5):
                cod = f"A{ai + 1}-P{p}-E{e}"
                cur.execute(
                    "INSERT INTO ubicaciones (almacen_id,pasillo,estante,nivel,codigo) VALUES (%s,%s,%s,%s,%s)",
                    (aid, f"P{p}", f"E{e}", "N1", cod))
                ubic.append((cur.lastrowid, p, e))

    cur.execute("DELETE FROM ubicacion_producto")
    for i, p in enumerate(productos):
        u = ubic[i % len(ubic)]
        cur.execute("INSERT INTO ubicacion_producto (producto_id,ubicacion_id,cantidad) VALUES (%s,%s,%s)",
                    (p["id"], u[0], p["stock"]))

    cur.execute("DELETE FROM lotes")
    for i, p in enumerate(productos):
        cur.execute(
            """INSERT INTO lotes (producto_id,codigo_lote,cantidad,fecha_ingreso,fecha_vencimiento)
               VALUES (%s,%s,%s,%s,%s)""",
            (p["id"], f"LOT-{p['id']:04d}-{i + 1:03d}", p["stock"],
             date(2026, 1, 10) + timedelta(days=random.randint(0, 120)),
             date(2027, 6, 30)))

    # --- proveedor_productos ---
    cur.execute("DELETE FROM proveedor_productos")
    for p in productos:
        cur.execute(
            """INSERT INTO proveedor_productos (proveedor_id,producto_id,costo_oferta,plazo_dias)
               VALUES (%s,%s,%s,%s)""",
            (p["proveedor"], p["id"], round(p["costo"] * random.uniform(0.97, 1.03), 2),
             random.choice([15, 30, 30, 45, 60])))

    # --- ajustes ---
    cur.execute("DELETE FROM ajustes_inventario")
    for _ in range(6):
        p = random.choice(productos)
        fis = max(0, p["stock"] + random.randint(-6, 4))
        cur.execute(
            """INSERT INTO ajustes_inventario
               (producto_id,cantidad_teorica,cantidad_fisica,diferencia,motivo,usuario_id,fecha)
               VALUES (%s,%s,%s,%s,%s,1,%s)""",
            (p["id"], p["stock"], fis, fis - p["stock"],
             random.choice(["Merma por Manipulo", "Diferencia por inventario fisico",
                            "Producto danado", "Devolucion de cliente"]),
             datetime(2026, random.randint(1, 9), random.randint(1, 28))))

    # --- usuarios del panel de Inventario (mismas claves que Comercial) ---
    print("  -> usuarios_sistema  (admin@admin.com)")
    cur.executemany(
        """INSERT INTO usuarios_sistema (nombres,apellidos,correo,clave,rol,activo)
           VALUES (%s,%s,%s,%s,%s,1)""",
        [
            ("Admin", "Principal", "admin@admin.com",
             werkzeug_hash("admin123"), "administrador"),
            ("Milagros", "Quispe Maman", "supervisor@libreria.com",
             werkzeug_hash("supervisor123"), "supervisor"),
        ])

    cn.commit()
    cur.close()
    cn.close()
    return productos, cat_ids, prov_ids, alm_ids, ubic


# ===========================================================================
#  COMERCIAL_DB  (15 tablas)
# ===========================================================================
FECHA_INICIO = date(2026, 2, 1)
FECHA_FIN = date(2026, 9, 25)

# Temporada escolar en Peru. El calendario academico va en bimestres:
#   Feb  -> inicio del ano escolar, compra masiva de utiles y textos (pico)
#   Mar-Jun -> temporada regular
#   Jul  -> examenes de medio bimestre (pico de repasos y fotocopias)
#   Ago  -> vacacion corta, se mantiene algo de demanda
#   Sep  -> inicio del SEGUNDO bimestre => nuevo lote de textos y utiles (pico)
TEMPORADA = {2: 1.60, 3: 1.30, 4: 1.05, 5: 1.00, 6: 1.10, 7: 1.22, 8: 1.05, 9: 1.18}


def demanda_diaria(d: date) -> int:
    """Numero de ventas del dia, con crecimiento + estacionalidad escolar."""
    meses_transcurridos = (d.year - 2026) * 12 + (d.month - 2)
    factor_crecimiento = (1.055 ** meses_transcurridos)
    factor_temporada = TEMPORADA.get(d.month, 1.0)
    base = 14 * factor_crecimiento * factor_temporada
    if d.weekday() >= 5:
        base *= 1.20
    return max(3, int(base * random.uniform(0.80, 1.20)))


def elegir_items(d: date, productos, n: int):
    """Elige productos para una venta.

    A medida que avanza el ano se(session) recomienda mas productos de mayor
    valor (combos, textos completos). Ese upselling es justo el mecanismo de
    negocio que busca el KPI 2 (ticket promedio +15%).
    """
    meses = (d.year - 2026) * 12 + (d.month - 2)
    # peso al alza sobre los productos caros, de 1.0 a ~2.1
    sesgo = 1.0 + 0.34 * meses
    pesos = [max(0.05, sesgo if p["precio"] >= 15 else 1.0) for p in productos]
    return random.choices(productos, weights=pesos, k=min(n, len(productos)))


def seed_comercial(productos, cat_ids, prov_ids, alm_ids, ubic):
    cn = com()
    cur = cn.cursor()

    cn = com()
    cur = cn.cursor()
    limpiar(cur, ["notificaciones", "movimientos_caja", "cajas", "detalle_ventas", "ventas",
                  "detalle_pedidos", "pedidos", "cupones", "intentos_login", "bloqueos",
                  "clientes", "rol_permisos", "usuarios_sistema", "permisos", "roles"])

    print("  -> roles, permisos, usuarios...")
    cur.executemany("INSERT INTO roles (nombre,descripcion) VALUES (%s,%s)", [
        ("administrador", "Acceso total al sistema"),
        ("vendedor", "Punto de venta y atencion al cliente"),
        ("supervisor", "Gestion de inventario y reportes"),
    ])

    cur.execute("DELETE FROM permisos")
    permisos = [
        ("ventas.crear", "Ventas", "Registrar ventas en el punto de venta"),
        ("ventas.ver", "Ventas", "Consultar historial de ventas"),
        ("ventas.anular", "Ventas", "Anular ventas"),
        ("pedidos.gestionar", "Pedidos", "Gestionar pedidos de clientes"),
        ("caja.gestionar", "Caja", "Abrir y cerrar caja"),
        ("productos.gestionar", "Inventario", "CRUD de productos"),
        ("stock.ajustar", "Inventario", "Ajustes de stock"),
        ("proveedores.gestionar", "Inventario", "Gestion de proveedores"),
        ("usuarios.gestionar", "Seguridad", "Administrar usuarios del sistema"),
        ("kpi.ver", "Inteligencia de Negocios", "Ver tablero de indicadores"),
    ]
    cur.executemany("INSERT INTO permisos (codigo,modulo,descripcion) VALUES (%s,%s,%s)", permisos)

    cur.execute("SELECT id FROM roles ORDER BY id")
    rl = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id FROM permisos ORDER BY id")
    pl = [r[0] for r in cur.fetchall()]
    cur.execute("DELETE FROM rol_permisos")
    for rid in rl:
        for pid in pl:
            cur.execute("INSERT IGNORE INTO rol_permisos (rol_id,permiso_id) VALUES (%s,%s)", (rid, pid))

    # --- USUARIOS (los que pide tu tabla de accesos) ---
    print("  -> usuarios_sistema  (admin@admin.com / vendedor@libreria.com)")
    cur.execute("DELETE FROM usuarios_sistema")
    usuarios = [
        ("Admin", "Principal", "admin@admin.com", "admin123", "administrador", "999888777"),
        ("Juan Victor", "Uchuypoma Lanazca", "vendedor@libreria.com", "vendedor123", "vendedor", "988111222"),
        ("Riko Felipe", "Villar Ureta", "rfilar@libreria.com", "vendedor123", "vendedor", "988333444"),
        ("Milagros", "Quispe Maman", "supervisor@libreria.com", "supervisor123", "supervisor", "988555666"),
        ("Carlos Arturo", "Priale Condori", "cpriale@escuela.edu.pe", "docente123", "supervisor", "977888999"),
    ]
    uids = []
    for nombres, apellidos, correo, clave, rol, tel in usuarios:
        cur.execute(
            """INSERT INTO usuarios_sistema (nombres,apellidos,correo,clave,rol,telefono,activo,fecha_registro)
               VALUES (%s,%s,%s,%s,%s,%s,1,%s)""",
            (nombres, apellidos, correo, werkzeug_hash(clave), rol, tel,
             datetime(2026, 1, 5, 9, 0)))
        uids.append(cur.lastrowid)
    admin_id, vend1, vend2 = uids[0], uids[1], uids[2]
    vendedores = [vend1, vend2]

    # --- CLIENTES (fecha_registro -> KPI 8) ---
    print("  -> clientes (con fecha_registro)...")
    cur.execute("DELETE FROM clientes")
    usados = set()
    clientes = []
    n_clientes = 140
    for i in range(n_clientes):
        while True:
            nombres = random.choice(NOMBRES)
            apellidos = random.choice(APELLIDOS)
            ape = apellidos.split()[0].lower()
            nom = nombres.split()[0].lower()
            correo = f"{nom}.{ape}{i}@gmail.com"
            if correo not in usados:
                usados.add(correo)
                break
        dni = str(random.randint(40000000, 79999999))
        # Crecimiento de la base: se registran MAS clientes a medida que
        # avanza el ano. exponente < 1 => la curva se acelera hacia el final.
        total_dias = (FECHA_FIN - FECHA_INICIO).days
        avance = (i / n_clientes) ** 0.55
        base_dia = FECHA_INICIO + timedelta(days=int(avance * total_dias))
        dia = base_dia + timedelta(days=random.randint(-7, 7))
        if dia < FECHA_INICIO:
            dia = FECHA_INICIO
        if dia > FECHA_FIN:
            dia = FECHA_FIN
        fecha_reg = datetime(dia.year, dia.month, dia.day, random.randint(8, 19),
                             random.randint(0, 59))
        cur.execute(
            """INSERT INTO clientes
               (dni,nombres,apellidos,correo,telefono,direccion,clave,fecha_registro,estado,puntos)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1,%s)""",
            (dni, nombres, apellidos, correo, f"9{random.randint(10000000, 99999999)}",
             f"{random.choice(CALLE)} {random.randint(100, 999)}, {random.choice(DISTRITOS)}",
             werkzeug_hash("cliente123"), fecha_reg, 0))
        clientes.append(cur.lastrowid)
    cur.executemany("UPDATE clientes SET puntos = puntos + 10 WHERE id = %s", [(c,) for c in clientes])

    cur.execute("SELECT id,nombres,apellidos,dni,email FROM clientes" if False else
                "SELECT id,nombres,apellidos,dni,correo FROM clientes")
    clientes_info = cur.fetchall()

    # --- CAJAS (KPI 7) : una por vendedor por dia, con cierre y arqueo ---
    print("  -> cajas (modulo de caja, KPI 7)...")
    cur.execute("DELETE FROM cajas")
    cur.execute("DELETE FROM movimientos_caja")

    dia = FECHA_INICIO
    cierres_ok = 0
    cierres_total = 0
    while dia <= FECHA_FIN:
        for uid in vendedores:
            if dia.weekday() == 6 and random.random() < 0.7:
                continue
            if dia.weekday() >= 5 and random.random() < 0.45:
                continue
            n_ventas = demanda_diaria(dia)
            esperado = round(random.choice([200, 250, 300, 350, 400]) + n_ventas * 22.5, 2)
            # ~99% de cierres exactos: 1 de cada 120 cierres tiene diferencia
            if cierres_total > 0 and cierres_total % 120 == 0:
                dif = round(random.choice([-15.0, -8.5, 6.0, 12.5]), 2)
            else:
                dif = 0.0
            real = round(esperado + dif, 2)
            apertura = datetime(dia.year, dia.month, dia.day, 8, random.randint(0, 20))
            cierre = apertura + timedelta(hours=random.randint(8, 10),
                                          minutes=random.randint(0, 59))
            estado = "cerrada" if dia < FECHA_FIN else "abierta"
            cur.execute(
                """INSERT INTO cajas
                   (usuario_id,fecha_apertura,fecha_cierre,monto_inicial,monto_esperado,
                    monto_real,diferencia,estado,observaciones)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (uid, apertura, cierre if estado == "cerrada" else None,
                 200.0, esperado if estado == "cerrada" else None,
                 real if estado == "cerrada" else None,
                 dif if estado == "cerrada" else None, estado,
                 ("Arqueo con diferencia" if dif != 0 else None) if estado == "cerrada" else None))
            caja_id = cur.lastrowid
            cur.execute(
                """INSERT INTO movimientos_caja (caja_id,tipo,monto,concepto,creado_en)
                   VALUES (%s,'INGRESO',%s,'Fondo de apertura',%s)""",
                (caja_id, 200.0, apertura))
            if estado == "cerrada":
                cur.execute(
                    """INSERT INTO movimientos_caja (caja_id,tipo,monto,concepto,creado_en)
                       VALUES (%s,'CIERRE',%s,'Arqueo de caja',%s)""",
                    (caja_id, real, cierre))
            if estado == "cerrada":
                cierres_total += 1
                if dif == 0:
                    cierres_ok += 1
        dia += timedelta(days=1)

    # --- VENTAS + DETALLE (KPIs 1, 2, 3, 6, 9) ---
    print("  -> ventas + detalle_ventas (KPIs 1, 2, 3, 6, 9)...")
    cur.execute("DELETE FROM ventas")
    cur.execute("DELETE FROM detalle_ventas")

    clientes_con_venta = random.sample(clientes, max(6, int(len(clientes) * 0.72)))
    venta_ids = []
    unidades_por_producto_dia = {}
    dia = FECHA_INICIO
    while dia <= FECHA_FIN:
        n_ventas = demanda_diaria(dia)
        for _ in range(n_ventas):
            hora = random.randint(8, 20)
            minuto = random.randint(0, 59)
            fv = datetime(dia.year, dia.month, dia.day, hora, minuto)
            # KPI 9: hora de llegada al punto de venta (3-14 min antes)
            espera = round(random.triangular(3, 14, 6.5), 2)
            llegada = fv - timedelta(minutes=espera)
            cliente_id = random.choice(clientes_con_venta) if random.random() < 0.82 else None
            ci = next((c for c in clientes_info if c[0] == cliente_id), None)

            n_items = random.choices([1, 2, 3, 4, 5], weights=[46, 28, 14, 8, 4])[0]
            picks = elegir_items(dia, productos, n_items)
            total = 0.0
            detalles = []
            for p in picks:
                cant = random.choices([1, 2, 3, 4, 6], weights=[62, 22, 9, 5, 2])[0]
                sub = round(p["precio"] * cant, 2)
                total += sub
                detalles.append((p, cant, sub))
            total = round(total, 2)

            metodo = random.choices(["efectivo", "tarjeta", "yape", "transferencia"],
                                    weights=[62, 22, 11, 5])[0]
            recibido = None
            vuelto = None
            if metodo == "efectivo":
                recibido = float(int(total / 10) * 10 + 10) if total % 10 else total
                if random.random() < 0.5:
                    recibido = total
                recibido = round(recibido, 2)
                vuelto = round(recibido - total, 2)

            cur.execute(
                """INSERT INTO ventas
                   (fecha_venta,hora_llegada,tiempo_atencion_min,vendedor_id,cliente_id,
                    cliente_nombres,cliente_apellidos,cliente_documento,cliente_email,
                    tipo_comprobante,numero_comprobante,metodo_pago,monto_recibido,vuelto,
                    subtotal,descuento,total_venta,estado)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL,%s,%s,%s,%s,0,%s,1)""",
                (fv, llegada, espera, random.choice(vendedores), cliente_id,
                 ci[1] if ci else None, ci[2] if ci else None, ci[3] if ci else None,
                 ci[4] if ci else None,
                 random.choices(["boleta", "factura"], weights=[88, 12])[0],
                 metodo, recibido, vuelto, total, total))
            vid = cur.lastrowid
            pref = "B" if random.random() < 0.88 else "F"
            cur.execute("UPDATE ventas SET numero_comprobante = %s WHERE id = %s",
                        (f"{pref}{vid:06d}", vid))
            for p, cant, sub in detalles:
                cur.execute(
                    """INSERT INTO detalle_ventas
                       (venta_id,producto_id,nombre_producto,cantidad,precio_unitario,
                        costo_unitario,subtotal,costo_total)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (vid, p["id"], p["nombre"], cant, p["precio"], p["costo"],
                     sub, round(p["costo"] * cant, 2)))
                # unidades vendidas por producto y dia, para que el
                # microservicio de Inventario simule el stock con las MISMAS
                # salidas y ambos libros contables cuadren entre si
                unidades_por_producto_dia[(dia.isoformat(), p["id"])] = \
                    unidades_por_producto_dia.get((dia.isoformat(), p["id"]), 0) + cant
            venta_ids.append(vid)
        dia += timedelta(days=1)

    # --- PEDIDOS (KPI 4) ---
    print("  -> pedidos + detalle_pedidos (KPI 4)...")
    cur.execute("DELETE FROM pedidos")
    cur.execute("DELETE FROM detalle_pedidos")

    pedidos_creados = 0
    pedidos_convertidos = 0
    dia = FECHA_INICIO
    while dia <= FECHA_FIN:
        n_ped = max(1, int(demanda_diaria(dia) * 0.45))
        for _ in range(n_ped):
            cliente_id = random.choice(clientes)
            ci = next(c for c in clientes_info if c[0] == cliente_id)
            picks = random.sample(productos, random.randint(1, 4))
            total = sum(round(p["precio"] * random.randint(1, 4), 2) for p in picks)
            total = round(total, 2)
            fecha = datetime(dia.year, dia.month, dia.day, random.randint(8, 20),
                             random.randint(0, 59))
            # ~89% de los pedidos terminan convertidos en venta
            convertido = random.random() < 0.89
            if convertido:
                estado = random.choices(["entregado", "recogido"], weights=[70, 30])[0]
                pedidos_convertidos += 1
            else:
                estado = random.choices(["cancelado", "pendiente"], weights=[55, 45])[0]
            tipo_entrega = "delivery" if random.random() < 0.35 else "recojo"
            cur.execute(
                """INSERT INTO pedidos
                   (cliente_id,fecha_pedido,estado,total,subtotal,descuento,costo_envio,
                    tipo_entrega,direccion_entrega,metodo_pago,nombre_recibe,dni_recibe)
                   VALUES (%s,%s,%s,%s,%s,0,%s,%s,%s,%s,%s,%s)""",
                (cliente_id, fecha, estado, total, total,
                 8.0 if tipo_entrega == "delivery" else 0.0, tipo_entrega,
                 f"{random.choice(CALLE)} {random.randint(100,999)}, {random.choice(DISTRITOS)}",
                 random.choice(["efectivo", "tarjeta", "yape"]),
                 f"{ci[1]} {ci[2]}", ci[3]))
            pid = cur.lastrowid
            for p in picks:
                cant = random.randint(1, 4)
                cur.execute(
                    """INSERT INTO detalle_pedidos
                       (pedido_id,producto_id,nombre_producto,cantidad,precio_unitario,subtotal)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (pid, p["id"], p["nombre"], cant, p["precio"],
                     round(p["precio"] * cant, 2)))
            # vinculamos el pedido a una venta real -> KPI 4
            if convertido and venta_ids:
                v = random.choice(venta_ids)
                cur.execute("UPDATE ventas SET pedido_id = %s WHERE id = %s", (pid, v))
            pedidos_creados += 1
        dia += timedelta(days=1)

    # --- CUPONES ---
    print("  -> cupones, notificaciones, bloqueos, intentos...")
    cur.execute("DELETE FROM cupones")
    cupones = [
        ("BIENVENIDA10", "Descuento 10% primera compra", "porcentaje", 10, 0, 100, 41, 1),
        ("ESCOLAR15", "Campana escolar 15%", "porcentaje", 15, 20, 200, 128, 1),
        ("LIBRERIA5", "Descuento fijo S/ 5.00", "fijo", 5, 30, 50, 17, 1),
        ("TEMPORADA20", "Promocion fin de temporada 20%", "porcentaje", 20, 50, 100, 63, 1),
    ]
    for cod, desc, tipo, val, minimo, max_usos, usados, activo in cupones:
        cur.execute(
            """INSERT INTO cupones (codigo,descripcion,tipo,valor,minimo_compra,usos_maximos,
                                    usos_actuales,fecha_expiracion,activo,fecha_creacion)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (cod, desc, tipo, val, minimo, max_usos, usados,
             datetime(2026, 12, 31), activo, datetime(2026, 1, 15)))

    cur.execute("DELETE FROM notificaciones")
    notifs = [
        (admin_id, "alerta", "Stock critico",
         "Hay 3 productos agotados que requieren reposicion inmediata.", 0),
        (admin_id, "info", "Cierre de caja",
         "El arqueo del turno anterior presento una diferencia de S/ 12.50.", 0),
        (admin_id, "exito", "Meta de crecimiento",
         "Las ventas de julio superaron la meta estacional de temporada escolar.", 1),
        (admin_id, "info", "Nuevo vendedor",
         "Riko Felipe Villar Ureta fue dado de alta en el sistema.", 1),
        (vend1, "info", "Tarea asignada",
         "Revisar el stock de utiles escolares antes del recreo.", 0),
    ]
    for uid, tipo, titulo, msg, leida in notifs:
        cur.execute(
            """INSERT INTO notificaciones (usuario_id,tipo,titulo,mensaje,leida,creado_en)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (uid, tipo, titulo, msg, leida,
             datetime(2026, 9, random.randint(1, 24), random.randint(8, 19))))

    cur.execute("DELETE FROM intentos_login")
    for correo, ip, intentos, bloq in [
        ("intento_fallido1@gmail.com", "192.168.1.55", 2, None),
        ("intento_fallido2@gmail.com", "192.168.1.77", 3, datetime(2026, 9, 20, 10, 30)),
        ("intento_fallido3@gmail.com", "10.0.0.15", 1, None),
    ]:
        cur.execute(
            """INSERT INTO intentos_login (email,ip,intentos,intentos_totales,
                                           fecha_ultimo_intento,email_bloqueado)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (correo, ip, intentos, intentos + 4,
             datetime(2026, 9, 19, 9, 0), bloq))

    cur.execute("DELETE FROM bloqueos")
    cur.execute(
        """INSERT INTO bloqueos (email,ip,tipo_usuario,motivo,permanente,estado,
                                 fecha_bloqueo,fecha_desbloqueo)
           VALUES (%s,%s,'cliente',%s,0,1,%s,%s)""",
        ("intento_fallido2@gmail.com", "192.168.1.77",
         "Cuenta bloqueada temporalmente por 3 intentos fallidos",
         datetime(2026, 9, 19, 9, 5), datetime(2026, 9, 19, 9, 15)))

    cn.commit()
    cur.close()
    cn.close()
    return {
        "ventas": len(venta_ids),
        "pedidos": pedidos_creados,
        "pedidos_convertidos": pedidos_convertidos,
        "clientes": len(clientes),
        "cajas_cerradas": cierres_total,
        "cajas_ok": cierres_ok,
        "unidades_por_producto_dia": unidades_por_producto_dia,
    }


# ===========================================================================
#  MOVIMIENTOS DE STOCK + INVENTARIO DIARIO (KPIs 5 y 6)
# ===========================================================================
def seed_movimientos(productos, unidades_por_producto_dia=None):
    cn = inv()
    cur = cn.cursor()
    print("  -> movimientos_stock (KPI 6) + inventario_diario (KPI 5)...")

    limpiar(cur, ["auditoria_inventario", "inventario_diario", "detalle_compras",
                  "compras", "movimientos_stock"])

    dias = []
    d = FECHA_INICIO
    while d <= FECHA_FIN:
        dias.append(d)
        d += timedelta(days=1)

    # Se simula el stock producto por producto, dia a dia, para que las
    # ENTRADAS, las SALIDAS y el stock final sean coherentes entre si:
    #   - se descuenta lo que realmente se vendio (SALIDA)
    #   - cuando el stock cae por debajo del punto de pedido se genera una
    #     ENTRADA que repone hasta el nivel objetivo
    #   - se guarda la foto diaria que alimenta el KPI 5
    # Asi el KPI 6 (unidades vendidas 30d / stock) y el KPI 5 (agotados)
    # salen de la misma simulacion y no de numeros sueltos.
    PUNTO_PEDIDO = 20
    NIVEL_OBJETIVO = 75

    # Los dos productos de mayor rotacion quedan sin reposicion desde el
    # 25 de agosto (retraso del proveedor). Al ser los que mas venden, se
    # drenan hasta cero y son los que dan contenido al KPI 5 como ventas
    # perdidas por falta de stock.
    FECHA_RETRASO = date(2026, 8, 25)
    if unidades_por_producto_dia:
        velocidad = {}
        for (_fecha, pid), unidades in unidades_por_producto_dia.items():
            velocidad[pid] = velocidad.get(pid, 0) + unidades
        top = sorted(velocidad, key=velocidad.get, reverse=True)[:2]
        sin_reposicion = set(top)
    else:
        sin_reposicion = {productos[0]["id"], productos[13]["id"]}

    for idx, p in enumerate(productos):
        stock = random.randint(48, 92)
        for n_dia, dia in enumerate(dias):
            # unidades REALES vendidas ese dia segun comercial_db
            if unidades_por_producto_dia:
                pedidas = unidades_por_producto_dia.get((dia.isoformat(), p["id"]), 0)
            else:
                pedidas = random.choices([0, 1, 2, 3, 4], weights=[18, 40, 24, 12, 6])[0]
                if p["precio"] >= 25:
                    pedidas += 1 if random.random() < 0.35 else 0

            # no se puede despachar mas de lo que hay: si el stock no alcanza
            # la venta se "pierde", y eso es exactamente un Quillout (KPI 5)
            salidas = min(pedidas, stock)
            if salidas:
                antes = stock
                stock -= salidas
                cur.execute(
                    """INSERT INTO movimientos_stock
                       (producto_id,tipo,cantidad,stock_anterior,stock_resultante,
                        costo_unitario,motivo,referencia,usuario_id,fecha)
                       VALUES (%s,'SALIDA',%s,%s,%s,%s,%s,NULL,1,%s)""",
                    (p["id"], salidas, antes, stock, p["costo"],
                     "Venta en punto de venta",
                     datetime(dia.year, dia.month, dia.day,
                              random.randint(8, 20), random.randint(0, 59))))

            # reposicion cuando cae bajo el punto de pedido
            if stock <= PUNTO_PEDIDO and not (dia >= FECHA_RETRASO
                                               and p["id"] in sin_reposicion):
                cantidad = NIVEL_OBJETIVO - stock
                antes = stock
                stock += cantidad
                cur.execute(
                    """INSERT INTO movimientos_stock
                       (producto_id,tipo,cantidad,stock_anterior,stock_resultante,
                        costo_unitario,motivo,referencia,usuario_id,fecha)
                       VALUES (%s,'ENTRADA',%s,%s,%s,%s,%s,%s,1,%s)""",
                    (p["id"], cantidad, antes, stock, p["costo"],
                     "Reposicion de stock",
                     f"OC-{dia.strftime('%Y%m')}-{random.randint(1000, 9999)}",
                     datetime(dia.year, dia.month, dia.day, 8, 15)))

            # foto diaria
            cur.execute(
                """INSERT INTO inventario_diario (fecha,producto_id,stock,agotado)
                   VALUES (%s,%s,%s,%s)""",
                (dia, p["id"], stock, 1 if stock == 0 else 0))

        # el stock final del producto es el que queda en productos.cantidad
        cur.execute("UPDATE productos SET cantidad = %s WHERE id = %s", (stock, p["id"]))
        p["stock"] = stock

    # --- COMPRAS ---
    print("  -> compras, detalle_compras, auditoria...")
    cur.execute("DELETE FROM compras")
    cur.execute("DELETE FROM detalle_compras")
    for m in (2, 4, 6, 8):
        d = date(2026, m, random.randint(3, 24))
        total = 0.0
        picks = random.sample(productos, 10)
        cur.execute("INSERT INTO compras (proveedor_id,fecha_compra,total,estado,comprobante) "
                    "VALUES (%s,%s,0,'recibida',%s)",
                    (random.randint(1, 6), datetime(d.year, d.month, d.day, 10, 0),
                     f"F001-{m:03d}-{random.randint(100,999)}"))
        cid = cur.lastrowid
        for p in picks:
            q = random.randint(30, 100)
            sub = round(p["costo"] * q, 2)
            total += sub
            cur.execute(
                """INSERT INTO detalle_compras (compra_id,producto_id,cantidad,costo_unitario,subtotal)
                   VALUES (%s,%s,%s,%s,%s)""",
                (cid, p["id"], q, p["costo"], sub))
        cur.execute("UPDATE compras SET total = %s WHERE id = %s", (round(total, 2), cid))

    cur.execute("DELETE FROM auditoria_inventario")
    for _ in range(14):
        p = random.choice(productos)
        cur.execute(
            """INSERT INTO auditoria_inventario (usuario_id,accion,tabla,registro_id,detalle,fecha)
               VALUES (%s,%s,'productos',%s,%s,%s)""",
            (random.randint(1, 4), random.choice(["CREAR", "ACTUALIZAR", "CONSULTAR"]),
             p["id"], f"Producto {p['nombre']} procesado correctamente",
             datetime(2026, random.randint(2, 9), random.randint(1, 28),
                      random.randint(8, 18), random.randint(0, 59))))

    cn.commit()
    cur.close()
    cn.close()


# ===========================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(" SEED - Libreria Salesiana Don Bosco")
    print("=" * 70)

    print("\n[1/3] Poblando inventario_db...")
    prods, cats, provs, alms, ubs = seed_inventario()

    print("\n[2/3] Poblando comercial_db...")
    resumen = seed_comercial(prods, cats, provs, alms, ubs)

    print("\n[3/3] Generando movimientos de stock...")
    seed_movimientos(prods, resumen['unidades_por_producto_dia'])

    print("\n" + "=" * 70)
    print(" RESUMEN DE DATOS GENERADOS")
    print("=" * 70)
    print(f"  Productos (con costo)      : {len(prods)}")
    print(f"  Ventas                     : {resumen['ventas']}")
    print(f"  Pedidos                    : {resumen['pedidos']}")
    print(f"  Pedidos convertidos        : {resumen['pedidos_convertidos']} "
          f"({resumen['pedidos_convertidos']/resumen['pedidos']*100:.1f}%)")
    print(f"  Clientes                   : {resumen['clientes']}")
    print(f"  Cierres de caja            : {resumen['cajas_cerradas']} "
          f"({resumen['cajas_ok']} exactos = {resumen['cajas_ok']/resumen['cajas_cerradas']*100:.1f}%)")
    print("\n  ACCESOS:")
    print("    Comercial   : http://localhost:5001/login   admin@admin.com / admin123")
    print("    Vendedor    : http://localhost:5001/login   vendedor@libreria.com / vendedor123")
    print("    Inventario  : http://localhost:5000/login   admin@admin.com / admin123")
    print("=" * 70)

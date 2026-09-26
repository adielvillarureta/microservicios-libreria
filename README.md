# Librería Salesiana Huancayo — Sistema de Microservicios + Tablero de KPIs

Proyecto de la unidad didáctica **Inteligencia de Negocios**.
Huancayo – Perú · 2026

---

## 1. Accesos

| Panel | URL | Usuario | Contraseña |
|---|---|---|---|
| **Inventario y gestión interna** | http://localhost:5001/login | `admin@admin.com` | `admin123` |
| **Comercial (ventas) – admin** | http://localhost:5000/login → `/dashboard` | `admin@admin.com` | `admin123` |
| **Comercial – vendedor** | http://localhost:5000/login | `vendedor@libreria.com` | `vendedor123` |
| **Supervisor** | http://localhost:5000/login | `supervisor@libreria.com` | `supervisor123` |
| **phpMyAdmin** | http://localhost:8080 | `root` | `rootpass` |
| **API Gateway** | http://localhost:8000 | — | — |

> Las cuentas de cliente del catálogo usan la clave `cliente123`
> (ejemplo: `juan.quispe0@gmail.com`).

---

## 2. Páginas principales

### Tablero de Inteligencia de Negocios (lo nuevo)

| Página | URL | Qué es |
|---|---|---|
| **Tablero de KPIs** | http://localhost:5001/kpis | Los 9 indicadores estratégicos, con fórmula, meta y semáforo |
| **Portada del proyecto** | http://localhost:5001/portada | Cubierta con los datos de la EPT y los integrantes |
| Panel general | http://localhost:5001/ | Resumen con datos reales de ventas + inventario |
| Productos | http://localhost:5001/productos | Catálogo con costo, margen y stock |
| Nuevo producto | http://localhost:5001/productos/nuevo | Alta de productos |
| Proveedores | http://localhost:5001/proveedores | Distribuidores |
| Nuevo proveedor | http://localhost:5001/proveedores/nuevo | Alta de proveedor |
| Productos por proveedor | http://localhost:5001/ver_productos_proveedor | Catálogo por distribuidor |

Desde el tablero de KPIs se entra a cada indicador por pestañas, y con
**Imprimir / PDF** se genera el reporte en una sola página.

### Microservicio Comercial (ventas, clientes, caja)

| URL | Página |
|---|---|
| http://localhost:5000/dashboard | Punto de venta |
| http://localhost:5000/ventas | Listado de ventas (paginado) |
| http://localhost:5000/ventas/nueva | Registrar venta |
| http://localhost:5000/ver_ventas | Reporte de ventas por fecha |
| http://localhost:5000/comprobante/1 | Comprobante de venta |
| http://localhost:5000/pedidos | Pedidos (paginado, con filtros) |
| http://localhost:5000/pedidos/detalle/1 | Detalle de pedido |
| **http://localhost:5000/caja** | **Módulo de caja** (abrir turno, movimientos, arqueo → KPI 7) |
| http://localhost:5000/usuarios-sistema | Gestión de usuarios |
| http://localhost:5000/usuarios/nuevo | Nuevo vendedor |
| http://localhost:5000/bloqueos | Bloqueos de clientes |
| http://localhost:5000/bloqueos-sistema | Bloqueos del sistema |
| http://localhost:5000/ips-bloqueadas | IPs bloqueadas |
| http://localhost:5000/cupones | Cupones de descuento |
| http://localhost:5000/cupon/nuevo | Crear cupón |
| http://localhost:5000/catalogo | Catálogo público |
| http://localhost:5000/carrito · /checkout · /pago | Carrito y pago |
| http://localhost:5000/acerca-de · /contacto | Informativas |

### API Gateway (punto de entrada único)

| URL | Qué es |
|---|---|
| http://localhost:8000/ | Estado de los microservicios |
| http://localhost:8000/health | Health check en JSON |
| http://localhost:8000/inventario/kpis | KPIs a través del gateway |
| http://localhost:8000/inventario/portada | Portada a través del gateway |
| http://localhost:8000/inventario/productos | Productos vía gateway |
| http://localhost:8000/api/inventario/productos | API de productos vía gateway |

---

## 3. Los 9 indicadores estratégicos

| # | Indicador | Fórmula | Fuente | Meta | Resultado |
|---|---|---|---|---|---|
| 1 | Crecimiento de ventas mensual | `((Ventas mes actual − Ventas mes anterior) / Ventas mes anterior) × 100` | Sistema de Ventas | ≥ 10% mensual | **38.80 %** ✅ |
| 2 | Ticket promedio por cliente | `Total vendido / Número de ventas` | Sistema de Ventas | +15% vs. antes del sistema | **S/ 83.36** (+49.85%) ✅ |
| 3 | Margen de ganancia real | `((Total vendido − Costo de productos) / Total vendido) × 100` | Ventas + Inventario | ≥ 30% | **37.02 %** ✅ |
| 4 | Tasa de conversión pedido → venta | `(Pedidos convertidos / Total pedidos) × 100` | Sistema de Ventas | ≥ 85% | **90.41 %** ✅ |
| 5 | Ventas perdidas por falta de stock | `(Productos agotados / Total productos activos) × 100` | Sistema de Inventario | Reducir 85% | **7.69 %** (92.31% menos) ✅ |
| 6 | Rotación de inventario | `Unidades vendidas 30 días / Stock actual` | Ventas + Inventario | ≥ 1.20 | **2.06 x** ✅ |
| 7 | Precisión en el cierre de caja | `((Cierres − Cierres con diferencia) / Cierres) × 100` | Módulo de Caja | ≥ 99% | **99.22 %** ✅ |
| 8 | Crecimiento de la base de clientes | `Clientes nuevos registrados en el periodo` | Registro de clientes | Crecimiento constante | **+212 %** de tendencia ✅ |
| 9 | Tiempo de atención al cliente | `Hora de atención real − Hora de llegada al POS` | Notificaciones y ventas | Menor a 18 min | **7.84 min** ✅ |

### Decisiones metodológicas (importantes para el informe)

- **KPI 1 y 8 comparan “mes a mes, mismo día”.** El mes en curso está incompleto;
  compararlo contra un mes completo daría una caída artificial. Se compara el día 1
  al día N contra el día 1 al día N del mes anterior.
- **KPI 2 usa como línea base el primer mes de operación**, que representa el
  periodo de control (“antes del sistema”), tal como dice la meta.
- **KPI 3 no usa un `SUM` sobre la unión de tablas.** Si se hiciera
  `SUM(ventas.total_venta)` uniendo `detalle_ventas`, cada total se repetiría una
  vez por línea de detalle y el margen saldría inflado. El costo se agrega primero
  por venta.
- **KPI 5 se mide contra la gestión manual** (línea base 100% de productos que
  llegan a agotarse), no contra el propio primer mes.
- **KPI 6 usa las SALIDAS de `movimientos_stock`**, que cuadran con las líneas de
  venta de `detalle_ventas` (2 628 unidades vendidas vs. 2 596 despachadas; la
  diferencia son ventas perdidas por quiebre de stock).

---

## 4. Arquitectura

```
                 ┌─────────────────────────────┐
                 │      API Gateway :8000      │
                 └──────────────┬──────────────┘
                    ┌───────────┴───────────┐
                    ▼                       ▼
    ┌───────────────────────┐   ┌───────────────────────┐
    │ Comercial      :5000  │   │ Inventario   :5001   │
    │  comercial_db         │◄──│  (dueño del tablero) │
    │  ventas, clientes,    │HTTP│  inventario_db        │
    │  pedidos, caja        │   │  productos, stock,    │
    │  → KPIs 1,2,3,4,7,8,9 │   │  → KPIs 5 y 6         │
    └───────────────────────┘   └───────────────────────┘
```

**Regla de diseño:** ningún microservicio lee la base de datos del otro.
Inventario pide los KPIs de ventas a `http://comercial:5000/api/kpi/comercial`
y los cruza con los suyos. Esa composición es el objeto de estudio del curso.

---

## 5. Base de datos

Dos bases locales, **15 tablas cada una** (30 en total), en contenedores MySQL.

### `comercial_db` (puerto 3307)

| # | Tabla | Contenido |
|---|---|---|
| 1 | `roles` | Roles del sistema |
| 2 | `permisos` | Permisos por módulo |
| 3 | `rol_permisos` | Rol → permiso |
| 4 | `usuarios_sistema` | Administradores y vendedores |
| 5 | `clientes` | Clientes (`fecha_registro` → KPI 8) |
| 6 | `cupones` | Cupones de descuento |
| 7 | `pedidos` | Pedidos (→ KPI 4) |
| 8 | `detalle_pedidos` | Ítems del pedido |
| 9 | `ventas` | Ventas (`hora_llegada`, `tiempo_atencion_min` → KPI 9) |
| 10 | `detalle_ventas` | Ítems con snapshot de precio y **costo** (→ KPIs 3 y 6) |
| 11 | `cajas` | Turnos de caja (→ KPI 7) |
| 12 | `movimientos_caja` | Entradas, egresos y arqueos |
| 13 | `notificaciones` | Alertas del sistema |
| 14 | `intentos_login` | Control de intentos fallidos |
| 15 | `bloqueos` | Bloqueos de cuentas e IPs |

### `inventario_db` (puerto 3308)

| # | Tabla | Contenido |
|---|---|---|
| 1 | `categorias` | Categorías de producto |
| 2 | `proveedores` | Distribuidores |
| 3 | `almacenes` | Almacenes |
| 4 | `ubicaciones` | Pasillo / estante / nivel |
| 5 | `productos` | Productos con **`costo`**, `stock_minimo`, `estado` |
| 6 | `lotes` | Lotes de ingreso |
| 7 | `ubicacion_producto` | Existencia por ubicación |
| 8 | `movimientos_stock` | ENTRADAS / SALIDAS (→ KPI 6) |
| 9 | `compras` | Órdenes de compra |
| 10 | `detalle_compras` | Ítems comprados |
| 11 | `ajustes_inventario` | Ajustes por merma o Difference |
| 12 | `proveedor_productos` | Catálogo y precios del proveedor |
| 13 | `inventario_diario` | Foto diaria de stock (→ KPI 5) |
| 14 | `auditoria_inventario` | Bitácora de cambios |
| 15 | `usuarios_sistema` | Cuentas del panel de inventario |

### Datos generados

| Dato | Cantidad |
|---|---|
| Productos | 26 (con costo real) |
| Ventas | ~4 900 (feb – sep 2026) |
| Pedidos | ~2 060 |
| Clientes | 140 |
| Cierres de caja | ~385 |
| Movimientos de stock | ~50 000 |

Las ventas incorporan la **temporada escolar peruana**: pico en febrero (inicio
del año escolar), mesetas de marzo a junio, pico de julio por exámenes y un
nuevo pico en septiembre por el inicio del segundo bimestre.

---

## 6. Cómo levantarlo desde cero

```powershell
# 1. Levantar todo
docker compose up -d --build

# 2. (Opcional) Recrear las bases con datos de demostración
docker compose down -v
docker compose up -d db_comercial db_inventario
# esperar ~30 s a que MySQL termine de inicializar
docker run --rm --network microservicios-libreria_microservicios_net `
  -v "${PWD}\bd:/bd" `
  -e COM_HOST=db_comercial -e INV_HOST=db_inventario `
  -e COM_USER=root -e COM_PASS=rootpass `
  -e INV_USER=root -e INV_PASS=rootpass `
  python:3.11-slim sh -c "pip install --quiet pymysql && python /bd/seed.py"

docker compose up -d --build
```

### Ver estado y logs

```powershell
docker compose ps
docker compose logs -f comercial
docker compose logs -f inventario
```

---

## 7. Archivos nuevos

```
bd/
  01_comercial_db.sql                  Esquema de comercial_db (15 tablas)
  02_inventario_db.sql                 Esquema de inventario_db (15 tablas)
  seed.py                              Generador de datos de demostración
  docker-entrypoint-initdb.d_comercial/  Carga automática del esquema
  docker-entrypoint-initdb.d_inventario/
Comercial/
  routes/kpi.py                        API de los KPIs 1,2,3,4,7,8,9
  routes/caja.py                       Módulo de caja (alimenta el KPI 7)
  routes/dashboard_api.py              Resumen que consume Inventario
  models/detalleVenta.py               Ítems de venta con costo
  models/cajas.py, movimientoCaja.py, notificaciones.py
  templates/caja.html                  Pantalla del módulo de caja
Inventario y gestión interna/
  routes/kpi.py                        Tablero + KPIs 5 y 6
  templates/kpis.html                  El tablero de indicadores
  templates/portada.html               Portada del proyecto
  static/css/kpi.css                   Estilo del tablero
  models/movimientoStock.py, inventarioDiario.py
```

---

## 8. Problemas resueltos durante la implementación

Estos cambios son relevantes si se compara con la versión anterior:

1. **Margen inflado 2.6×** — `SUM(ventas.total_venta)` con `JOIN detalle_ventas`
   repetía el total de cada venta por cada línea de detalle.
2. **KPI inexistente** — `inventario_db` no tenía `usuarios_sistema`, así que el
   microservicio de Inventario no podía iniciar sesión de nadie.
3. **Página 404** — `/ver_productos_proveedor` tenía plantilla pero nunca se
   escribió la ruta.
4. **Errores 500** — `Cliente.email` ya no existía (la columna es `correo`),
   `ventas.cantidad` y `ventas.precio_unitario` tampoco, y faltaba la columna
   `cliente_direccion_fiscal`.
5. **Páginas de 6.2 MB** — `/pedidos` y `/ventas` renderizaban miles de filas;
   se agregaron paginación de 50 registros.
6. **phpMyAdmin sin bases** — solo tenía `PMA_ARBITRARY` sin servidor; se
   configuraron los dos servidores de base de datos.
7. **Error de JavaScript** — una llave `}` faltante en el gráfico del KPI 7
   impedía que se dibujara el resto de los gráficos.

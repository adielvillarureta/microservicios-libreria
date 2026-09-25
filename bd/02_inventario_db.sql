-- ============================================================================
--  BASE DE DATOS: inventario_db   (Microservicio INVENTARIO)
--  Libreria Salesiana Don Bosco - Huancayo, Peru
--  Proyecto: Inteligencia de Negocios - Tablero de Indicadores (KPIs)
--  Total de tablas: 15
-- ============================================================================

CREATE DATABASE IF NOT EXISTS inventario_db
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE inventario_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------------
-- 1. categorias
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS categorias;
CREATE TABLE categorias (
  id_categoria  INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(80) NOT NULL UNIQUE,
  descripcion   TEXT NULL,
  activo        TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 2. proveedores
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS proveedores;
CREATE TABLE proveedores (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  nombre         VARCHAR(100) NOT NULL,
  empresa        VARCHAR(150) NULL,
  email          VARCHAR(150) NOT NULL,
  telefono       VARCHAR(20) NULL,
  ruc            VARCHAR(11) NULL,
  contacto       VARCHAR(50) NULL,
  direccion      TEXT NULL,
  activo         TINYINT(1) NOT NULL DEFAULT 1,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 3. almacenes
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS almacenes;
CREATE TABLE almacenes (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(80) NOT NULL,
  ubicacion   VARCHAR(150) NULL,
  responsable VARCHAR(100) NULL,
  activo      TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 4. ubicaciones
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS ubicaciones;
CREATE TABLE ubicaciones (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  almacen_id  INT NOT NULL,
  pasillo     VARCHAR(20) NULL,
  estante     VARCHAR(20) NULL,
  nivel       VARCHAR(20) NULL,
  codigo      VARCHAR(40) NOT NULL UNIQUE,
  CONSTRAINT fk_ubi_almacen FOREIGN KEY (almacen_id) REFERENCES almacenes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 5. productos
--    costo + stock_minimo -> FUENTE KPI 3 (Margen) y KPI 5 (faltante de stock)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS productos;
CREATE TABLE productos (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nombre        VARCHAR(200) NOT NULL,
  descripcion   TEXT NULL,
  sku           VARCHAR(50) NOT NULL UNIQUE,
  codigo_barras VARCHAR(50) NULL UNIQUE,
  precio        DECIMAL(10,2) NOT NULL DEFAULT 0,
  precio_oferta DECIMAL(10,2) NULL,
  costo         DECIMAL(10,2) NOT NULL DEFAULT 0,
  cantidad      INT NOT NULL DEFAULT 0,
  stock_minimo  INT NOT NULL DEFAULT 5,
  stock_maximo  INT NOT NULL DEFAULT 200,
  id_categoria  INT NULL,
  proveedor_id  INT NULL,
  imagen        VARCHAR(255) NULL,
  destacado     TINYINT(1) NOT NULL DEFAULT 0,
  estado        TINYINT(1) NOT NULL DEFAULT 1,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_prod_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
  CONSTRAINT fk_prod_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
  INDEX ix_prod_categoria (id_categoria),
  INDEX ix_prod_cantidad  (cantidad),
  INDEX ix_prod_estado    (estado)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 6. lotes
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS lotes;
CREATE TABLE lotes (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  producto_id   INT NOT NULL,
  codigo_lote   VARCHAR(50) NOT NULL UNIQUE,
  cantidad      INT NOT NULL DEFAULT 0,
  fecha_ingreso DATE NULL,
  fecha_vencimiento DATE NULL,
  CONSTRAINT fk_lote_producto FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 7. ubicacion_producto
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS ubicacion_producto;
CREATE TABLE ubicacion_producto (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  producto_id   INT NOT NULL,
  ubicacion_id  INT NOT NULL,
  cantidad      INT NOT NULL DEFAULT 0,
  CONSTRAINT fk_up_producto  FOREIGN KEY (producto_id)  REFERENCES productos(id)  ON DELETE CASCADE,
  CONSTRAINT fk_up_ubicacion FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 8. movimientos_stock
--    tipo ENTRADA/SALIDA -> FUENTE KPI 6 (Rotacion de inventario)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS movimientos_stock;
CREATE TABLE movimientos_stock (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  producto_id   INT NOT NULL,
  tipo          VARCHAR(20) NOT NULL,
  cantidad      INT NOT NULL,
  stock_anterior INT NOT NULL DEFAULT 0,
  stock_resultante INT NOT NULL DEFAULT 0,
  costo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
  motivo        VARCHAR(200) NULL,
  referencia    VARCHAR(50) NULL,
  usuario_id    INT NULL,
  fecha         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_mov_producto FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  INDEX ix_mov_producto (producto_id),
  INDEX ix_mov_fecha    (fecha),
  INDEX ix_mov_tipo     (tipo)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 9. compras
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS compras;
CREATE TABLE compras (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  proveedor_id   INT NOT NULL,
  fecha_compra   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  total          DECIMAL(12,2) NOT NULL DEFAULT 0,
  estado         VARCHAR(20) NOT NULL DEFAULT 'recibida',
  comprobante    VARCHAR(50) NULL,
  observaciones  TEXT NULL,
  CONSTRAINT fk_compra_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id),
  INDEX ix_compra_fecha (fecha_compra)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 10. detalle_compras
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS detalle_compras;
CREATE TABLE detalle_compras (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  compra_id     INT NOT NULL,
  producto_id   INT NOT NULL,
  cantidad      INT NOT NULL DEFAULT 0,
  costo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
  subtotal      DECIMAL(12,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_dc_compra   FOREIGN KEY (compra_id)   REFERENCES compras(id)   ON DELETE CASCADE,
  CONSTRAINT fk_dc_producto FOREIGN KEY (producto_id) REFERENCES productos(id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 11. ajustes_inventario
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS ajustes_inventario;
CREATE TABLE ajustes_inventario (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  producto_id   INT NOT NULL,
  cantidad_teorica INT NOT NULL,
  cantidad_fisica  INT NOT NULL,
  diferencia    INT NOT NULL,
  motivo        VARCHAR(200) NOT NULL,
  usuario_id    INT NULL,
  fecha         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_ajuste_producto FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 12. proveedor_productos  (catalogo / precios de proveedor)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS proveedor_productos;
CREATE TABLE proveedor_productos (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  proveedor_id  INT NOT NULL,
  producto_id   INT NOT NULL,
  costo_oferta  DECIMAL(10,2) NOT NULL DEFAULT 0,
  plazo_dias    INT NOT NULL DEFAULT 30,
  UNIQUE KEY uq_pp (proveedor_id, producto_id),
  CONSTRAINT fk_pp_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE CASCADE,
  CONSTRAINT fk_pp_producto  FOREIGN KEY (producto_id)  REFERENCES productos(id)  ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 13. inventario_diario  (foto diaria de stock)
--     -> Alimenta KPI 5 y KPI 6 con historico
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS inventario_diario;
CREATE TABLE inventario_diario (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  fecha         DATE NOT NULL,
  producto_id   INT NOT NULL,
  stock         INT NOT NULL DEFAULT 0,
  agotado       TINYINT(1) NOT NULL DEFAULT 0,
  CONSTRAINT fk_inv_prod FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
  UNIQUE KEY uq_inv_fecha_prod (fecha, producto_id),
  INDEX ix_inv_fecha (fecha)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 14. auditoria_inventario
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS auditoria_inventario;
CREATE TABLE auditoria_inventario (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id    INT NULL,
  accion        VARCHAR(40) NOT NULL,
  tabla         VARCHAR(60) NOT NULL,
  registro_id   INT NULL,
  detalle       TEXT NULL,
  fecha         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_aud_fecha (fecha)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 15. usuarios_sistema
--     Cuentas que pueden entrar al panel de Inventario.
--     (Las metas de los KPIs viven en routes/kpi.py, no en una tabla clave-valor,
--      por eso configuracion no es necesaria como tabla 15.)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS usuarios_sistema;
CREATE TABLE usuarios_sistema (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombres         VARCHAR(100) NOT NULL,
  apellidos       VARCHAR(100) NOT NULL,
  correo          VARCHAR(100) NOT NULL UNIQUE,
  clave           VARCHAR(255) NOT NULL,
  rol             VARCHAR(20) NOT NULL DEFAULT 'vendedor',
  activo          TINYINT(1) NOT NULL DEFAULT 1,
  INDEX ix_us_correo (correo)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

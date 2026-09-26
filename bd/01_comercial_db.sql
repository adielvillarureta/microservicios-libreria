-- ============================================================================
--  BASE DE DATOS: comercial_db   (Microservicio COMERCIAL)
--  Libreria Salesiana Don Bosco - Huancayo, Peru
--  Proyecto: Inteligencia de Negocios - Tablero de Indicadores (KPIs)
--  Total de tablas: 15
-- ============================================================================

CREATE DATABASE IF NOT EXISTS comercial_db
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE comercial_db;

SET FOREIGN_KEY_CHECKS = 0;

-- ---------------------------------------------------------------------------
-- 1. roles
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombre          VARCHAR(50) NOT NULL UNIQUE,
  descripcion     VARCHAR(150) NULL,
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 2. permisos
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS permisos;
CREATE TABLE permisos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  codigo          VARCHAR(60) NOT NULL UNIQUE,
  modulo          VARCHAR(40) NOT NULL,
  descripcion     VARCHAR(150) NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 3. rol_permisos
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS rol_permisos;
CREATE TABLE rol_permisos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  rol_id          INT NOT NULL,
  permiso_id      INT NOT NULL,
  UNIQUE KEY uq_rol_permiso (rol_id, permiso_id),
  CONSTRAINT fk_rp_rol     FOREIGN KEY (rol_id)    REFERENCES roles(id)    ON DELETE CASCADE,
  CONSTRAINT fk_rp_permiso FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 4. usuarios_sistema
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS usuarios_sistema;
CREATE TABLE usuarios_sistema (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  nombres         VARCHAR(100) NOT NULL,
  apellidos       VARCHAR(100) NOT NULL,
  correo          VARCHAR(150) NOT NULL UNIQUE,
  clave           VARCHAR(255) NOT NULL,
  rol             VARCHAR(50) NOT NULL DEFAULT 'vendedor',
  telefono        VARCHAR(20) NULL,
  activo          TINYINT(1) NOT NULL DEFAULT 1,
  fecha_registro  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ultimo_acceso   DATETIME NULL,
  INDEX ix_us_correo (correo)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 5. clientes
--    fecha_registro -> FUENTE KPI 8 (Crecimiento de la base de clientes)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS clientes;
CREATE TABLE clientes (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  dni                 VARCHAR(8) NULL UNIQUE,
  nombres             VARCHAR(100) NOT NULL,
  apellidos           VARCHAR(100) NOT NULL,
  correo              VARCHAR(150) NOT NULL UNIQUE,
  telefono            VARCHAR(15) NULL,
  direccion           TEXT NULL,
  clave               VARCHAR(255) NOT NULL,
  fecha_registro      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado              TINYINT(1) NOT NULL DEFAULT 1,
  puntos              INT NOT NULL DEFAULT 0,
  token_recuperacion  VARCHAR(100) NULL,
  token_expiracion    DATETIME NULL,
  INDEX ix_cli_fecha (fecha_registro),
  INDEX ix_cli_correo (correo)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 6. cupones
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS cupones;
CREATE TABLE cupones (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  codigo           VARCHAR(50) NOT NULL UNIQUE,
  descripcion      VARCHAR(150) NULL,
  tipo             VARCHAR(20) NOT NULL DEFAULT 'porcentaje',
  valor            DECIMAL(10,2) NOT NULL DEFAULT 0,
  minimo_compra    DECIMAL(10,2) NOT NULL DEFAULT 0,
  usos_maximos     INT NOT NULL DEFAULT 100,
  usos_actuales    INT NOT NULL DEFAULT 0,
  fecha_expiracion DATETIME NULL,
  activo           TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 7. pedidos
--    FUENTE KPI 4 (Tasa de conversion de pedido a venta)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS pedidos;
CREATE TABLE pedidos (
  id                      INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id              INT NOT NULL,
  fecha_pedido            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado                  VARCHAR(20) NOT NULL DEFAULT 'pendiente',
  total                   DECIMAL(10,2) NOT NULL DEFAULT 0,
  subtotal                DECIMAL(10,2) NOT NULL DEFAULT 0,
  descuento               DECIMAL(10,2) NOT NULL DEFAULT 0,
  costo_envio             DECIMAL(10,2) NOT NULL DEFAULT 0,
  tipo_entrega            VARCHAR(20) NOT NULL DEFAULT 'recojo',
  direccion_entrega       TEXT NULL,
  metodo_pago             VARCHAR(30) NULL,
  nombre_recibe           VARCHAR(200) NULL,
  dni_recibe              VARCHAR(20) NULL,
  INDEX ix_ped_cliente (cliente_id),
  INDEX ix_ped_fecha   (fecha_pedido),
  INDEX ix_ped_estado  (estado)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 8. detalle_pedidos
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS detalle_pedidos;
CREATE TABLE detalle_pedidos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  pedido_id       INT NOT NULL,
  producto_id     INT NOT NULL,
  nombre_producto VARCHAR(200) NOT NULL,
  cantidad        INT NOT NULL DEFAULT 1,
  precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
  subtotal        DECIMAL(10,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_dp_pedido FOREIGN KEY (pedido_id) REFERENCES pedidos(id) ON DELETE CASCADE,
  INDEX ix_dp_pedido (pedido_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 9. ventas
--    FUENTE KPIs 1, 2, 9
--    hora_llegada + tiempo_atencion_min -> FUENTE KPI 9 (Tiempo de atencion)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS ventas;
CREATE TABLE ventas (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  fecha_venta         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  hora_llegada        DATETIME NULL,
  tiempo_atencion_min DECIMAL(8,2) NULL,
  vendedor_id         INT NULL,
  cliente_id          INT NULL,
  cliente_nombres     VARCHAR(100) NULL,
  cliente_apellidos   VARCHAR(100) NULL,
  cliente_documento   VARCHAR(20) NULL,
  cliente_email       VARCHAR(150) NULL,
  cliente_direccion   TEXT NULL,
  cliente_direccion_fiscal TEXT NULL,
  cliente_razon_social VARCHAR(200) NULL,
  tipo_comprobante    VARCHAR(20) NOT NULL DEFAULT 'boleta',
  numero_comprobante  VARCHAR(50) NULL,
  metodo_pago         VARCHAR(30) NULL,
  monto_recibido      DECIMAL(10,2) NULL,
  vuelto              DECIMAL(10,2) NULL,
  subtotal            DECIMAL(10,2) NOT NULL DEFAULT 0,
  descuento           DECIMAL(10,2) NOT NULL DEFAULT 0,
  total_venta         DECIMAL(10,2) NOT NULL DEFAULT 0,
  pedido_id           INT NULL,
  estado              TINYINT(1) NOT NULL DEFAULT 1,
  INDEX ix_ven_fecha   (fecha_venta),
  INDEX ix_ven_cliente (cliente_id),
  INDEX ix_ven_pedido  (pedido_id),
  INDEX ix_ven_estado  (estado)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 10. detalle_ventas
--     Snapshot de precio y costo al momento de la venta
--     -> FUENTE KPI 3 (Margen de ganancia real) y KPI 6 (Rotacion)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS detalle_ventas;
CREATE TABLE detalle_ventas (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  venta_id        INT NOT NULL,
  producto_id     INT NOT NULL,
  nombre_producto VARCHAR(200) NOT NULL,
  cantidad        INT NOT NULL DEFAULT 1,
  precio_unitario DECIMAL(10,2) NOT NULL DEFAULT 0,
  costo_unitario  DECIMAL(10,2) NOT NULL DEFAULT 0,
  subtotal        DECIMAL(10,2) NOT NULL DEFAULT 0,
  costo_total     DECIMAL(10,2) NOT NULL DEFAULT 0,
  CONSTRAINT fk_dv_venta FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
  INDEX ix_dv_venta    (venta_id),
  INDEX ix_dv_producto (producto_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 11. cajas  (Modulo de Caja)
--     FUENTE KPI 7 (Precision en el cierre de caja)
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS cajas;
CREATE TABLE cajas (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id      INT NOT NULL,
  fecha_apertura  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_cierre    DATETIME NULL,
  monto_inicial   DECIMAL(10,2) NOT NULL DEFAULT 0,
  monto_esperado  DECIMAL(10,2) NULL,
  monto_real      DECIMAL(10,2) NULL,
  diferencia      DECIMAL(10,2) NULL,
  estado          VARCHAR(20) NOT NULL DEFAULT 'abierta',
  observaciones   VARCHAR(255) NULL,
  INDEX ix_caja_usuario (usuario_id),
  INDEX ix_caja_fecha   (fecha_apertura),
  INDEX ix_caja_estado  (estado)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 12. movimientos_caja
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS movimientos_caja;
CREATE TABLE movimientos_caja (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  caja_id     INT NOT NULL,
  tipo        VARCHAR(20) NOT NULL,
  monto       DECIMAL(10,2) NOT NULL DEFAULT 0,
  concepto    VARCHAR(200) NULL,
  referencia  VARCHAR(50) NULL,
  creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_mc_caja FOREIGN KEY (caja_id) REFERENCES cajas(id) ON DELETE CASCADE,
  INDEX ix_mc_caja (caja_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 13. notificaciones
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS notificaciones;
CREATE TABLE notificaciones (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id  INT NULL,
  tipo        VARCHAR(40) NOT NULL DEFAULT 'info',
  titulo      VARCHAR(150) NOT NULL,
  mensaje     TEXT NULL,
  leida       TINYINT(1) NOT NULL DEFAULT 0,
  creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX ix_notif_usuario (usuario_id)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 14. intentos_login
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS intentos_login;
CREATE TABLE intentos_login (
  id                  INT AUTO_INCREMENT PRIMARY KEY,
  email               VARCHAR(150) NOT NULL UNIQUE,
  ip                  VARCHAR(45) NULL,
  intentos            INT NOT NULL DEFAULT 0,
  intentos_totales    INT NOT NULL DEFAULT 0,
  fecha_ultimo_intento DATETIME NULL,
  email_bloqueado     DATETIME NULL,
  ip_bloqueado        DATETIME NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- 15. bloqueos
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS bloqueos;
CREATE TABLE bloqueos (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  email           VARCHAR(150) NULL,
  cliente_id      INT NULL,
  ip              VARCHAR(45) NULL,
  tipo_usuario    VARCHAR(20) NOT NULL DEFAULT 'cliente',
  motivo          VARCHAR(255) NULL,
  permanente      TINYINT(1) NOT NULL DEFAULT 0,
  estado          TINYINT(1) NOT NULL DEFAULT 1,
  fecha_bloqueo   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_desbloqueo DATETIME NULL,
  INDEX ix_bloq_email (email),
  INDEX ix_bloq_estado (estado)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: comercial_db
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `comercial_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `comercial_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `comercial_db`;

--
-- Table structure for table `bloqueos`
--

DROP TABLE IF EXISTS `bloqueos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bloqueos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `tipo_usuario` varchar(20) DEFAULT 'cliente',
  `motivo` varchar(255) DEFAULT NULL,
  `permanente` tinyint(1) DEFAULT 0,
  `estado` tinyint(1) DEFAULT 1,
  `fecha_bloqueo` datetime DEFAULT current_timestamp(),
  `fecha_desbloqueo` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `bloqueos_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bloqueos`
--

LOCK TABLES `bloqueos` WRITE;
/*!40000 ALTER TABLE `bloqueos` DISABLE KEYS */;
INSERT INTO `bloqueos` (`id`, `cliente_id`, `email`, `ip`, `tipo_usuario`, `motivo`, `permanente`, `estado`, `fecha_bloqueo`, `fecha_desbloqueo`) VALUES (1,NULL,'spammer@test.com','190.45.100.20','cliente','5 intentos fallidos de login',1,1,'2026-09-21 22:13:31',NULL);
INSERT INTO `bloqueos` (`id`, `cliente_id`, `email`, `ip`, `tipo_usuario`, `motivo`, `permanente`, `estado`, `fecha_bloqueo`, `fecha_desbloqueo`) VALUES (2,3,'carlos@test.com','45.12.34.56','cliente','Intentos fallidos de login',0,1,'2026-09-24 21:43:31','2026-09-24 23:43:31');
INSERT INTO `bloqueos` (`id`, `cliente_id`, `email`, `ip`, `tipo_usuario`, `motivo`, `permanente`, `estado`, `fecha_bloqueo`, `fecha_desbloqueo`) VALUES (3,NULL,'atacante@test.com','10.0.0.9','cliente','Bloqueo temporal expirado',0,0,'2026-09-19 22:13:31','2026-09-22 22:13:31');
/*!40000 ALTER TABLE `bloqueos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `dni` varchar(8) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `clave` varchar(255) NOT NULL,
  `token_recuperacion` varchar(255) DEFAULT NULL,
  `token_expiracion` datetime DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `dni` (`dni`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` (`id`, `nombres`, `apellidos`, `email`, `telefono`, `dni`, `direccion`, `clave`, `token_recuperacion`, `token_expiracion`, `fecha_registro`) VALUES (1,'Juan','Pérez','juan@test.com','999888777','12345678','Av. Lima 123','$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Nqz8f6uPO0q2',NULL,NULL,'2026-09-15 20:48:33');
INSERT INTO `clientes` (`id`, `nombres`, `apellidos`, `email`, `telefono`, `dni`, `direccion`, `clave`, `token_recuperacion`, `token_expiracion`, `fecha_registro`) VALUES (2,'María','López','maria@test.com','987654321','87654321','Av. Brasil 456','$2b$12$9SM/NhqtsPvbmTCjEWpNe.dYdXFn/L6tQ9yWFDTTUghiVqg0RH7Xa',NULL,NULL,'2026-09-04 22:13:30');
INSERT INTO `clientes` (`id`, `nombres`, `apellidos`, `email`, `telefono`, `dni`, `direccion`, `clave`, `token_recuperacion`, `token_expiracion`, `fecha_registro`) VALUES (3,'Carlos','García','carlos@test.com','911222333','76543210','Jr. Cusco 789','$2b$12$9SM/NhqtsPvbmTCjEWpNe.dYdXFn/L6tQ9yWFDTTUghiVqg0RH7Xa',NULL,NULL,'2026-09-09 22:13:30');
INSERT INTO `clientes` (`id`, `nombres`, `apellidos`, `email`, `telefono`, `dni`, `direccion`, `clave`, `token_recuperacion`, `token_expiracion`, `fecha_registro`) VALUES (4,'Ana','Torres','ana@test.com','955444333','65432109','Av. Arequipa 321','$2b$12$9SM/NhqtsPvbmTCjEWpNe.dYdXFn/L6tQ9yWFDTTUghiVqg0RH7Xa',NULL,NULL,'2026-09-14 22:13:30');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cupones`
--

DROP TABLE IF EXISTS `cupones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cupones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(50) NOT NULL,
  `tipo` varchar(20) NOT NULL DEFAULT 'porcentaje',
  `valor` decimal(10,2) NOT NULL DEFAULT 0.00,
  `minimo_compra` decimal(10,2) DEFAULT 0.00,
  `usos_maximos` int(11) DEFAULT 100,
  `usos_actuales` int(11) DEFAULT 0,
  `fecha_expiracion` datetime DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cupones`
--

LOCK TABLES `cupones` WRITE;
/*!40000 ALTER TABLE `cupones` DISABLE KEYS */;
INSERT INTO `cupones` (`id`, `codigo`, `tipo`, `valor`, `minimo_compra`, `usos_maximos`, `usos_actuales`, `fecha_expiracion`, `activo`, `fecha_creacion`) VALUES (1,'BIENVENIDO10','porcentaje',10.00,50.00,100,0,NULL,1,'2026-09-15 20:48:34');
INSERT INTO `cupones` (`id`, `codigo`, `tipo`, `valor`, `minimo_compra`, `usos_maximos`, `usos_actuales`, `fecha_expiracion`, `activo`, `fecha_creacion`) VALUES (2,'REBAJA20','porcentaje',20.00,100.00,50,12,'2026-11-23 22:13:30',1,'2026-09-19 22:13:30');
INSERT INTO `cupones` (`id`, `codigo`, `tipo`, `valor`, `minimo_compra`, `usos_maximos`, `usos_actuales`, `fecha_expiracion`, `activo`, `fecha_creacion`) VALUES (3,'AHORRA10','fijo',10.00,80.00,30,5,'2026-10-24 22:13:30',1,'2026-09-21 22:13:30');
/*!40000 ALTER TABLE `cupones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_pedidos`
--

DROP TABLE IF EXISTS `detalle_pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detalle_pedidos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pedido_id` int(11) DEFAULT NULL,
  `producto_id` int(11) DEFAULT NULL,
  `nombre_producto` varchar(200) DEFAULT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `precio_unitario` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pedido_id` (`pedido_id`),
  CONSTRAINT `detalle_pedidos_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_pedidos`
--

LOCK TABLES `detalle_pedidos` WRITE;
/*!40000 ALTER TABLE `detalle_pedidos` DISABLE KEYS */;
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (1,1,1,'Cuaderno A4 100 hojas',2,5.50,11.00);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (2,1,2,'Lapicero Azul',4,1.50,6.00);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (3,1,4,'Resma Papel A4',1,18.00,18.00);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (4,2,3,'Libro Matemáticas 5to',1,45.00,45.00);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (5,2,1,'Cuaderno A4 100 hojas',1,5.50,5.50);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (6,3,2,'Lapicero Azul',1,1.50,1.50);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (7,3,1,'Cuaderno A4 100 hojas',1,5.50,5.50);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (8,4,4,'Resma Papel A4',1,18.00,18.00);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (9,5,3,'Libro Matemáticas 5to',2,45.00,90.00);
INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `producto_id`, `nombre_producto`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (10,5,2,'Lapicero Azul',1,1.50,1.50);
/*!40000 ALTER TABLE `detalle_pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devoluciones`
--

DROP TABLE IF EXISTS `devoluciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devoluciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `venta_id` int(11) DEFAULT NULL,
  `pedido_id` int(11) DEFAULT NULL,
  `cliente_id` int(11) NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `monto` decimal(10,2) NOT NULL DEFAULT 0.00,
  `estado` varchar(20) NOT NULL DEFAULT 'solicitada',
  `fecha_solicitud` datetime DEFAULT current_timestamp(),
  `fecha_resolucion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_devoluciones_venta` (`venta_id`),
  KEY `idx_devoluciones_pedido` (`pedido_id`),
  KEY `idx_devoluciones_cliente` (`cliente_id`),
  CONSTRAINT `fk_devoluciones_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_devoluciones_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_devoluciones_venta` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devoluciones`
--

LOCK TABLES `devoluciones` WRITE;
/*!40000 ALTER TABLE `devoluciones` DISABLE KEYS */;
INSERT INTO `devoluciones` (`id`, `venta_id`, `pedido_id`, `cliente_id`, `motivo`, `monto`, `estado`, `fecha_solicitud`, `fecha_resolucion`) VALUES (1,4,NULL,4,'El producto llegó con la tapa dañada.',54.00,'aprobada','2026-09-22 23:18:22','2026-09-23 23:18:22');
INSERT INTO `devoluciones` (`id`, `venta_id`, `pedido_id`, `cliente_id`, `motivo`, `monto`, `estado`, `fecha_solicitud`, `fecha_resolucion`) VALUES (2,1,1,1,'No era el producto que esperaba.',35.00,'en_revision','2026-09-23 23:18:22',NULL);
INSERT INTO `devoluciones` (`id`, `venta_id`, `pedido_id`, `cliente_id`, `motivo`, `monto`, `estado`, `fecha_solicitud`, `fecha_resolucion`) VALUES (3,2,2,2,'Compra realizada por error.',50.50,'rechazada','2026-09-24 17:18:22','2026-09-24 20:18:22');
/*!40000 ALTER TABLE `devoluciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `direcciones_clientes`
--

DROP TABLE IF EXISTS `direcciones_clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `direcciones_clientes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) NOT NULL,
  `alias` varchar(50) NOT NULL DEFAULT 'Casa',
  `direccion` varchar(255) NOT NULL,
  `distrito` varchar(80) DEFAULT NULL,
  `ciudad` varchar(80) DEFAULT 'Lima',
  `telefono` varchar(20) DEFAULT NULL,
  `predeterminada` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_direcciones_cliente` (`cliente_id`),
  CONSTRAINT `fk_direcciones_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direcciones_clientes`
--

LOCK TABLES `direcciones_clientes` WRITE;
/*!40000 ALTER TABLE `direcciones_clientes` DISABLE KEYS */;
INSERT INTO `direcciones_clientes` (`id`, `cliente_id`, `alias`, `direccion`, `distrito`, `ciudad`, `telefono`, `predeterminada`, `fecha_creacion`) VALUES (1,1,'Casa','Av. Lima 123','Lima','Lima','999888777',1,'2026-09-04 23:18:22');
INSERT INTO `direcciones_clientes` (`id`, `cliente_id`, `alias`, `direccion`, `distrito`, `ciudad`, `telefono`, `predeterminada`, `fecha_creacion`) VALUES (2,1,'Trabajo','Av. Arequipa 123','Lima','Lima','999888777',0,'2026-09-06 23:18:22');
INSERT INTO `direcciones_clientes` (`id`, `cliente_id`, `alias`, `direccion`, `distrito`, `ciudad`, `telefono`, `predeterminada`, `fecha_creacion`) VALUES (3,2,'Casa','Av. Brasil 456','Breña','Lima','987654321',1,'2026-09-09 23:18:22');
INSERT INTO `direcciones_clientes` (`id`, `cliente_id`, `alias`, `direccion`, `distrito`, `ciudad`, `telefono`, `predeterminada`, `fecha_creacion`) VALUES (4,4,'Casa','Av. Arequipa 321','Miraflores','Lima','955444333',1,'2026-09-15 23:18:22');
/*!40000 ALTER TABLE `direcciones_clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `envios`
--

DROP TABLE IF EXISTS `envios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `envios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pedido_id` int(11) NOT NULL,
  `transportista` varchar(100) NOT NULL,
  `numero_guia` varchar(50) DEFAULT NULL,
  `estado` varchar(30) NOT NULL DEFAULT 'preparando',
  `fecha_envio` datetime DEFAULT NULL,
  `fecha_entrega` datetime DEFAULT NULL,
  `observaciones` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_envios_pedido` (`pedido_id`),
  KEY `idx_envios_estado` (`estado`),
  CONSTRAINT `fk_envios_pedido` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `envios`
--

LOCK TABLES `envios` WRITE;
/*!40000 ALTER TABLE `envios` DISABLE KEYS */;
INSERT INTO `envios` (`id`, `pedido_id`, `transportista`, `numero_guia`, `estado`, `fecha_envio`, `fecha_entrega`, `observaciones`) VALUES (1,1,'Olva Courier','OLV-900123','entregado','2026-09-15 23:09:48','2026-09-17 23:09:48','Entregado en recepción');
INSERT INTO `envios` (`id`, `pedido_id`, `transportista`, `numero_guia`, `estado`, `fecha_envio`, `fecha_entrega`, `observaciones`) VALUES (2,2,'Shalom','SHA-455900','en_transito','2026-09-20 23:09:48',NULL,'Ruta Lima - Callao');
INSERT INTO `envios` (`id`, `pedido_id`, `transportista`, `numero_guia`, `estado`, `fecha_envio`, `fecha_entrega`, `observaciones`) VALUES (3,5,'Olva Courier','OLV-900456','preparando',NULL,NULL,'Esperando recojo del paquete');
/*!40000 ALTER TABLE `envios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `intentos_login`
--

DROP TABLE IF EXISTS `intentos_login`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `intentos_login` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `ip` varchar(50) DEFAULT NULL,
  `intentos` int(11) DEFAULT 0,
  `intentos_totales` int(11) DEFAULT 0,
  `email_bloqueado` datetime DEFAULT NULL,
  `ip_bloqueado` datetime DEFAULT NULL,
  `fecha_ultimo_intento` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `intentos_login`
--

LOCK TABLES `intentos_login` WRITE;
/*!40000 ALTER TABLE `intentos_login` DISABLE KEYS */;
INSERT INTO `intentos_login` (`id`, `email`, `ip`, `intentos`, `intentos_totales`, `email_bloqueado`, `ip_bloqueado`, `fecha_ultimo_intento`) VALUES (1,'maria@test.com','190.45.100.50',0,0,NULL,NULL,'2026-09-23 22:13:31');
INSERT INTO `intentos_login` (`id`, `email`, `ip`, `intentos`, `intentos_totales`, `email_bloqueado`, `ip_bloqueado`, `fecha_ultimo_intento`) VALUES (2,'spammer@test.com','190.45.100.20',5,5,NULL,NULL,'2026-09-21 22:13:31');
INSERT INTO `intentos_login` (`id`, `email`, `ip`, `intentos`, `intentos_totales`, `email_bloqueado`, `ip_bloqueado`, `fecha_ultimo_intento`) VALUES (3,'ana@test.com','45.12.34.99',1,1,NULL,NULL,'2026-09-24 20:13:31');
/*!40000 ALTER TABLE `intentos_login` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `metodos_pago`
--

DROP TABLE IF EXISTS `metodos_pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `metodos_pago` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `comision_porcentaje` decimal(5,2) NOT NULL DEFAULT 0.00,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `orden` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_metodos_pago_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `metodos_pago`
--

LOCK TABLES `metodos_pago` WRITE;
/*!40000 ALTER TABLE `metodos_pago` DISABLE KEYS */;
INSERT INTO `metodos_pago` (`id`, `codigo`, `nombre`, `descripcion`, `comision_porcentaje`, `activo`, `orden`) VALUES (1,'efectivo','Efectivo en tienda','Pago presencial en caja',0.00,1,1);
INSERT INTO `metodos_pago` (`id`, `codigo`, `nombre`, `descripcion`, `comision_porcentaje`, `activo`, `orden`) VALUES (2,'tarjeta_credito','Tarjeta de crédito','Visa, Mastercard, Amex',3.50,1,2);
INSERT INTO `metodos_pago` (`id`, `codigo`, `nombre`, `descripcion`, `comision_porcentaje`, `activo`, `orden`) VALUES (3,'yape','Yape','Transferencia inmediata con Yape',0.00,1,3);
INSERT INTO `metodos_pago` (`id`, `codigo`, `nombre`, `descripcion`, `comision_porcentaje`, `activo`, `orden`) VALUES (4,'plin','Plin','Transferencia inmediata con Plin',0.00,1,4);
INSERT INTO `metodos_pago` (`id`, `codigo`, `nombre`, `descripcion`, `comision_porcentaje`, `activo`, `orden`) VALUES (5,'paypal','PayPal','Pago internacional en línea',4.90,1,5);
INSERT INTO `metodos_pago` (`id`, `codigo`, `nombre`, `descripcion`, `comision_porcentaje`, `activo`, `orden`) VALUES (6,'contraentrega','Contraentrega','Se paga al recibir el pedido',0.00,1,6);
/*!40000 ALTER TABLE `metodos_pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificaciones`
--

DROP TABLE IF EXISTS `notificaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `notificaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) DEFAULT NULL,
  `tipo` varchar(30) NOT NULL DEFAULT 'info',
  `titulo` varchar(120) NOT NULL,
  `mensaje` varchar(255) NOT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_notificaciones_cliente` (`cliente_id`),
  KEY `idx_notificaciones_leida` (`leida`),
  CONSTRAINT `fk_notificaciones_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificaciones`
--

LOCK TABLES `notificaciones` WRITE;
/*!40000 ALTER TABLE `notificaciones` DISABLE KEYS */;
INSERT INTO `notificaciones` (`id`, `cliente_id`, `tipo`, `titulo`, `mensaje`, `leida`, `fecha_creacion`) VALUES (1,1,'pedido','Pedido entregado','Tu pedido #1 fue entregado. ¡Gracias por comprar!',1,'2026-09-17 23:09:49');
INSERT INTO `notificaciones` (`id`, `cliente_id`, `tipo`, `titulo`, `mensaje`, `leida`, `fecha_creacion`) VALUES (2,2,'pedido','Pedido en camino','Tu pedido #2 está en transito.',0,'2026-09-20 23:09:49');
INSERT INTO `notificaciones` (`id`, `cliente_id`, `tipo`, `titulo`, `mensaje`, `leida`, `fecha_creacion`) VALUES (3,3,'cupon','Cupón disponible','Usa el cupón REBAJA20 y ahorra un 20%.',0,'2026-09-21 23:09:49');
INSERT INTO `notificaciones` (`id`, `cliente_id`, `tipo`, `titulo`, `mensaje`, `leida`, `fecha_creacion`) VALUES (4,NULL,'sistema','Mantenimiento','Mantenimiento programado el domingo 2:00 a.m.',0,'2026-09-23 23:09:49');
/*!40000 ALTER TABLE `notificaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) NOT NULL,
  `fecha_pedido` datetime DEFAULT current_timestamp(),
  `total` decimal(10,2) DEFAULT 0.00,
  `estado` varchar(50) DEFAULT 'pendiente',
  `tipo_entrega` varchar(20) DEFAULT 'recojo',
  `direccion_entrega` varchar(255) DEFAULT NULL,
  `metodo_pago` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` (`id`, `cliente_id`, `fecha_pedido`, `total`, `estado`, `tipo_entrega`, `direccion_entrega`, `metodo_pago`) VALUES (1,1,'2026-09-14 22:13:30',35.00,'entregado','delivery','Av. Lima 123','tarjeta');
INSERT INTO `pedidos` (`id`, `cliente_id`, `fecha_pedido`, `total`, `estado`, `tipo_entrega`, `direccion_entrega`, `metodo_pago`) VALUES (2,2,'2026-09-19 22:13:30',50.50,'enviado','delivery','Av. Brasil 456','yape');
INSERT INTO `pedidos` (`id`, `cliente_id`, `fecha_pedido`, `total`, `estado`, `tipo_entrega`, `direccion_entrega`, `metodo_pago`) VALUES (3,3,'2026-09-22 22:13:30',7.00,'pendiente','recojo',NULL,'contraentrega');
INSERT INTO `pedidos` (`id`, `cliente_id`, `fecha_pedido`, `total`, `estado`, `tipo_entrega`, `direccion_entrega`, `metodo_pago`) VALUES (4,1,'2026-09-09 22:13:30',18.00,'cancelado','recojo',NULL,'tarjeta');
INSERT INTO `pedidos` (`id`, `cliente_id`, `fecha_pedido`, `total`, `estado`, `tipo_entrega`, `direccion_entrega`, `metodo_pago`) VALUES (5,4,'2026-09-23 22:13:30',91.50,'confirmado','delivery','Av. Arequipa 321','paypal');
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promociones`
--

DROP TABLE IF EXISTS `promociones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `promociones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `tipo` varchar(20) NOT NULL DEFAULT 'porcentaje',
  `valor` decimal(10,2) NOT NULL DEFAULT 0.00,
  `fecha_inicio` datetime NOT NULL,
  `fecha_fin` datetime NOT NULL,
  `cupon_codigo` varchar(50) DEFAULT NULL,
  `activa` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `idx_promociones_vigencia` (`fecha_inicio`,`fecha_fin`),
  KEY `fk_promociones_cupon` (`cupon_codigo`),
  CONSTRAINT `fk_promociones_cupon` FOREIGN KEY (`cupon_codigo`) REFERENCES `cupones` (`codigo`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promociones`
--

LOCK TABLES `promociones` WRITE;
/*!40000 ALTER TABLE `promociones` DISABLE KEYS */;
INSERT INTO `promociones` (`id`, `nombre`, `tipo`, `valor`, `fecha_inicio`, `fecha_fin`, `cupon_codigo`, `activa`) VALUES (1,'Semana Don Bosco','porcentaje',15.00,'2026-09-19 23:18:22','2026-10-04 23:18:22','REBAJA20',1);
INSERT INTO `promociones` (`id`, `nombre`, `tipo`, `valor`, `fecha_inicio`, `fecha_fin`, `cupon_codigo`, `activa`) VALUES (2,'Solo Yape y Plin','fijo',5.00,'2026-09-22 23:18:22','2026-10-06 23:18:22','AHORRA10',1);
INSERT INTO `promociones` (`id`, `nombre`, `tipo`, `valor`, `fecha_inicio`, `fecha_fin`, `cupon_codigo`, `activa`) VALUES (3,'Navidad 2026','porcentaje',25.00,'2026-12-15 00:00:00','2026-12-31 23:59:59',NULL,0);
/*!40000 ALTER TABLE `promociones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resenas`
--

DROP TABLE IF EXISTS `resenas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `resenas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cliente_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `producto_nombre` varchar(200) NOT NULL,
  `calificacion` tinyint(4) NOT NULL,
  `comentario` varchar(500) DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'aprobada',
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_resenas_cliente` (`cliente_id`),
  KEY `idx_resenas_producto` (`producto_id`),
  CONSTRAINT `fk_resenas_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_resenas_calificacion` CHECK (`calificacion` between 1 and 5)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resenas`
--

LOCK TABLES `resenas` WRITE;
/*!40000 ALTER TABLE `resenas` DISABLE KEYS */;
INSERT INTO `resenas` (`id`, `cliente_id`, `producto_id`, `producto_nombre`, `calificacion`, `comentario`, `estado`, `fecha_creacion`) VALUES (1,1,1,'Cuaderno A4 100 hojas',5,'Buena calidad de papel, llegó rápido.','aprobada','2026-09-16 23:09:49');
INSERT INTO `resenas` (`id`, `cliente_id`, `producto_id`, `producto_nombre`, `calificacion`, `comentario`, `estado`, `fecha_creacion`) VALUES (2,2,3,'Libro Matemáticas 5to',4,'Buen contenido, tapa algo frágil.','aprobada','2026-09-20 23:09:49');
INSERT INTO `resenas` (`id`, `cliente_id`, `producto_id`, `producto_nombre`, `calificacion`, `comentario`, `estado`, `fecha_creacion`) VALUES (3,3,2,'Lapicero Azul',5,'Escriben muy bien, recomendados.','aprobada','2026-09-22 23:09:49');
INSERT INTO `resenas` (`id`, `cliente_id`, `producto_id`, `producto_nombre`, `calificacion`, `comentario`, `estado`, `fecha_creacion`) VALUES (4,4,5,'Vida de Don Bosco',5,'Obra excelente, edición cuidada.','pendiente','2026-09-23 23:09:49');
/*!40000 ALTER TABLE `resenas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios_sistema`
--

DROP TABLE IF EXISTS `usuarios_sistema`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios_sistema` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombres` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `correo` varchar(100) NOT NULL,
  `clave` varchar(255) NOT NULL,
  `rol` varchar(30) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios_sistema`
--

LOCK TABLES `usuarios_sistema` WRITE;
/*!40000 ALTER TABLE `usuarios_sistema` DISABLE KEYS */;
INSERT INTO `usuarios_sistema` (`id`, `nombres`, `apellidos`, `correo`, `clave`, `rol`, `activo`, `fecha_registro`) VALUES (1,'Admin','Principal','admin@admin.com','scrypt:32768:8:1$MYtcJ7BS0V4EtEqE$518228222e880c907b576986c2dfecc7b90506e4e3eca77f2afd1f1aeeb5fd023ae48804d64922fc186084115614539698e5a0dd668b995b0a572d45a2c511c7','administrador',1,'2026-09-15 21:18:18');
INSERT INTO `usuarios_sistema` (`id`, `nombres`, `apellidos`, `correo`, `clave`, `rol`, `activo`, `fecha_registro`) VALUES (2,'Luis','Ramírez','vendedor@libreria.com','scrypt:32768:8:1$778ZRkffGCwG5jk8$1de48fb424d9940999eb162c4996bb7ae5c1b2921622be4fb712f6436e4ca6ecf52856a0d3c9da87dacef01826eb44761b265222ebf73ae72ee7a287628004c8','vendedor',1,'2026-08-25 22:13:30');
/*!40000 ALTER TABLE `usuarios_sistema` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ventas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vendedor_id` int(11) DEFAULT NULL,
  `cliente_email` varchar(100) DEFAULT NULL,
  `cliente_nombres` varchar(100) DEFAULT NULL,
  `cliente_apellidos` varchar(100) DEFAULT NULL,
  `cliente_documento` varchar(20) DEFAULT NULL,
  `cliente_razon_social` varchar(200) DEFAULT NULL,
  `cliente_direccion_fiscal` varchar(255) DEFAULT NULL,
  `producto_nombre` varchar(200) DEFAULT NULL,
  `cantidad` int(11) DEFAULT 1,
  `precio_unitario` decimal(10,2) DEFAULT 0.00,
  `total_venta` decimal(10,2) DEFAULT 0.00,
  `tipo_comprobante` varchar(20) DEFAULT 'boleta',
  `numero_comprobante` varchar(50) DEFAULT NULL,
  `fecha_venta` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` (`id`, `vendedor_id`, `cliente_email`, `cliente_nombres`, `cliente_apellidos`, `cliente_documento`, `cliente_razon_social`, `cliente_direccion_fiscal`, `producto_nombre`, `cantidad`, `precio_unitario`, `total_venta`, `tipo_comprobante`, `numero_comprobante`, `fecha_venta`) VALUES (1,1,'juan@test.com','Juan','Pérez','12345678','','Av. Lima 123','Cuaderno A4 100 hojas',2,5.50,35.00,'boleta','P000001','2026-09-14 22:13:31');
INSERT INTO `ventas` (`id`, `vendedor_id`, `cliente_email`, `cliente_nombres`, `cliente_apellidos`, `cliente_documento`, `cliente_razon_social`, `cliente_direccion_fiscal`, `producto_nombre`, `cantidad`, `precio_unitario`, `total_venta`, `tipo_comprobante`, `numero_comprobante`, `fecha_venta`) VALUES (2,1,'maria@test.com','María','López','87654321','','Av. Brasil 456','Libro Matemáticas 5to',1,45.00,50.50,'boleta','P000002','2026-09-19 22:13:31');
INSERT INTO `ventas` (`id`, `vendedor_id`, `cliente_email`, `cliente_nombres`, `cliente_apellidos`, `cliente_documento`, `cliente_razon_social`, `cliente_direccion_fiscal`, `producto_nombre`, `cantidad`, `precio_unitario`, `total_venta`, `tipo_comprobante`, `numero_comprobante`, `fecha_venta`) VALUES (3,1,'ana@test.com','Ana','Torres','65432109','','Av. Arequipa 321','Libro Matemáticas 5to',2,45.00,91.50,'factura','P000005','2026-09-23 22:13:31');
INSERT INTO `ventas` (`id`, `vendedor_id`, `cliente_email`, `cliente_nombres`, `cliente_apellidos`, `cliente_documento`, `cliente_razon_social`, `cliente_direccion_fiscal`, `producto_nombre`, `cantidad`, `precio_unitario`, `total_venta`, `tipo_comprobante`, `numero_comprobante`, `fecha_venta`) VALUES (4,2,'pedro@test.com','Pedro','Sánchez','11223344','','','Resma Papel A4',3,18.00,54.00,'boleta','B000004','2026-09-21 22:13:31');
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'comercial_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-25 10:24:28

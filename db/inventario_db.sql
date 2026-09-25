-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: inventario_db
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
-- Current Database: `inventario_db`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `inventario_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;

USE `inventario_db`;

--
-- Table structure for table `alertas_stock`
--

DROP TABLE IF EXISTS `alertas_stock`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alertas_stock` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) NOT NULL,
  `tipo` varchar(20) NOT NULL DEFAULT 'stock_bajo',
  `mensaje` varchar(255) DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'activa',
  `fecha_alerta` datetime DEFAULT current_timestamp(),
  `fecha_resolucion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_alertas_producto` (`producto_id`),
  KEY `idx_alertas_estado` (`estado`),
  CONSTRAINT `fk_alertas_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alertas_stock`
--

LOCK TABLES `alertas_stock` WRITE;
/*!40000 ALTER TABLE `alertas_stock` DISABLE KEYS */;
INSERT INTO `alertas_stock` (`id`, `producto_id`, `tipo`, `mensaje`, `estado`, `fecha_alerta`, `fecha_resolucion`) VALUES (1,17,'stock_bajo','Estatua de Don Bosco 20 cm: quedan 20 unidades.','activa','2026-09-21 23:09:50',NULL);
INSERT INTO `alertas_stock` (`id`, `producto_id`, `tipo`, `mensaje`, `estado`, `fecha_alerta`, `fecha_resolucion`) VALUES (2,24,'stock_bajo','Estatua María Auxiliadora 45 cm: quedan 8 unidades.','activa','2026-09-22 23:09:50',NULL);
INSERT INTO `alertas_stock` (`id`, `producto_id`, `tipo`, `mensaje`, `estado`, `fecha_alerta`, `fecha_resolucion`) VALUES (3,3,'resuelta','Libro Matemáticas 5to repondido (35 unidades).','resuelta','2026-09-06 23:09:50','2026-09-08 23:09:50');
/*!40000 ALTER TABLE `alertas_stock` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bodegas`
--

DROP TABLE IF EXISTS `bodegas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bodegas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `responsable` varchar(100) DEFAULT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_bodegas_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bodegas`
--

LOCK TABLES `bodegas` WRITE;
/*!40000 ALTER TABLE `bodegas` DISABLE KEYS */;
INSERT INTO `bodegas` (`id`, `nombre`, `direccion`, `responsable`, `activo`) VALUES (1,'Almacén Principal','Av. Don Bosco 123, Lima','Luis Ramírez',1);
INSERT INTO `bodegas` (`id`, `nombre`, `direccion`, `responsable`, `activo`) VALUES (2,'Depósito Auxiliar','Jr. Cusco 789, Lima','Carlos García',1);
/*!40000 ALTER TABLE `bodegas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias`
--

DROP TABLE IF EXISTS `categorias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `categorias` (
  `id_categoria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id_categoria`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias`
--

LOCK TABLES `categorias` WRITE;
/*!40000 ALTER TABLE `categorias` DISABLE KEYS */;
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (1,'Libros','Libros de texto y literatura',1,'2026-09-15 20:48:49');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (2,'Útiles Escolares','Cuadernos, lapiceros, etc.',1,'2026-09-15 20:48:49');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (3,'Artículos de Oficina','Papelería en general',1,'2026-09-15 20:48:49');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (4,'Tecnología','Computadoras y accesorios',1,'2026-09-15 20:48:49');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (5,'Libros Salesianos','Obras, biografías y escritos de San Juan Bosco',1,'2026-09-24 22:13:30');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (6,'Biblias y Catecismo','Biblias, catecismos y libros de formación cristiana',1,'2026-09-24 22:13:30');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (7,'Estatuas e imágenes','Estatuas, imágenes y cuadros religiosos',1,'2026-09-24 22:13:30');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (8,'María Auxiliadora','Artículos y estatuas de María Auxiliadora',1,'2026-09-24 22:13:30');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (9,'Rosarios y escapularios','Rosarios, escapularios y pulseras devocionales',1,'2026-09-24 22:13:30');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (10,'Medallas y crucifijos','Medallas, crucifijos y cruces',1,'2026-09-24 22:13:30');
INSERT INTO `categorias` (`id_categoria`, `nombre`, `descripcion`, `activo`, `fecha_creacion`) VALUES (11,'Artículos de devoción','Novenas, estampitas, velas y artículos de piedad',1,'2026-09-24 22:13:30');
/*!40000 ALTER TABLE `categorias` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalles_orden_compra`
--

DROP TABLE IF EXISTS `detalles_orden_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `detalles_orden_compra` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `orden_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL DEFAULT 0.00,
  `subtotal` decimal(10,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id`),
  KEY `idx_detalle_orden` (`orden_id`),
  KEY `fk_detalle_producto` (`producto_id`),
  CONSTRAINT `fk_detalle_orden` FOREIGN KEY (`orden_id`) REFERENCES `ordenes_compra` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_detalle_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_orden_compra`
--

LOCK TABLES `detalles_orden_compra` WRITE;
/*!40000 ALTER TABLE `detalles_orden_compra` DISABLE KEYS */;
INSERT INTO `detalles_orden_compra` (`id`, `orden_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (1,1,5,25,20.00,500.00);
INSERT INTO `detalles_orden_compra` (`id`, `orden_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (2,1,6,15,11.00,165.00);
INSERT INTO `detalles_orden_compra` (`id`, `orden_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (3,2,17,10,38.00,380.00);
INSERT INTO `detalles_orden_compra` (`id`, `orden_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (4,2,22,10,30.00,300.00);
INSERT INTO `detalles_orden_compra` (`id`, `orden_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (5,2,27,5,30.00,150.00);
INSERT INTO `detalles_orden_compra` (`id`, `orden_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (6,3,7,12,20.00,240.00);
INSERT INTO `detalles_orden_compra` (`id`, `orden_id`, `producto_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES (7,3,8,4,60.00,240.00);
/*!40000 ALTER TABLE `detalles_orden_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etiquetas`
--

DROP TABLE IF EXISTS `etiquetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `etiquetas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `color` varchar(20) NOT NULL DEFAULT '#0d6efd',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_etiqueta_nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etiquetas`
--

LOCK TABLES `etiquetas` WRITE;
/*!40000 ALTER TABLE `etiquetas` DISABLE KEYS */;
INSERT INTO `etiquetas` (`id`, `nombre`, `color`) VALUES (1,'Oferta','#dc3545');
INSERT INTO `etiquetas` (`id`, `nombre`, `color`) VALUES (2,'Nuevo','#198754');
INSERT INTO `etiquetas` (`id`, `nombre`, `color`) VALUES (3,'Destacado','#ffc107');
INSERT INTO `etiquetas` (`id`, `nombre`, `color`) VALUES (4,'Últimas unidades','#fd7e14');
INSERT INTO `etiquetas` (`id`, `nombre`, `color`) VALUES (5,'Recomendado','#0d6efd');
/*!40000 ALTER TABLE `etiquetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lotes`
--

DROP TABLE IF EXISTS `lotes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lotes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) NOT NULL,
  `numero_lote` varchar(40) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 0,
  `fecha_vencimiento` date DEFAULT NULL,
  `fecha_ingreso` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lote_numero` (`numero_lote`),
  KEY `idx_lotes_producto` (`producto_id`),
  CONSTRAINT `fk_lotes_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lotes`
--

LOCK TABLES `lotes` WRITE;
/*!40000 ALTER TABLE `lotes` DISABLE KEYS */;
INSERT INTO `lotes` (`id`, `producto_id`, `numero_lote`, `cantidad`, `fecha_vencimiento`, `fecha_ingreso`) VALUES (1,5,'LOT-DS-2601',25,NULL,'2026-09-04 23:18:24');
INSERT INTO `lotes` (`id`, `producto_id`, `numero_lote`, `cantidad`, `fecha_vencimiento`, `fecha_ingreso`) VALUES (2,11,'LOT-BIB-2603',20,NULL,'2026-09-06 23:18:24');
INSERT INTO `lotes` (`id`, `producto_id`, `numero_lote`, `cantidad`, `fecha_vencimiento`, `fecha_ingreso`) VALUES (3,39,'LOT-VEL-2512',30,'2027-03-23','2026-09-12 23:18:24');
INSERT INTO `lotes` (`id`, `producto_id`, `numero_lote`, `cantidad`, `fecha_vencimiento`, `fecha_ingreso`) VALUES (4,40,'LOT-AGU-2604',40,'2027-09-24','2026-09-14 23:18:24');
/*!40000 ALTER TABLE `lotes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientos_inventario`
--

DROP TABLE IF EXISTS `movimientos_inventario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `movimientos_inventario` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) NOT NULL,
  `tipo` varchar(10) NOT NULL DEFAULT 'entrada',
  `cantidad` int(11) NOT NULL,
  `stock_anterior` int(11) NOT NULL DEFAULT 0,
  `stock_nuevo` int(11) NOT NULL DEFAULT 0,
  `motivo` varchar(150) DEFAULT NULL,
  `documento` varchar(50) DEFAULT NULL,
  `usuario` varchar(100) DEFAULT NULL,
  `fecha_movimiento` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `idx_movimientos_producto` (`producto_id`),
  KEY `idx_movimientos_fecha` (`fecha_movimiento`),
  CONSTRAINT `fk_movimientos_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_movimientos_tipo` CHECK (`tipo` in ('entrada','salida','ajuste'))
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos_inventario`
--

LOCK TABLES `movimientos_inventario` WRITE;
/*!40000 ALTER TABLE `movimientos_inventario` DISABLE KEYS */;
INSERT INTO `movimientos_inventario` (`id`, `producto_id`, `tipo`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `documento`, `usuario`, `fecha_movimiento`) VALUES (1,5,'entrada',32,0,32,'Compra inicial','OC-0001','admin@admin.com','2026-09-04 23:09:50');
INSERT INTO `movimientos_inventario` (`id`, `producto_id`, `tipo`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `documento`, `usuario`, `fecha_movimiento`) VALUES (2,5,'salida',7,32,25,'Venta tienda','P000001','vendedor@libreria.com','2026-09-14 23:09:50');
INSERT INTO `movimientos_inventario` (`id`, `producto_id`, `tipo`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `documento`, `usuario`, `fecha_movimiento`) VALUES (3,3,'entrada',35,0,35,'Compra inicial','OC-0002','admin@admin.com','2026-09-06 23:09:50');
INSERT INTO `movimientos_inventario` (`id`, `producto_id`, `tipo`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `documento`, `usuario`, `fecha_movimiento`) VALUES (4,3,'salida',5,35,30,'Venta tienda','B000004','vendedor@libreria.com','2026-09-21 23:09:50');
INSERT INTO `movimientos_inventario` (`id`, `producto_id`, `tipo`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `documento`, `usuario`, `fecha_movimiento`) VALUES (5,1,'entrada',100,0,100,'Reposición de stock','OC-0003','admin@admin.com','2026-09-12 23:09:50');
INSERT INTO `movimientos_inventario` (`id`, `producto_id`, `tipo`, `cantidad`, `stock_anterior`, `stock_nuevo`, `motivo`, `documento`, `usuario`, `fecha_movimiento`) VALUES (6,1,'ajuste',0,100,100,'Inventario físico: sin diferencias','AJ-0001','admin@admin.com','2026-09-22 23:09:50');
/*!40000 ALTER TABLE `movimientos_inventario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes_compra`
--

DROP TABLE IF EXISTS `ordenes_compra`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ordenes_compra` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `proveedor_id` int(11) NOT NULL,
  `fecha_orden` datetime DEFAULT current_timestamp(),
  `fecha_recepcion` datetime DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'pendiente',
  `total` decimal(10,2) NOT NULL DEFAULT 0.00,
  `usuario` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_ordenes_proveedor` (`proveedor_id`),
  KEY `idx_ordenes_estado` (`estado`),
  CONSTRAINT `fk_ordenes_proveedor` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes_compra`
--

LOCK TABLES `ordenes_compra` WRITE;
/*!40000 ALTER TABLE `ordenes_compra` DISABLE KEYS */;
INSERT INTO `ordenes_compra` (`id`, `proveedor_id`, `fecha_orden`, `fecha_recepcion`, `estado`, `total`, `usuario`) VALUES (1,3,'2026-09-02 23:09:50','2026-09-04 23:09:50','recibida',665.00,'admin@admin.com');
INSERT INTO `ordenes_compra` (`id`, `proveedor_id`, `fecha_orden`, `fecha_recepcion`, `estado`, `total`, `usuario`) VALUES (2,5,'2026-09-09 23:09:50','2026-09-11 23:09:50','recibida',830.00,'admin@admin.com');
INSERT INTO `ordenes_compra` (`id`, `proveedor_id`, `fecha_orden`, `fecha_recepcion`, `estado`, `total`, `usuario`) VALUES (3,3,'2026-09-22 23:09:50',NULL,'pendiente',480.00,'admin@admin.com');
/*!40000 ALTER TABLE `ordenes_compra` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `producto_etiqueta`
--

DROP TABLE IF EXISTS `producto_etiqueta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `producto_etiqueta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) NOT NULL,
  `etiqueta_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_producto_etiqueta` (`producto_id`,`etiqueta_id`),
  KEY `idx_pe_etiqueta` (`etiqueta_id`),
  CONSTRAINT `fk_pe_etiqueta` FOREIGN KEY (`etiqueta_id`) REFERENCES `etiquetas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pe_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `producto_etiqueta`
--

LOCK TABLES `producto_etiqueta` WRITE;
/*!40000 ALTER TABLE `producto_etiqueta` DISABLE KEYS */;
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (11,1,5);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (8,3,1);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (9,3,5);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (1,5,3);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (2,5,5);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (3,6,1);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (4,6,3);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (5,11,1);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (6,11,5);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (7,17,3);
INSERT INTO `producto_etiqueta` (`id`, `producto_id`, `etiqueta_id`) VALUES (10,24,4);
/*!40000 ALTER TABLE `producto_etiqueta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `productos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL DEFAULT 0.00,
  `precio_oferta` decimal(10,2) DEFAULT NULL,
  `cantidad` int(11) DEFAULT 0,
  `codigo_barras` varchar(50) DEFAULT NULL,
  `stock_minimo` int(11) DEFAULT 5,
  `id_categoria` int(11) DEFAULT NULL,
  `proveedor_id` int(11) DEFAULT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `destacado` tinyint(1) DEFAULT 0,
  `activo` tinyint(1) DEFAULT 1,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_productos_codigo_barras` (`codigo_barras`),
  KEY `proveedor_id` (`proveedor_id`),
  KEY `productos_ibfk_1` (`id_categoria`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`id_categoria`) REFERENCES `categorias` (`id_categoria`) ON DELETE SET NULL,
  CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (1,'Cuaderno A4 100 hojas','Cuaderno rayado tamaño A4',5.50,NULL,100,'7750000100001',5,2,1,NULL,1,1,'2026-09-15 20:48:49');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (2,'Lapicero Azul','Lapicero tinta azul',1.50,NULL,500,'7750000100002',5,2,1,NULL,0,1,'2026-09-15 20:48:49');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (3,'Libro Matemáticas 5to','Libro de texto escolar',45.00,39.90,30,'7750000100003',5,1,1,NULL,1,1,'2026-09-15 20:48:49');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (4,'Resma Papel A4','Resma 500 hojas',18.00,15.50,50,'7750000100004',5,3,2,NULL,0,1,'2026-09-15 20:48:49');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (5,'Vida de Don Bosco','Biografía completa de San Juan Bosco, fundador de los Salesianos.',45.00,NULL,25,'900100001',5,5,3,'900100001.svg',1,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (6,'Memorias del Oratorio de San Francisco de Sales','Obra autobiográfica de Don Bosco sobre el nacimiento de su obra.',55.00,49.90,15,'900100002',5,5,3,'900100002.svg',1,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (7,'El Sistema Preventivo de Don Bosco','El método educativo salesiano: razón, religión y amor.',38.00,NULL,20,'900100003',5,5,3,'900100003.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (8,'Cartas de Don Bosco','Selección de las cartas más significativas de San Juan Bosco.',42.00,NULL,18,'900100004',5,5,3,'900100004.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (9,'Don Bosco y los jóvenes','Testimonios y reflexiones sobre la pastoral juvenil salesiana.',36.00,NULL,22,'900100005',5,5,3,'900100005.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (10,'Novena a San Juan Bosco','Noveno devocional para pedir la intercesión de Don Bosco.',8.00,NULL,60,'900100006',5,5,3,'900100006.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (11,'Biblia Latinoamericana','Biblia Latinoamericana con introducciones y notas pastorales.',65.00,59.90,20,'900200001',5,6,3,'900200001.svg',1,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (12,'Biblia de Jerusalén','Edición de estudio de la Biblia de Jerusalén, tapa dura.',85.00,NULL,12,'900200002',5,6,3,'900200002.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (13,'Catecismo de la Iglesia Católica','Texto completo del Catecismo de la Iglesia Católica.',40.00,NULL,25,'900200003',5,6,3,'900200003.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (14,'Compendio del Catecismo','Versión resumida en preguntas y respuestas del Catecismo.',25.00,NULL,30,'900200004',5,6,3,'900200004.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (15,'Misal dominical','Misal para seguir la liturgia de la Santa Misa dominical.',30.00,NULL,28,'900200005',5,6,3,'900200005.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (16,'Devocionario católico','Oraciones y devociones para el uso diario del creyente.',18.00,NULL,40,'900200006',5,6,3,'900200006.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (17,'Estatua de Don Bosco 20 cm','Estatua de San Juan Bosco de 20 cm, resina pintada a mano.',55.00,NULL,20,'900300001',5,7,5,'900300001.svg',1,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (18,'Estatua del Sagrado Corazón de Jesús','Estatua del Sagrado Corazón de Jesús, 25 cm.',60.00,NULL,18,'900300002',5,7,5,'900300002.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (19,'Cuadro de la Última Cena','Cuadro enmarcado de la Última Cena, 30 x 20 cm.',45.00,NULL,15,'900300003',5,7,5,'900300003.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (20,'Imagen de la Virgen de Fátima 15 cm','Imagen de Nuestra Señora de Fátima de 15 cm.',40.00,NULL,22,'900300004',5,7,5,'900300004.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (21,'Estatua de San Francisco de Sales','Estatua de San Francisco de Sales, patrono de los salesianos.',50.00,NULL,14,'900300005',5,7,5,'900300005.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (22,'Estatua María Auxiliadora 15 cm','Estatua de María Auxiliadora de 15 cm, resina pintada.',45.00,NULL,30,'900400001',5,8,5,'900400001.svg',1,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (23,'Estatua María Auxiliadora 30 cm','Estatua de María Auxiliadora de 30 cm con base de madera.',85.00,79.90,18,'900400002',5,8,5,'900400002.svg',1,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (24,'Estatua María Auxiliadora 45 cm','Estatua grande de María Auxiliadora de 45 cm para capilla u hogar.',150.00,NULL,8,'900400003',5,8,5,'900400003.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (25,'Cuadro de María Auxiliadora','Cuadro enmarcado de María Auxiliadora, 30 x 20 cm.',40.00,NULL,16,'900400004',5,8,5,'900400004.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (26,'Virgen María Auxiliadora con corona 25 cm','Estatua de María Auxiliadora de 25 cm con corona dorada.',95.00,NULL,12,'900400005',5,8,5,'900400005.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (27,'Rosario de madera','Rosario de madera con cruz, resistente para el uso diario.',15.00,NULL,50,'900500001',5,9,5,'900500001.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (28,'Rosario de cristal María Auxiliadora','Rosario de cristal con medalla de María Auxiliadora.',25.00,NULL,35,'900500002',5,9,5,'900500002.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (29,'Rosario metálico con caja','Rosario metálico de lujo presentado en estuche.',30.00,NULL,25,'900500003',5,9,5,'900500003.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (30,'Escapulario de María Auxiliadora','Escapulario de María Auxiliadora con oración impresa.',10.00,NULL,70,'900500004',5,9,5,'900500004.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (31,'Pulsera de María Auxiliadora','Pulsera devocional con medalla de María Auxiliadora.',12.00,NULL,60,'900500005',5,9,5,'900500005.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (32,'Medalla de María Auxiliadora dorada','Medalla de María Auxiliadora dorada con cadena.',8.00,NULL,90,'900600001',5,10,5,'900600001.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (33,'Medalla de Don Bosco','Medalla de San Juan Bosco, acabado plateado.',8.00,NULL,80,'900600002',5,10,5,'900600002.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (34,'Crucifijo de pared 20 cm','Crucifijo de pared de madera y metal, 20 cm.',35.00,NULL,24,'900600003',5,10,5,'900600003.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (35,'Cruz de madera para colgar','Cruz de madera tallada para colgar en el hogar.',18.00,NULL,32,'900600004',5,10,5,'900600004.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (36,'Llavero de María Auxiliadora','Llavero con imagen de María Auxiliadora.',10.00,NULL,65,'900600005',5,10,5,'900600005.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (37,'Novenas a María Auxiliadora','Noveno para la fiesta de María Auxiliadora (24 de mayo).',8.00,NULL,75,'900700001',5,11,3,'900700001.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (38,'Estampitas de María Auxiliadora x20','Paquete de 20 estampitas de María Auxiliadora.',12.00,NULL,55,'900700002',5,11,3,'900700002.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (39,'Vela devocional a María Auxiliadora','Vela blanca decorada con la imagen de María Auxiliadora.',10.00,NULL,48,'900700003',5,11,3,'900700003.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (40,'Agua bendita (frasco 250 ml)','Frasco de agua bendita con tapa, 250 ml.',15.00,NULL,40,'900700004',5,11,3,'900700004.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (41,'Portarretrato con oración','Portarretrato con la oración a María Auxiliadora.',20.00,NULL,30,'900700005',5,11,3,'900700005.svg',0,1,'2026-09-24 22:13:30');
INSERT INTO `productos` (`id`, `nombre`, `descripcion`, `precio`, `precio_oferta`, `cantidad`, `codigo_barras`, `stock_minimo`, `id_categoria`, `proveedor_id`, `imagen`, `destacado`, `activo`, `fecha_creacion`) VALUES (42,'Incienso litúrgico','Incienso litúrgico aromático para uso en oración.',15.00,NULL,42,'900700006',5,11,3,'900700006.svg',0,1,'2026-09-24 22:13:30');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `proveedores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `empresa` varchar(150) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `contacto` varchar(50) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT 1,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` (`id`, `nombre`, `empresa`, `email`, `contacto`, `direccion`, `activo`, `fecha_registro`) VALUES (1,'Distribuidora Lima','DistLima SAC','ventas@distlima.com','999111222',NULL,1,'2026-09-15 20:48:49');
INSERT INTO `proveedores` (`id`, `nombre`, `empresa`, `email`, `contacto`, `direccion`, `activo`, `fecha_registro`) VALUES (2,'Papelera del Sur','PapelSur EIRL','contacto@papelsur.com','999333444',NULL,1,'2026-09-15 20:48:49');
INSERT INTO `proveedores` (`id`, `nombre`, `empresa`, `email`, `contacto`, `direccion`, `activo`, `fecha_registro`) VALUES (3,'Editorial Salesiana','Editorial Salesiana Perú','ventas@editorialsalesiana.org','987 111 222','Jr. Don Bosco 120, Lima',1,'2026-09-24 22:13:30');
INSERT INTO `proveedores` (`id`, `nombre`, `empresa`, `email`, `contacto`, `direccion`, `activo`, `fecha_registro`) VALUES (4,'Librería Salesiana','Librería Salesiana Don Bosco','pedidos@libreriasalesiana.com','985 222 333','Av. Don Bosco 123, Lima',1,'2026-09-24 22:13:30');
INSERT INTO `proveedores` (`id`, `nombre`, `empresa`, `email`, `contacto`, `direccion`, `activo`, `fecha_registro`) VALUES (5,'Artículos Religiosos Jerusalén','Jerusalén Import','ventas@religiososjerusalen.pe','983 444 555','Av. Abancay 456, Lima',1,'2026-09-24 22:13:30');
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudes_reposicion`
--

DROP TABLE IF EXISTS `solicitudes_reposicion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `solicitudes_reposicion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) NOT NULL,
  `bodega_id` int(11) DEFAULT NULL,
  `cantidad_solicitada` int(11) NOT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'pendiente',
  `solicitante` varchar(100) DEFAULT NULL,
  `fecha_solicitud` datetime DEFAULT current_timestamp(),
  `fecha_aprobacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_solicitudes_producto` (`producto_id`),
  KEY `idx_solicitudes_estado` (`estado`),
  KEY `fk_solicitudes_bodega` (`bodega_id`),
  CONSTRAINT `fk_solicitudes_bodega` FOREIGN KEY (`bodega_id`) REFERENCES `bodegas` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_solicitudes_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudes_reposicion`
--

LOCK TABLES `solicitudes_reposicion` WRITE;
/*!40000 ALTER TABLE `solicitudes_reposicion` DISABLE KEYS */;
INSERT INTO `solicitudes_reposicion` (`id`, `producto_id`, `bodega_id`, `cantidad_solicitada`, `estado`, `solicitante`, `fecha_solicitud`, `fecha_aprobacion`) VALUES (1,17,1,30,'pendiente','admin@admin.com','2026-09-22 23:18:24',NULL);
INSERT INTO `solicitudes_reposicion` (`id`, `producto_id`, `bodega_id`, `cantidad_solicitada`, `estado`, `solicitante`, `fecha_solicitud`, `fecha_aprobacion`) VALUES (2,24,1,20,'aprobada','admin@admin.com','2026-09-19 23:18:24','2026-09-20 23:18:24');
INSERT INTO `solicitudes_reposicion` (`id`, `producto_id`, `bodega_id`, `cantidad_solicitada`, `estado`, `solicitante`, `fecha_solicitud`, `fecha_aprobacion`) VALUES (3,11,2,15,'recibida','vendedor@libreria.com','2026-09-15 23:18:24','2026-09-17 23:18:24');
/*!40000 ALTER TABLE `solicitudes_reposicion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stock_bodegas`
--

DROP TABLE IF EXISTS `stock_bodegas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `stock_bodegas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `producto_id` int(11) NOT NULL,
  `bodega_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_stock_producto_bodega` (`producto_id`,`bodega_id`),
  KEY `idx_stock_bodega` (`bodega_id`),
  CONSTRAINT `fk_stock_bodega` FOREIGN KEY (`bodega_id`) REFERENCES `bodegas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_stock_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_stock_cantidad` CHECK (`cantidad` >= 0)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stock_bodegas`
--

LOCK TABLES `stock_bodegas` WRITE;
/*!40000 ALTER TABLE `stock_bodegas` DISABLE KEYS */;
INSERT INTO `stock_bodegas` (`id`, `producto_id`, `bodega_id`, `cantidad`) VALUES (1,1,1,60);
INSERT INTO `stock_bodegas` (`id`, `producto_id`, `bodega_id`, `cantidad`) VALUES (2,1,2,40);
INSERT INTO `stock_bodegas` (`id`, `producto_id`, `bodega_id`, `cantidad`) VALUES (3,3,1,20);
INSERT INTO `stock_bodegas` (`id`, `producto_id`, `bodega_id`, `cantidad`) VALUES (4,3,2,10);
INSERT INTO `stock_bodegas` (`id`, `producto_id`, `bodega_id`, `cantidad`) VALUES (5,5,1,18);
INSERT INTO `stock_bodegas` (`id`, `producto_id`, `bodega_id`, `cantidad`) VALUES (6,5,2,7);
INSERT INTO `stock_bodegas` (`id`, `producto_id`, `bodega_id`, `cantidad`) VALUES (7,6,1,15);
/*!40000 ALTER TABLE `stock_bodegas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidades_medida`
--

DROP TABLE IF EXISTS `unidades_medida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unidades_medida` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(15) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `abreviatura` varchar(10) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_unidad_codigo` (`codigo`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidades_medida`
--

LOCK TABLES `unidades_medida` WRITE;
/*!40000 ALTER TABLE `unidades_medida` DISABLE KEYS */;
INSERT INTO `unidades_medida` (`id`, `codigo`, `nombre`, `abreviatura`) VALUES (1,'UND','Unidad','UND');
INSERT INTO `unidades_medida` (`id`, `codigo`, `nombre`, `abreviatura`) VALUES (2,'CJA','Caja','CJA');
INSERT INTO `unidades_medida` (`id`, `codigo`, `nombre`, `abreviatura`) VALUES (3,'PAQ','Paquete','PAQ');
INSERT INTO `unidades_medida` (`id`, `codigo`, `nombre`, `abreviatura`) VALUES (4,'KG','Kilogramo','KG');
INSERT INTO `unidades_medida` (`id`, `codigo`, `nombre`, `abreviatura`) VALUES (5,'M','Metro','M');
/*!40000 ALTER TABLE `unidades_medida` ENABLE KEYS */;
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
  `rol` varchar(30) DEFAULT 'vendedor',
  `activo` tinyint(1) DEFAULT 1,
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
INSERT INTO `usuarios_sistema` (`id`, `nombres`, `apellidos`, `correo`, `clave`, `rol`, `activo`, `fecha_registro`) VALUES (1,'Admin','Sistema','admin@libreria.com','$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Nqz8f6uPO0q2','admin',1,'2026-09-15 20:48:49');
INSERT INTO `usuarios_sistema` (`id`, `nombres`, `apellidos`, `correo`, `clave`, `rol`, `activo`, `fecha_registro`) VALUES (2,'Admin','Principal','admin@admin.com','scrypt:32768:8:1$KRgSZLkb4fZvibOt$02522f77b1129862ec38713207c48819db5f91ff5a03fe794e1a802b9c1b0be294ed238ab86af18db0dc733a7e62c3889b55502918100ca4f450c9fa2e0b1c95','administrador',1,'2026-09-16 09:19:27');
/*!40000 ALTER TABLE `usuarios_sistema` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'inventario_db'
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

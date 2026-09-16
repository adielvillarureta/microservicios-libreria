# Genera imágenes SVG coherentes (ícono por categoría + nombre) para cada
# producto del catálogo, en Comercial/static/img/productos/<codigo_barras>.svg
#
# Uso:  py generar_imagenes_productos.py

import os
import sys
import math
import html

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from seed_productos import PRODUCTOS

DEST = os.path.abspath(os.path.join(BASE, "..", "Comercial", "static", "img", "productos"))
os.makedirs(DEST, exist_ok=True)

COLORES = {
    "Libros Salesianos": ("#7C3AED", "#4C1D95"),
    "Biblias y Catecismo": ("#B45309", "#78350F"),
    "Estatuas e imágenes": ("#0891B2", "#155E75"),
    "María Auxiliadora": ("#2563EB", "#1E3A8A"),
    "Rosarios y escapularios": ("#059669", "#065F46"),
    "Medallas y crucifijos": ("#CA8A04", "#854D0E"),
    "Artículos de devoción": ("#DC2626", "#7F1D1D"),
}


def icono(categoria):
    if categoria in ("Libros Salesianos", "Biblias y Catecismo"):
        return (
            '<g transform="translate(300,270)">'
            '<rect x="-115" y="-100" width="210" height="200" rx="18" fill="#ffffff" opacity="0.96"/>'
            '<rect x="-115" y="-100" width="48" height="200" rx="18" fill="#000000" opacity="0.13"/>'
            '<rect x="-5" y="-52" width="16" height="104" rx="4" fill="#B91C1C"/>'
            '<rect x="-40" y="-18" width="86" height="16" rx="4" fill="#B91C1C"/>'
            '</g>'
        )
    if categoria in ("Estatuas e imágenes", "María Auxiliadora"):
        halo = ""
        if categoria == "María Auxiliadora":
            halo = '<circle cx="0" cy="-78" r="66" fill="none" stroke="#FFD700" stroke-width="10"/>'
        return (
            '<g transform="translate(300,255)" fill="#ffffff">'
            f'{halo}'
            '<circle cx="0" cy="-42" r="40"/>'
            '<path d="M-64,148 L-44,-2 Q0,-30 44,-2 L64,148 Z"/>'
            '<rect x="-74" y="148" width="148" height="26" rx="8"/>'
            '</g>'
        )
    if categoria == "Rosarios y escapularios":
        beads = ""
        for i in range(12):
            a = math.radians(i * 30 - 90)
            beads += f'<circle cx="{round(98 * math.cos(a))}" cy="{round(98 * math.sin(a))}" r="12"/>'
        return (
            '<g transform="translate(300,255)" fill="#ffffff">'
            f'{beads}'
            '<rect x="-7" y="96" width="14" height="60" rx="4"/>'
            '<rect x="-30" y="118" width="60" height="14" rx="4"/>'
            '</g>'
        )
    if categoria == "Medallas y crucifijos":
        return (
            '<g transform="translate(300,255)">'
            '<path d="M-48,-118 L0,-52 L48,-118" fill="none" stroke="#ffffff" stroke-width="16" stroke-linejoin="round"/>'
            '<circle cx="0" cy="14" r="82" fill="#ffffff"/>'
            '<rect x="-10" y="-52" width="20" height="118" rx="6" fill="#B45309"/>'
            '<rect x="-42" y="-20" width="84" height="20" rx="6" fill="#B45309"/>'
            '</g>'
        )
    return (
        '<g transform="translate(300,270)">'
        '<rect x="-36" y="-52" width="72" height="168" rx="10" fill="#ffffff"/>'
        '<ellipse cx="0" cy="-80" rx="18" ry="30" fill="#FFD700"/>'
        '<ellipse cx="0" cy="-80" rx="8" ry="18" fill="#F97316"/>'
        '</g>'
    )


def envolver(texto, ancho=22, max_lineas=2):
    lineas, actual = [], ""
    for palabra in texto.split():
        if len(actual) + len(palabra) + 1 <= ancho:
            actual = (actual + " " + palabra).strip()
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        lineas[-1] = lineas[-1][: ancho - 1] + "…"
    return lineas


def svg_producto(categoria, nombre):
    c1, c2 = COLORES.get(categoria, ("#334155", "#0F172A"))
    lineas = envolver(nombre)
    tspans = "".join(
        f'<tspan x="300" dy="{0 if i == 0 else 38}">{html.escape(linea)}</tspan>'
        for i, linea in enumerate(lineas)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c1}"/>
      <stop offset="1" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="600" fill="url(#g)"/>
  <text x="300" y="150" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="24" font-weight="700" fill="#ffffff" opacity="0.85">{html.escape(categoria.upper())}</text>
  {icono(categoria)}
  <text x="300" y="420" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="28" font-weight="600" fill="#ffffff">{tspans}</text>
  <text x="300" y="560" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" font-size="19" fill="#ffffff" opacity="0.7">Librería Salesiana Don Bosco</text>
</svg>
'''


def main():
    generados = 0
    for producto in PRODUCTOS:
        categoria, nombre, codigo = producto[0], producto[1], producto[6]
        ruta = os.path.join(DEST, f"{codigo}.svg")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(svg_producto(categoria, nombre))
        generados += 1
    print(f"{generados} imágenes generadas en {DEST}")


if __name__ == "__main__":
    main()

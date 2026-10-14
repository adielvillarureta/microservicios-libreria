const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
if (s.indexOf('id="mapaRecojo"')===-1) {
  const anchor = '<a target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=Jr.+Santa+Rosa+299%2C+El+Tambo%2C+Huancayo" class="btn btn-sm btn-outline-primary mt-2 rounded-pill">';
  const idx=s.indexOf(anchor);
  const closeIdx=s.indexOf('</div>', idx);
  // insert map container before the closing div of infoRecojo
  const insertAt = closeIdx;
  const insert = '\n                            <div id="mapaRecojo" class="mt-2 rounded border" style="height: 170px; background:#eef2ff;"></div>\n';
  s=s.slice(0,insertAt)+insert+s.slice(insertAt);
}
// add init map on selecting recojo in JS
s=s.replace('            if (recojoInfo) recojoInfo.style.display = "block";\n            direccionDiv.style.display = "none";',
            '            if (recojoInfo) recojoInfo.style.display = "block";\n            direccionDiv.style.display = "none";\n            setTimeout(iniciarMapaRecojo, 120);');
// add map function before escapeHtml? insert before window.onload? choose near end of script by adding at function cargarCarrito end
const marker='    // Renderizar el carrito\n        renderizarCarrito();\n    }';
const fn=`var mapaRecojo = null;
    function iniciarMapaRecojo() {
        var el = document.getElementById('mapaRecojo');
        if (!el) return;
        if (mapaRecojo) { mapaRecojo.invalidateSize(); return; }
        mapaRecojo = L.map('mapaRecojo').setView([-12.045765, -75.214802], 16);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '' }).addTo(mapaRecojo);
        L.marker([-12.045765, -75.214802]).addTo(mapaRecojo).bindPopup('<strong>Librería Salesiana</strong><br>Jr. Santa Rosa N° 299, El Tambo, Huancayo').openPopup();
    }
`;
if (s.indexOf('function iniciarMapaRecojo')===-1) s=s.replace(marker, fn + '\n' + marker, 1);
fs.writeFileSync(p,s,'utf8');
console.log('done');
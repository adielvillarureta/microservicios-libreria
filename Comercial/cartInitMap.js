const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
if (!s.includes('inicializarMapaRecojoCart')) {
  const marker='renderizarCarrito();\n    }';
  const add='renderizarCarrito();\n    }\n    setTimeout(function(){ if (document.getElementById("mapaRecojo") && tipoEntregaSeleccionado === "recojo") iniciarMapaRecojo(); }, 200);';
  s=s.replace(marker, marker + '\n    ' + 'setTimeout(initCartStoreMap, 250);', 1);
  // define if missing
  if (!s.includes('function initCartStoreMap')) s += '\n    function initCartStoreMap() { if (document.getElementById("mapaRecojo") && typeof iniciarMapaRecojo === "function") iniciarMapaRecojo(); }\n';
}
fs.writeFileSync(p,s);
console.log('done');
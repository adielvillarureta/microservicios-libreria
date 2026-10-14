const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');

// Insert call in recojo branch if not already
const old='            if (recojoInfo) recojoInfo.style.display = "block";\n            direccionDiv.style.display = "none";';
const neu='            if (recojoInfo) recojoInfo.style.display = "block";\n            direccionDiv.style.display = "none";\n            setTimeout(function(){ if (document.getElementById("mapaRecojo") && typeof iniciarMapaRecojo === "function") iniciarMapaRecojo(); }, 150);';
if (s.includes(old) && !s.includes('setTimeout(function(){ if (document.getElementById("mapaRecojo")')) {
  s=s.replace(old,neu,1);
}

// Also call on initial cart if map container exists
if (!s.includes('initMapaRecojoCarritoInitial')) {
  const marker='renderizarCarrito();\n    }';
  const add='renderizarCarrito();\n    }\n    setTimeout(function initMapaRecojoCarritoInitial(){ if (document.getElementById("mapaRecojo") && typeof iniciarMapaRecojo === "function" && (tipoEntregaSeleccionado === "recojo")) iniciarMapaRecojo(); }, 300);';
  s=s.replace(marker, add, 1);
}
fs.writeFileSync(p,s,'utf8');
console.log('done');
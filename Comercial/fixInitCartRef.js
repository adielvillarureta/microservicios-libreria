const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
s=s.replace('setTimeout(initCartStoreMap, 250);','setTimeout(function(){ if (typeof iniciarMapaRecojo === "function" && document.getElementById("mapaRecojo") && tipoEntregaSeleccionado === "recojo") iniciarMapaRecojo(); }, 250);');
fs.writeFileSync(p,s,'utf8');
console.log('done');
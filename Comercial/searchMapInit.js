const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
const s=fs.readFileSync(p,'utf8');
console.log('has map init on selection:', s.includes('setTimeout(iniciarMapaRecojo'));
console.log('has init func:', s.includes('function iniciarMapaRecojo'));
// show relevant snippet
const i=s.indexOf('iniciarMapaRecojo');
console.log(s.slice(i-120, i+80));
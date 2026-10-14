const fs=require('fs');
const s=fs.readFileSync('C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html','utf8');
console.log('has init func:', s.includes('function iniciarMapaRecojo'));
console.log('has map div:', s.includes('id="mapaRecojo"'));
const i=s.indexOf('function iniciarMapaRecojo');
console.log(s.slice(Math.max(0,i-50), i+120));
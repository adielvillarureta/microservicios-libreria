const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
const inline = `setTimeout(function(){
  var container = document.getElementById("mapaRecojo");
  if (!container) return;
  if (!window._mapaRecojo) {
    window._mapaRecojo = L.map("mapaRecojo").setView([-12.045765, -75.214802], 16);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { attribution: "" }).addTo(window._mapaRecojo);
    L.marker([-12.045765, -75.214802]).addTo(window._mapaRecojo).bindPopup("<strong>Libreria Salesiana</strong><br>Jr. Santa Rosa N. 299, El Tambo, Huancayo").openPopup();
  } else {
    window._mapaRecojo.invalidateSize();
  }
}, 200);`;
// Replace any previous map timeout calls
s=s.replace(/setTimeout\(function\(\)\{\s*if \(typeof iniciarMapaRecojo[\s\S]*?\}, 250\);/g, inline);
s=s.replace(/setTimeout\(function\(\)\{\s*if \(document.getElementById\("mapaRecojo"\)[\s\S]*?\}, 250\);/g, inline);
// Add inline init to selection recojo branch even if our replacement missed
s=s.replace('            if (recojoInfo) recojoInfo.style.display = "block";\n            direccionDiv.style.display = "none";',
            '            if (recojoInfo) recojoInfo.style.display = "block";\n            direccionDiv.style.display = "none";\n' + inline, 1);
fs.writeFileSync(p,s,'utf8');
console.log('done');
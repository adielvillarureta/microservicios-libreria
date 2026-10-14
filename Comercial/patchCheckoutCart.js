const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
const rx=/\n[ \t]*if \(tipoEntregaSeleccionado === 'delivery'\) \{\n[\s\S]*?\n[ \t]*\} else \{\n[ \t]*direccionEntrega = '';\n[ \t]*\}\n/;
const neu = "\n        if (tipoEntregaSeleccionado === 'delivery') {\n            let direccion = (document.getElementById('direccion')?.value || '').trim();\n            direccionEntrega = direccion;\n            try { localStorage.setItem('direccionEntrega', direccion); } catch (e) { }\n        } else {\n            direccionEntrega = '';\n        }\n";
const changed = rx.test(s);
const ns = s.replace(rx, neu);
fs.writeFileSync(p, ns);
console.log('matched:', changed, 'changed:', s !== ns);
const fs=require('fs');
const html=fs.readFileSync('C:\\Users\\LABH\\Documents\\GitHub\\microservicios-libreria\\Comercial\\templates\\catalogo_cliente.html','utf8');
const m = html.match(/<script\b[^>]*>([\s\S]*?)<\/script>/g) || [];
const js = m.map(x=>x.replace(/^<script\b[^>]*>/,'').replace(/<\/script>$/,'')).join('\n');
fs.writeFileSync('C:\\Users\\LABH\\AppData\\Local\\Temp\\opencode\\catalogo.js', js);
console.log('count',m.length,'len',js.length);
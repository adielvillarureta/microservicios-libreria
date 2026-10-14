p='/app/templates/carrito.html'
s=open(p,encoding='utf-8').read()
start=s.find('<div id="direccionEntrega"')
end=s.find('<button class="btn btn-oro w-100 mt-2 py-2"')
assert start!=-1 and end!=-1
clean='''                        <div id="direccionEntrega" class="mt-3" style="display: none;">
                            <textarea id="direccion" class="form-control" rows="2"
                                placeholder="Calle, numero, urbanizacion, referencia"
                                oninput="try{localStorage.setItem('direccionEntrega', this.value);}catch(e){}; if(typeof actualizarLinkMapa==='function') actualizarLinkMapa(this.value);"></textarea>
                            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mt-1">
                                <small id="direccionAyuda" class="text-muted"></small>
                                <a id="btnVerEnMapa" href="#" target="_blank" rel="noopener" class="btn btn-sm btn-outline-secondary rounded-pill mt-1"><i class="fas fa-map-location-dot me-1"></i>Ver en mapa</a>
                            </div>
                    '''
s=s[:start]+clean+s[end:]
# add helper JS if missing
if 'function actualizarLinkMapa' not in s:
    marker='function escapeHtml(t) {'
    helper='''function actualizarLinkMapa(texto) {
        const link = document.getElementById('btnVerEnMapa');
        if (!link) return;
        const q = encodeURIComponent(texto || '');
        link.href = q ? 'https://www.google.com/maps/search/?api=1&query=' + q : '#';
    }
'''
    s=s.replace(marker, helper + marker, 1)
open(p,'w',encoding='utf-8').write(s)
print('done')
PY
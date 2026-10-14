import os, re
root='/app/templates'
miss=[]
for dirpath,_,fs in os.walk(root):
    for fn in fs:
        if fn.endswith('.html'):
            s=open(os.path.join(dirpath,fn),encoding='utf-8',errors='ignore').read()
            for m in re.finditer(r"<img[^>]*src\s*=\s*['\"]([^'\"]+)['\"]", s):
                u=m.group(1)
                if u.startswith('/') and not u.startswith('http') and '{{' not in u and '}' not in u:
                    u = u.split('?')[0]
                    staticpath = '/app/static' + u if u.startswith('/') else '/app/static/' + u
                    if not os.path.exists(staticpath):
                        miss.append((fn,u))
print('missing', len(miss))
for x in miss[:60]:
    print(x)
PY
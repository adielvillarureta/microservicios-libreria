import os, re
root='/app/templates'
for dp,_,fs in os.walk(root):
    for fn in fs:
        if fn.endswith('.html'):
            s=open(os.path.join(dp,fn),encoding='utf-8',errors='ignore').read()
            for m in re.finditer(r"<img[^>]*src\s*=\s*['\"]([^'\"]+)['\"]", s):
                u=m.group(1)
                if '{{' not in u and not u.startswith('http') and u.startswith('/'):
                    p='/app/static' + u.split('?')[0]
                    if not os.path.exists(p):
                        print('MISSING', fn, u)
print('done')
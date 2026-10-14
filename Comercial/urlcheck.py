import os,re
root='/app/templates'
urls=set()
for dp,_,fs in os.walk(root):
    for fn in fs:
        if fn.endswith('.html'):
            s=open(os.path.join(dp,fn),encoding='utf-8',errors='ignore').read()
            for m in re.finditer(r"https?://[^\s\"'<>]+",s):
                urls.add(m.group(0))
for u in sorted(urls):
    print(u)
print('count',len(urls))
PY
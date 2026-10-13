"""Beratercockpit: Netlify-Build aus hochgeladener ZIP.

Sucht im Repository alle ZIP-Dateien, nimmt die mit dem neuesten
Build-Stempel (meta cockpit-build in der index.html) und entpackt sie
in den Ordner "site", den Netlify veröffentlicht. Liegt keine ZIP vor,
werden index.html und Co. direkt aus dem Repository übernommen.
"""
import glob
import os
import re
import shutil
import sys
import zipfile

OUT = 'site'
FILES = ('index.html', 'apple-touch-icon.png', '_headers', '_redirects')


def stamp(path):
    try:
        with zipfile.ZipFile(path) as z:
            name = next((n for n in z.namelist() if n.split('/')[-1] == 'index.html'), None)
            if not name:
                return None
            head = z.read(name)[:6000].decode('utf-8', 'ignore')
            m = re.search(r'name="cockpit-build" content="([^"]+)"', head)
            return m.group(1) if m else '0000'
    except zipfile.BadZipFile:
        return None


shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT)
zips = [z for z in glob.glob('**/*.zip', recursive=True) if not z.startswith(OUT + os.sep)]
found = [(stamp(z), os.path.getsize(z), z) for z in zips]
found = [f for f in found if f[0]]
if found:
    st, _, best = max(found)
    print(f'Verwende {best} (Build {st}), {len(found)} ZIP-Datei(en) gefunden')
    with zipfile.ZipFile(best) as z:
        for n in z.namelist():
            base = n.split('/')[-1]
            if not base or base.startswith('.') or n.startswith('__MACOSX'):
                continue
            with open(os.path.join(OUT, base), 'wb') as fh:
                fh.write(z.read(n))
else:
    print('Keine ZIP gefunden, verwende Dateien aus dem Repository')
    for f in FILES:
        if os.path.exists(f):
            shutil.copy(f, os.path.join(OUT, f))

if not os.path.exists(os.path.join(OUT, 'index.html')):
    sys.exit('Fehler: Keine index.html gefunden. Bitte die Beratercockpit_Netlify.zip hochladen.')
print('Veröffentlicht:', ', '.join(sorted(os.listdir(OUT))))

#!/usr/bin/env python3
"""Build the public, self-contained Bor skill and ready-to-use platform exports."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/bor-brand'
PUBLIC = ROOT / 'public'

def archive(source, target, prefix):
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as out:
        for path in sorted(source.rglob('*')):
            if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.pyc':
                continue
            info = zipfile.ZipInfo(prefix + '/' + path.relative_to(source).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            out.writestr(info, path.read_bytes())

for path in (SKILL / 'assets').iterdir():
    if path.name == 'brand.json':
        continue
    shutil.copy2(path, PUBLIC / 'assets' / path.name)
shutil.copy2(SKILL / 'assets/brand.json', PUBLIC / 'brand.json')
shutil.copy2(SKILL / 'references/brand.typ', PUBLIC / 'brand.typ')
subprocess.run(['typst', 'compile', str(SKILL / 'references/brand.typ'), str(PUBLIC / 'brand.pdf')], check=True)
archive(SKILL, PUBLIC / 'bor-brand.zip', 'bor-brand')
for platform in ('web', 'android'):
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary)
        for profile in ('identity', 'devices'):
            subprocess.run([sys.executable, str(SKILL / 'scripts/brand.py'), 'export', '--platform', platform,
                            '--profile', profile, '--output', str(source / profile)], check=True)
        archive(source, PUBLIC / f'bor-{platform}.zip', f'bor-{platform}')
kit = json.loads((SKILL / 'assets/brand.json').read_text())
manifest = {'version': kit['version'], 'repository': kit['brand']['repository'], 'downloads': {}}
for name in ('bor-brand.zip', 'bor-web.zip', 'bor-android.zip'):
    path = PUBLIC / name
    manifest['downloads'][name] = {'url': f'https://brand.bybor.cc/{name}',
                                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
(PUBLIC / 'kit.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Built skill, web/Android exports, tokens and public documentation')

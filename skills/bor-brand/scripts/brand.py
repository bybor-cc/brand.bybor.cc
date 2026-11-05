#!/usr/bin/env python3
"""Export Bor resources, install the self-contained skill, or verify an export. Python stdlib only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from xml.etree import ElementTree as ET

SKILL = Path(__file__).resolve().parents[1]
ASSETS = SKILL / 'assets'
KIT = json.loads((ASSETS / 'brand.json').read_text())


def kebab(name):
    return re.sub(r'([A-Z])', lambda m: '-' + m[1].lower(), name)


def android_vector(filename, adaptive=False):
    tree = ET.parse(ASSETS / filename).getroot()
    if adaptive:
        artwork = list(tree)
        tree = ET.Element('svg', {'viewBox': '0 0 512 512'})
        ET.SubElement(tree, 'g', {'transform': 'translate(111 163) scale(.86)'}).extend(artwork)
    _, origin_y, width, height = tree.attrib['viewBox'].split()

    def node(element, inherited=None):
        attrs = dict(inherited or {})
        attrs.update(element.attrib)
        tag = element.tag.rsplit('}', 1)[-1]
        if tag == 'title':
            return ''
        if tag in ('svg', 'g'):
            style = {k: v for k, v in attrs.items() if k in ('fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin')}
            content = ''.join(node(child, style) for child in element)
            if 'transform' in element.attrib:
                x, y, scale = re.findall(r'-?\d*\.?\d+', element.attrib['transform'])
                return f'<group android:translateX="{x}" android:translateY="{y}" android:scaleX="{scale}" android:scaleY="{scale}">{content}</group>'
            return content
        if tag == 'circle':
            x, y, radius = map(float, (attrs['cx'], attrs['cy'], attrs['r']))
            data = f'M{x-radius},{y}a{radius},{radius} 0 1,0 {2*radius},0a{radius},{radius} 0 1,0 {-2*radius},0'
        elif tag == 'path':
            data = attrs['d']
        else:
            raise ValueError(f'Unsupported canonical SVG element: {tag}')
        values = {'pathData': data, 'fillColor': attrs.get('fill', '#000000').replace('none', '#00000000')}
        for svg_key, android_key in [('stroke', 'strokeColor'), ('stroke-width', 'strokeWidth'), ('stroke-linecap', 'strokeLineCap'), ('stroke-linejoin', 'strokeLineJoin')]:
            if svg_key in attrs:
                values[android_key] = attrs[svg_key]
        return '<path ' + ' '.join(f'android:{k}="{v}"' for k, v in values.items()) + '/>'

    content = node(tree)
    if float(origin_y):
        content = f'<group android:translateY="{-float(origin_y)}">{content}</group>'
    return f'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="{width}dp" android:height="{height}dp" android:viewportWidth="{width}" android:viewportHeight="{height}">{content}</vector>\n'


def export_web(stage, profile):
    for name in ('bybor-mark-light.svg', 'bybor-mark-dark.svg'):
        shutil.copy2(ASSETS / name, stage / name)
    css = '.bor-mark { display: block; width: 8rem; max-width: 100%; height: auto; }\n'
    if profile == 'devices':
        design = KIT['profiles']['devices']
        for name in ('geist.ttf', 'geist-license.txt'):
            shutil.copy2(ASSETS / name, stage / name)
        css += '@font-face { font-family: BorGeist; src: url("geist.ttf") format("truetype"); font-weight: 100 900; font-display: swap; }\n'
        css += '[data-bor-profile="devices"] { font-family: BorGeist, sans-serif; }\n'
        for theme, colors in design['colors'].items():
            css += f'[data-bor-profile="devices"][data-bor-theme="{theme}"] {{\n'
            css += ''.join(f'  --bor-{kebab(key)}: {value};\n' for key, value in colors.items())
            for category in ('radius', 'layout'):
                css += ''.join(f'  --bor-{category}-{kebab(key)}: {value}px;\n' for key, value in design[category].items())
            css += '  background: var(--bor-background); color: var(--bor-on-background);\n}\n'
        css += '.bor-surface { background: var(--bor-surface); color: var(--bor-on-surface); border: 1px solid var(--bor-outline-variant); border-radius: var(--bor-radius-medium); padding: var(--bor-layout-card-inset); }\n'
    (stage / 'bor-brand.css').write_text(css)
    (stage / 'example.html').write_text(f'''<!doctype html>
<html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bor integration example</title><link rel="stylesheet" href="bor-brand.css">
<body data-bor-profile="{profile}" data-bor-theme="light">
<!-- Choose the SVG for the actual background. Do not stretch the mark. -->
<img class="bor-mark" src="bybor-mark-light.svg" width="338" height="174" alt="Bor">
<p>Знак Bor. Подключите bor-brand.css и используйте нужный SVG.</p>
</body></html>
''')


def export_android(stage, profile, package):
    drawable = stage / 'res/drawable'
    drawable.mkdir(parents=True)
    for theme in ('light', 'dark'):
        (drawable / f'bor_mark_{theme}.xml').write_text(android_vector(f'bybor-mark-{theme}.svg'))
    (drawable / 'bor_launcher_foreground.xml').write_text(android_vector('bybor-mark-light.svg', adaptive=True))
    if profile != 'devices':
        return
    design = KIT['profiles']['devices']
    font = stage / 'res/font'
    font.mkdir()
    shutil.copy2(ASSETS / 'geist.ttf', font / 'bor_geist.ttf')
    shutil.copy2(ASSETS / 'geist-license.txt', stage / 'geist-license.txt')
    text = f'package {package}\n\nimport androidx.compose.ui.graphics.Color\nimport androidx.compose.ui.unit.dp\n\n// Opt-in Devices profile; not a mandatory Bor palette.\nobject BorDevicesTokens {{\n'
    for theme, colors in design['colors'].items():
        text += f'    object {theme.title()} {{\n'
        text += ''.join(f'        val {key} = Color(0xFF{value[1:]})\n' for key, value in colors.items())
        text += '    }\n'
    for category in ('radius', 'layout'):
        text += f'    object {category.title()} {{\n'
        text += ''.join(f'        val {key} = {value}.dp\n' for key, value in design[category].items())
        text += '    }\n'
    (stage / 'BorDevicesTokens.kt').write_text(text + '}\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(args):
    if args.output.is_symlink():
        raise ValueError("Export directory must not be a symlink")
    out = args.output.resolve()
    lock = out / 'bor-brand.lock.json'
    if lock.exists():
        previous = json.loads(lock.read_text())
        if (previous['platform'], previous['profile']) != (args.platform, args.profile):
            raise ValueError('Use a separate export directory for a different platform or profile')
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent, prefix='.bor-export-') as temporary:
        stage = Path(temporary)
        if args.platform == 'web':
            export_web(stage, args.profile)
        else:
            export_android(stage, args.profile, args.package)
        (stage / 'brand.json').write_text(json.dumps({
            'version': KIT['version'], 'brand': KIT['brand'],
            'profile': args.profile, 'design': KIT['profiles'][args.profile],
        }, ensure_ascii=False, indent=2) + '\n')
        manifest = {'kitVersion': KIT['version'], 'repository': KIT['brand']['repository'],
                    'platform': args.platform, 'profile': args.profile,
                    'sha256': {p.relative_to(stage).as_posix(): digest(p) for p in sorted(stage.rglob('*')) if p.is_file()}}
        (stage / 'bor-brand.lock.json').write_text(json.dumps(manifest, indent=2) + '\n')
        files = [p for p in stage.rglob('*') if p.is_file()]
        collisions = [p.relative_to(stage).as_posix() for p in files
                      if (out / p.relative_to(stage)).exists() and
                      ((out / p.relative_to(stage)).is_symlink() or not (out / p.relative_to(stage)).is_file() or
                       (out / p.relative_to(stage)).read_bytes() != p.read_bytes())]
        # Output is a dedicated kit directory. Symlinks must not escape it.
        if out.is_symlink() or any(p.is_symlink() for p in out.rglob('*')):
            raise ValueError('Export directory must not contain symlinks')
        if collisions and not args.force:
            raise ValueError('Existing files differ; choose another directory or use --force: ' + ', '.join(collisions))
        out.mkdir(parents=True, exist_ok=True)
        for path in files:
            target = out / path.relative_to(stage)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    print(f'Exported Bor {KIT["version"]}: {args.platform}/{args.profile} → {out}')


def check(args):
    root = args.output.resolve()
    manifest = json.loads((root / 'bor-brand.lock.json').read_text())
    for name, expected in manifest['sha256'].items():
        path = root / name
        if not path.resolve().is_relative_to(root) or not path.is_file() or digest(path) != expected:
            raise ValueError(f'Missing or modified export: {name}')
    print(f'Export verified: {len(manifest["sha256"])} files')


def install(args):
    target = args.dest.expanduser().absolute() / 'bor-brand'
    if target.exists():
        raise ValueError(f'Skill already exists: {target}. Preserve/remove it explicitly before updating.')
    if target.is_relative_to(SKILL):
        raise ValueError('Cannot install the skill inside itself')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    print(f'Installed {target}; available on the next Codex turn')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    cmd = commands.add_parser('export')
    cmd.add_argument('--platform', choices=['web', 'android'], required=True)
    cmd.add_argument('--profile', choices=['identity', 'devices'], default='identity')
    cmd.add_argument('--output', type=Path, required=True, help='Dedicated export directory, not the application root')
    cmd.add_argument('--package', default='bor.brand', help='Kotlin package for Android tokens')
    cmd.add_argument('--force', action='store_true', help='Replace conflicting files in this dedicated export directory')
    cmd.set_defaults(run=export)
    cmd = commands.add_parser('check')
    cmd.add_argument('--output', type=Path, required=True)
    cmd.set_defaults(run=check)
    cmd = commands.add_parser('install-skill')
    cmd.add_argument('--dest', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills')
    cmd.set_defaults(run=install)
    args = parser.parse_args()
    if hasattr(args, 'package') and not re.fullmatch(r'[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)*', args.package):
        parser.error('Invalid Kotlin package name')
    try:
        args.run(args)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()

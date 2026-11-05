import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/bor-brand/scripts/brand.py'

class KitTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def run_cli(self, *args, script=SCRIPT, success=True):
        result = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def export(self, platform='web', profile='identity'):
        output = self.root / f'{platform}-{profile}'
        self.run_cli('export', '--platform', platform, '--profile', profile, '--output', output)
        return output

    def test_identity_does_not_impose_devices_style(self):
        output = self.export()
        self.assertFalse((output / 'geist.ttf').exists())
        self.assertNotIn('Geist', (output / 'bor-brand.css').read_text())
        self.assertNotIn('devices', json.loads((output / 'brand.json').read_text())['design'])
        for theme in ('light', 'dark'):
            name = f'bybor-mark-{theme}.svg'
            self.assertEqual((output / name).read_bytes(), (ROOT / 'skills/bor-brand/assets' / name).read_bytes())
        self.run_cli('check', '--output', output)

    def test_devices_values_are_shared_between_platforms(self):
        web = self.export(profile='devices')
        android = self.export('android', 'devices')
        design = json.loads((web / 'brand.json').read_text())['design']
        kotlin = (android / 'BorDevicesTokens.kt').read_text()
        css = (web / 'bor-brand.css').read_text()
        for theme in design['colors'].values():
            for color in theme.values():
                self.assertIn(color, css)
                self.assertIn('0xFF' + color[1:], kotlin)
        self.assertEqual((web / 'geist.ttf').read_bytes(), (android / 'res/font/bor_geist.ttf').read_bytes())
        self.assertTrue((android / 'geist-license.txt').exists())
        self.run_cli('check', '--output', android)

    def test_update_refuses_edits_without_partial_writes(self):
        output = self.export()
        css = output / 'bor-brand.css'
        css.write_text('custom product styles')
        mark = output / 'bybor-mark-light.svg'
        previous = mark.read_bytes()
        self.run_cli('check', '--output', output, success=False)
        self.run_cli('export', '--platform', 'web', '--output', output, success=False)
        self.assertEqual(css.read_text(), 'custom product styles')
        self.assertEqual(mark.read_bytes(), previous)
        self.run_cli('export', '--platform', 'web', '--output', output, '--force')
        self.run_cli('check', '--output', output)

    def test_platforms_and_profiles_cannot_mix_in_one_directory(self):
        output = self.export()
        self.run_cli('export', '--platform', 'android', '--profile', 'devices', '--output', output, '--force', success=False)
        self.assertFalse((output / 'res').exists())

    def test_symlink_output_cannot_write_outside_export(self):
        outside = self.root / 'outside'
        outside.mkdir()
        target = self.root / 'export'
        target.symlink_to(outside, target_is_directory=True)
        self.run_cli('export', '--platform', 'web', '--output', target, success=False)
        self.assertEqual(list(outside.iterdir()), [])

    def test_android_mark_keeps_proportions_and_adaptive_safe_area(self):
        output = self.export('android')
        android = '{http://schemas.android.com/apk/res/android}'
        mark = ET.parse(output / 'res/drawable/bor_mark_light.xml').getroot()
        self.assertEqual(mark.attrib[android + 'viewportWidth'], '338')
        self.assertEqual(mark.attrib[android + 'viewportHeight'], '174')
        icon = ET.parse(output / 'res/drawable/bor_launcher_foreground.xml').getroot()
        group = icon.find('group')
        self.assertEqual(group.attrib[android + 'scaleX'], group.attrib[android + 'scaleY'])
        self.assertEqual(float(group.attrib[android + 'scaleX']), .86)
        self.assertEqual(len(list(icon.iter('path'))), 4)

    def test_downloaded_skill_is_self_contained(self):
        with zipfile.ZipFile(ROOT / 'public/bor-brand.zip') as archive:
            archive.extractall(self.root / 'unpacked')
        source_script = self.root / 'unpacked/bor-brand/scripts/brand.py'
        self.run_cli('install-skill', '--dest', self.root / 'installed', script=source_script)
        installed_script = self.root / 'installed/bor-brand/scripts/brand.py'
        output = self.root / 'exported'
        self.run_cli('export', '--platform', 'web', '--profile', 'devices', '--output', output, script=installed_script)
        self.run_cli('check', '--output', output, script=installed_script)
        self.run_cli('install-skill', '--dest', self.root / 'installed', script=source_script, success=False)

if __name__ == '__main__':
    unittest.main()

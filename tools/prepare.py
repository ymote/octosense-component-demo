#!/usr/bin/env python3
"""Prepare real GitHub attestation subjects from this immutable tag checkout."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.1.0'
WORKFLOW = '.github/workflows/publish.yml'


def run(hub, *args):
    result = subprocess.run([str(hub), *map(str, args)], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError((result.stderr + result.stdout).strip())
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hub', type=Path, required=True)
    args = parser.parse_args()
    identity = {'repository': os.environ['GITHUB_REPOSITORY'], 'repository-id': os.environ['PUBLISHER_REPOSITORY_ID'],
                'owner-id': os.environ['PUBLISHER_OWNER_ID'], 'workflow': WORKFLOW,
                'tag': os.environ['GITHUB_REF_NAME'], 'commit': os.environ['GITHUB_SHA']}
    assert identity['repository'] == 'ymote/octosense-component-demo'
    assert identity['tag'] == 'v' + VERSION
    flags = [value for key, value in identity.items() for value in ('--' + key, value)]
    build = ROOT / 'build'
    build.mkdir(exist_ok=False)
    components = {}
    for name in ('notes', 'hostcall'):
        directory = build / name
        directory.mkdir()
        wasm = ROOT / 'guest/target/wasm32-wasip2/release' / (name + '.wasm')
        subject = directory / 'octosense-component.json'
        receipt = run(args.hub, 'component-prepare', wasm, '--draft', ROOT / 'components' / (name + '.json'),
                      *flags, '--out', subject)
        (directory / 'prepare-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
        components[name] = json.loads(subject.read_text())['component']
    pins = [{'as': alias, 'id': components[name]['id'], 'version': VERSION, 'blake3': components[name]['wasm_blake3']}
            for name, alias in [('notes', 'md'), ('hostcall', 'bridge')]]
    for name in ('first', 'second'):
        directory = build / name
        bundle = directory / 'bundle'
        bundle.mkdir(parents=True)
        app_id = 'org.ymote.componentdemo.' + name
        label = 'Component Demo · ' + name.title()
        source = (ROOT / 'templates/main.splash').read_text().replace('{{label}}', label).replace('{{app_id}}', app_id)
        (bundle / 'main.splash').write_text(source)
        shutil.copy(ROOT / 'templates/icon.svg', bundle / 'icon.svg')
        # This must be an actual hidden native preview of this app, reviewed
        # before the tag is pushed. A missing screenshot stops publication.
        shutil.copy(ROOT / 'templates' / (name + '.png'), bundle / 'preview.png')
        (bundle / 'AGENT.md').write_text('Run ' + name + '.inspect only when the user asks. Use synthetic local data. No account or network requests.\n')
        (bundle / 'tools.json').write_text(json.dumps({'schema': 1, 'tools': [{
            'name': name + '.inspect', 'description': 'Exercise local shared components with synthetic data.',
            'implemented_by': 'app', 'risk': 'act', 'background': False, 'shareable': False, 'private_data': True,
            'input_schema': {'type': 'object', 'properties': {}, 'additionalProperties': False},
            'output_schema': {'type': 'object', 'properties': {'app': {'type': 'string'}, 'results': {'type': 'object'}},
                              'required': ['app', 'results'], 'additionalProperties': False}}]}, indent=2) + '\n')
        manifest = {'schema': 1, 'id': app_id, 'version': VERSION, 'name': label,
                    'integrity': {'bundle_blake3': '0' * 64}, 'capabilities': ['wasm', 'storage'],
                    'requires': ['wasm-shared-components-v1', 'script-tools-v1', 'host-api-v1'],
                    'host_api': {'required': {'app_tools.dispatch': 1, 'runtime.describe': 1}},
                    'components': pins,
                    'agent': {'instructions': 'AGENT.md', 'background': False, 'profile': 'workspace-write-never-ask',
                              'model': {'needs': ['tool_calling'], 'local_only': False}, 'tools': []}}
        (bundle / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        listing = {'schema': 1, 'description': 'Synthetic shared-component acceptance app. No personal data or account connection.',
                   'category': 'utilities', 'screenshots': ['preview.png'], 'icon': 'icon.svg',
                   'platforms': ['macos', 'linux', 'android'], 'age_rating': 'all',
                   'publisher': components['notes']['publisher']}
        (bundle / 'listing.json').write_text(json.dumps(listing, indent=2) + '\n')
        receipt = run(args.hub, 'publisher-prepare', bundle, *flags, '--out', directory / 'octosense-app-manifest.json')
        (directory / 'prepare-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()

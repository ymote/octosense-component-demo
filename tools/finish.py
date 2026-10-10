#!/usr/bin/env python3
"""Attach and verify real Actions proofs; no mock verifier or signing key."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def run(hub, *args):
    result = subprocess.run([str(hub), *map(str, args)], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError((result.stderr + result.stdout).strip())
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hub', type=Path, required=True)
    args = parser.parse_args()
    build = ROOT / 'build'
    release = build / 'release'
    release.mkdir(exist_ok=False)
    receipts = {}
    for name in ('notes', 'hostcall'):
        wasm = ROOT / 'guest/target/wasm32-wasip2/release' / (name + '.wasm')
        packed = build / (name + '-release')
        receipts[name] = run(args.hub, 'component-pack', build / name / 'octosense-component.json',
                             '--wasm', wasm, '--attestation', os.environ[name.upper() + '_PROOF'], '--out', packed)
        for path in packed.iterdir():
            shutil.copy(path, release / path.name)
    for name in ('first', 'second'):
        bundle = build / name / 'bundle'
        run(args.hub, 'publisher-attach', bundle, '--attestation', os.environ[name.upper() + '_PROOF'])
        # Pins are verified against the catalog by the admin's catalog-prepare
        # step. Without a catalog, this pack records the unresolved-pin warning.
        receipts[name] = run(args.hub, 'publisher-pack', bundle, '--out', release / ('org.ymote.componentdemo.' + name + '-0.1.0.bundle.pack.json'))
    # Paths returned by the CLI belong to a transient runner; keep public
    # evidence limited to identities/digests, not absolute runner locations.
    for receipt in receipts.values():
        for field in ('release', 'wasm'):
            if field in receipt:
                receipt[field] = Path(receipt[field]).name
    (release / 'publisher-receipt.json').write_text(json.dumps({'schema': 1, 'artifacts': receipts,
        'catalog_published': False, 'not_verified': ['App Hub installation', 'native execution']}, indent=2) + '\n')


if __name__ == '__main__':
    main()

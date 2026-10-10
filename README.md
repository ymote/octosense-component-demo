# Shared component acceptance

English | [简体中文](README.zh-CN.md)

Two OctoScript apps use the same pinned Rust WebAssembly components. Each app
gets its own retained counter and private note, while the component bytes are
stored once. A second component calls the real host's `runtime.describe` API.
All input is synthetic. No personal account, API key, model, or separate
publisher signing key is needed.

The first app declares an empty capability list. The second declares `wasm`
and `storage`. Both must work through the same host APIs and shared component
bytes: these manifest fields describe the app, and do not gate ordinary APIs.

This is an acceptance fixture, not a general note editor. `SOURCE.json` records
the exact upstream source and verifier revisions. The Rust source and lockfile
are in `guest/`; `pulldown-cmark` supplies the Markdown renderer.

## Release and review

The release workflow builds both components with Rust 1.97.1, derives their
WIT import/export inventories and exact BLAKE3 digests, then pins those digests
in two app manifests. Four GitHub Actions attestations bind the immutable tag,
repository numeric identity, workflow, commit, and subject bytes. The pinned
App Hub CLI verifies each real proof before writing release files.

Before pushing a release tag, capture and review `templates/first.png` and
`templates/second.png` in a hidden native Makepad window using the exact
template. Missing screenshots stop preparation. Never substitute unrelated
screenshots. The normal tag is `v0.1.0` and every later release needs a new
version; existing release bytes must remain immutable.

The publisher release has two `*.component.json` / `*.wasm` pairs and two
`*.bundle.pack.json` consumer packs. Open an App Hub submission issue with the
repository, immutable tag and commit, and release files. Component pins in a
pack are unresolved until checked against its authenticated catalog; the
publisher receipt does not claim catalog or runtime acceptance.

An App Hub admin reviews all files, prepares a candidate containing both
components and apps against the current authenticated catalog, and runs the
existing catalog workflow with `dry_run: true`. Its real signed envelope can
be installed from an isolated local mirror without adding test apps to the
public store. A dry run still requires a reviewed candidate commit on App Hub
main and the protected admin environment. A fake or test verifier cannot
replace either publisher provenance or the admin catalog proof.

## Runtime acceptance

Use a clean build with `wasm-shared-components-v1` and a new app-data directory.
Install both apps from the verified local mirror using the normal store.
Never switch the production acceptance to the legacy catalog channel.

1. Run `first.inspect` / `second.inspect` in the first app, then the second. The result
   exposes each unmodified host reply for independent inspection.
2. Each app's first two counters must be 1 and 2. Calling again must yield
   3 and 4 in that app, without affecting the other app.
3. Each first `before_write` must fail because `note.html` does not yet exist.
   Each `read_back` must contain its own app label.
4. Markdown must render correctly. `wasm.functions` must list both `md.*`
   and `bridge.call` with the exact shared component pins.
5. `bridge.call` must reach `runtime.describe` through the normal host
   dispatcher; the descriptor must identify the implemented host API.
6. The installed `.components` directory must hold only one read-only file
   per component digest despite having two apps.

First validate desktop in hidden Makepad windows. Test an assigned Android
phone last, using a fresh `dev.makepad.octosense.hostapilab.*` package and
synthetic app-data only. Never replace the user's Home package. The existing
OctoSense `wasm-phone-smoke` harness tests the core-module ABI and cannot by
itself establish this shared-component publishing flow.

No release, catalog proof, screenshot or runtime acceptance has been completed
merely by preparing this source. Record measured results with source, runtime,
APK and artifact digests separately.

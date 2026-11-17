#!/usr/bin/env bash
# End-to-end test on synthetic audio with known ground truth. Usage: tests/run_test.sh [workdir]
set -euo pipefail
cd "$(dirname "$0")/.."
W="${1:-$(mktemp -d)}"
python3 tests/make_test_audio.py "$W/audio"
rm -rf "$W/data"
python3 -m holotype_ingest --root "$W/data" index "$W/audio/ref"
python3 -m holotype_ingest --root "$W/data" scan "$W/audio/new/A vocal version.wav" "$W/audio/new/A vinyl +6pct.wav" "$W/audio/new/D unknown riddim.wav" "$W/audio/new/D vocal version.wav"
python3 -m holotype_ingest --root "$W/data" scan --set "$W/audio/set/pirate set.wav"
python3 -m holotype_ingest --root "$W/data" review
python3 -m holotype_ingest --root "$W/data" verify
python3 tests/check.py "$W/data"

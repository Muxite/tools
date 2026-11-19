#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
export COCKPIT_STAGE=fixture GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL=/dev/null
dir=run/${COCKPIT_RUN:?}/artifacts
repo=$dir/fixture-repo
fixtures=$PWD/demo/fixtures

pace() {
    local seconds
    seconds=$(jq -n --argjson seconds "$1" --argjson speed "${COCKPIT_SPEED:-1}" '$seconds / $speed')
    sleep "$seconds"
}

prepare() {
    if [[ ! -f $dir/stock-revision.txt ]]; then
        if [[ ! -d $repo/.git ]]; then
            git init -q --initial-branch=stock "$repo"
        fi
        if ! git -C "$repo" rev-parse --verify HEAD >/dev/null 2>&1; then
            python3 - "$repo" "$fixtures/stock.json" <<'PY'
import json
import sys
from pathlib import Path

for name, content in json.loads(Path(sys.argv[2]).read_text()).items():
    path = Path(sys.argv[1]) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
PY
            git -C "$repo" add runtime
            GIT_AUTHOR_DATE=2024-01-01T00:00:00Z GIT_COMMITTER_DATE=2024-01-01T00:00:00Z \
                git -C "$repo" -c user.name=Fixture -c user.email=fixture@example.invalid commit -qm stock
        fi
        for patch in "$fixtures"/patches/*.patch; do
            capsule=${patch##*/}
            capsule=${capsule%.patch}
            git -C "$repo" restore --staged --worktree -- runtime
            git -C "$repo" apply "$patch"
            git -C "$repo" -c color.ui=always diff --no-ext-diff > "$dir/$capsule.diff"
        done
        git -C "$repo" restore --staged --worktree -- runtime
        git -C "$repo" rev-parse HEAD > "$dir/stock-revision.txt"
    fi
    printf '[fixture] stock source %s\n' "$(cat "$dir/stock-revision.txt")"
    jq -r '.task, .baseline, .acceptance' "$fixtures/contract.json"
    jq -r '.finding' "$fixtures/prior.json"
    pace 1
    bin/ev plan ok --cc requirements_capsule --ref demo/fixtures/contract.json
    bin/ev note ok --cc methodology_capsule --ref demo/fixtures/ontology.json
    bin/ev note ok --cc evidence_collector --ref demo/fixtures/prior.json
    bin/ev note ok --ref "$dir/stock-revision.txt"
    for patch in "$fixtures"/patches/*.patch; do
        capsule=${patch##*/}
        capsule=${capsule%.patch}
        bin/ev note ok --cc "$capsule" --ref "$dir/$capsule.diff" \
            --data '{"diff_stat":"+1/−1","role":"fixture catalog"}'
    done
}

case "${1:?}" in
    stock) prepare ;;
    cache)
        patch=$fixtures/patches/expert_weight_cache.patch
        if ! git -C "$repo" apply --reverse --check "$patch" 2>/dev/null; then
            git -C "$repo" apply "$patch"
        fi
        git -C "$repo" diff --stat
        git -C "$repo" -c color.ui=always diff --no-ext-diff > "$dir/cache-applied.diff"
        pace 1
        bin/ev cc_apply ok --cc expert_weight_cache --ref "$dir/cache-applied.diff" \
            --data '{"diff_stat":"+1/−1","component":"weights","subcomponent":"expert residency"}'
        ;;
    verify)
        git -C "$repo" diff --check
        git -C "$repo" apply --reverse --check "$fixtures/patches/expert_weight_cache.patch"
        pace 1
        printf '%s\n' '[fixture] source and patch checks passed'
        bin/ev verify ok --cc expert_weight_cache --ref "$dir/cache-applied.diff"
        ;;
    build)
        while IFS= read -r line; do printf '%s\n' "$line"; pace 0.5; done < "$fixtures/build.log"
        jq -r '.digest' "$fixtures/image.json"
        bin/ev build ok --cc image_builder --ref demo/fixtures/image.json
        ;;
    activate)
        pace 1
        jq -er 'select(.ready).marker' "$fixtures/acceptance.json"
        bin/ev activate ok --cc expert_weight_cache --ref demo/fixtures/acceptance.json \
            --data '{"marker":"expert_weight_cache=active"}'
        ;;
    abba)
        printf '%s\n' '[fixture] paired laboratory comparison, one model on one machine'
        pace 3
        jq -r '.samples[] | "arm=\(.arm) ttft_ms=\(.ttft_ms) native_prefill_ms=\(.native_prefill_ms) decode_tps=\(.decode_tps) memory_mib=\(.memory_mib)"' "$fixtures/abba.json"
        ;;
    *) printf 'Unknown fixture action %s\n' "$1" >&2; exit 2 ;;
esac

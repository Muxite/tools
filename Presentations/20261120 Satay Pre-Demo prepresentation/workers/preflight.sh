#!/bin/bash
# Machine preflight for timed llama.cpp runs. Read-only. Prints a JSON receipt to stdout; exit 0 = no blocker, 1 = blocker(s).
# usage: preflight.sh [--bin DIR] [--model GGUF] [--min-avail-gib N] [--max-load X] > receipt.json
BIN=""; MODEL=""; MIN_AVAIL=16; MAX_LOAD=1.0
while [ $# -gt 0 ]; do case "$1" in --bin) BIN=$2; shift 2;; --model) MODEL=$2; shift 2;; --min-avail-gib) MIN_AVAIL=$2; shift 2;; --max-load) MAX_LOAD=$2; shift 2;; *) shift;; esac; done
blockers=(); warns=()
j() { python3 -c 'import json,sys;print(json.dumps(sys.argv[1]))' "$1"; }
mem_kb() { awk -v k="$1" '$1==k":"{print $2}' /proc/meminfo; }
avail_gib=$(awk -v a="$(mem_kb MemAvailable)" 'BEGIN{printf "%.1f",a/1048576}')
total_gib=$(awk -v a="$(mem_kb MemTotal)" 'BEGIN{printf "%.1f",a/1048576}')
swap_used_mib=$(awk -v t="$(mem_kb SwapTotal)" -v f="$(mem_kb SwapFree)" 'BEGIN{printf "%d",(t-f)/1024}')
load1=$(cut -d' ' -f1 /proc/loadavg)
awk -v a="$avail_gib" -v m="$MIN_AVAIL" 'BEGIN{exit !(a<m)}' && blockers+=("MemAvailable ${avail_gib} GiB below ${MIN_AVAIL} GiB guard")
awk -v l="$load1" -v m="$MAX_LOAD" 'BEGIN{exit !(l>m)}' && blockers+=("load average ${load1} above ${MAX_LOAD}: machine not quiet")
[ "$swap_used_mib" -gt 256 ] && warns+=("swap in use ${swap_used_mib} MiB: page-cache and swap state will add noise")
# busy processes (excluding this shell): anything over 5% CPU right now
busy=$(ps -eo pid,pcpu,comm --sort=-pcpu | awk 'NR>1 && $2>5 {printf "%s(%s%%) ",$3,$2}')
[ -n "$busy" ] && blockers+=("busy processes: $busy")
# other benchmark-ish processes
others=$(pgrep -a -x -f "llama-server|llama-cli|llama-bench|llama-completion" 2>/dev/null | head -3 | tr '\n' ';')
[ -z "$others" ] && others=$(pgrep -x "llama-server|llama-cli|llama-bench|llama-completion" | tr '\n' ' ')
[ -n "$others" ] && blockers+=("llama processes running: $others")
# cpu freq/governor
gov=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo unknown)
curf=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null || echo 0)
maxf=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null || echo 0)
[ "$gov" != "performance" ] && warns+=("cpu governor is '$gov' (not performance); clocks ramp, expect spread")
# temperature
tmax=$(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | sort -n | tail -1); tmax=${tmax:-0}
[ "$tmax" -gt 75000 ] && warns+=("hottest thermal zone $((tmax/1000))C; throttling risk")
# cgroup limit visible to this shell
cg=$(cat /sys/fs/cgroup/memory.max 2>/dev/null || cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null || echo unknown)
# gpu
gpu=$(nvidia-smi --query-gpu=name,driver_version,clocks.sm,clocks.max.sm --format=csv,noheader 2>/dev/null | head -1)
[ -z "$gpu" ] && gpu=$(nvidia-smi 2>/dev/null | sed -n 's/.*\(Orin\|GB10\|Blackwell\).*/\1/p' | head -1)
# disk free where the model lives
dfree=""; [ -n "$MODEL" ] && dfree=$(df -BG --output=avail "$(dirname "$MODEL")" 2>/dev/null | tail -1 | tr -dc 0-9)
# effective load mode on this machine (uses the real binary, small model not required: --help is not enough, so only if a model is given)
lm=""; lazy=""
if [ -n "$BIN" ] && [ -n "$MODEL" ] && [ -x "$BIN/llama-server" ]; then
  tmp=$(mktemp); LD_LIBRARY_PATH="$BIN" timeout 120 "$BIN/llama-server" -m "$MODEL" --port 18999 -c 512 -ngl 0 -lv 4 > "$tmp" 2>&1 &
  sp=$!; for i in $(seq 1 100); do curl -sf http://127.0.0.1:18999/health >/dev/null 2>&1 && break; kill -0 $sp 2>/dev/null || break; sleep 1; done
  kill $sp 2>/dev/null; wait $sp 2>/dev/null
  lm=$(sed -n 's/.*load_mode = \([a-z+]*\).*/\1/p' "$tmp" | head -1)
  [ -z "$lm" ] && warns+=("could not read effective load_mode from the log (needs -lv 4)")
  [ "$lm" = "none" ] && warns+=("effective load_mode is 'none': weights are not mmap-backed; mmap-dependent CCs will be inactive unless -lm mmap is set")
  rm -f "$tmp"
fi
tools=""; for t in tmux jq asciinema python3 git docker; do command -v $t >/dev/null 2>&1 && tools="$tools$t " || warns+=("missing tool: $t"); done
sudo -n true 2>/dev/null && sudo_ok=true || sudo_ok=false
[ "$sudo_ok" = false ] && warns+=("no passwordless sudo: cannot lock clocks or drop caches from scripts")
python3 - "$@" <<PY
import json,sys,datetime,socket
b=[x for x in """$(printf '%s\n' "${blockers[@]}")""".split("\n") if x]
w=[x for x in """$(printf '%s\n' "${warns[@]}")""".split("\n") if x]
print(json.dumps({"schema":"preflight/1","host":socket.gethostname(),"at":datetime.datetime.utcnow().isoformat()+"Z",
 "mem_total_gib":$total_gib,"mem_available_gib":$avail_gib,"swap_used_mib":$swap_used_mib,"load1":$load1,
 "cpu_governor":"$gov","cpu_cur_khz":int("${curf:-0}"),"cpu_max_khz":int("${maxf:-0}"),"hottest_zone_mc":int("${tmax:-0}"),
 "cgroup_memory_max":"$cg","gpu":"$gpu","model_dir_free_gib":"${dfree}","effective_load_mode":"$lm",
 "tools_present":"""$tools""".split(),"passwordless_sudo":"$sudo_ok"=="true",
 "blockers":b,"warnings":w,"quiet":len(b)==0},indent=1))
PY
[ ${#blockers[@]} -eq 0 ]

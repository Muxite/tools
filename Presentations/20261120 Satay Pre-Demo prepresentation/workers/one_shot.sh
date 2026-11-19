#!/bin/bash
# usage: one_shot.sh <bindir> <outprefix> <port> [server args...]   (env vars pass through)
# Starts llama-server, sends one greedy request, saves JSON + server log, stops server.
set -u
BIN="$1"; OUT="$2"; PORT="$3"; shift 3
export LD_LIBRARY_PATH="$BIN"
M=${MODEL:-$HOME/models/campaign/gguf/granite-3.1-1b-a400m-instruct-Q8_0.gguf}
"$BIN/llama-server" -m "$M" --port "$PORT" -c 2048 -np 1 --temp 0 --seed 1 --no-cache-prompt "$@" > "$OUT.server.log" 2>&1 &
SP=$!
for i in $(seq 1 120); do
  curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break
  kill -0 $SP 2>/dev/null || { echo "server died"; tail -5 "$OUT.server.log"; exit 2; }
  sleep 1
done
P='Write a short note about mixture of experts models and why memory bandwidth matters. Then list three facts.'
curl -s "http://127.0.0.1:$PORT/completion" -d "{\"prompt\":\"$P\",\"n_predict\":48,\"temperature\":0,\"cache_prompt\":false,\"return_tokens\":true}" > "$OUT.json"
kill $SP 2>/dev/null; wait $SP 2>/dev/null
jq -c '{tokens:(.tokens|tostring|.[0:80]), stop:.stop_type, prompt_ms:.timings.prompt_ms, predicted_ms:.timings.predicted_ms, n:.timings.predicted_n}' "$OUT.json"
jq -c '.tokens' "$OUT.json" | sha256sum | cut -c1-16
grep -m3 -E "expert_fill|expert_prefetch" "$OUT.server.log" || echo "(no expert_fill/prefetch marker)"

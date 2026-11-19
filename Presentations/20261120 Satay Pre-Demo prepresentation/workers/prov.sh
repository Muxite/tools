#!/bin/bash
# Provenance of stock llama.cpp features relevant to the demo (upstream history, pin 9048bad8)
cd ~/predemo/history/llama.cpp
PIN=9048bad8d6e3a0f9f1726e238e451181c7e02613
first_add() { # path
  git log $PIN --diff-filter=A --follow --reverse --format="%h %cs %s" -- "$1" 2>/dev/null | head -1
}
echo "## files: first commit that added the path"
for p in src/llama-moe-cache.cpp src/llama-moe-cache.h docs/moe-cache.md scripts/moe-cache-tune.py src/models/deepseek41.cpp src/llama-expert-fill.h; do
  printf '%-34s ' "$p"; r=$(first_add "$p"); echo "${r:-NOT IN UPSTREAM HISTORY}"
done
echo
echo "## symbols: first commit whose diff adds the string (restricted to a file to keep it cheap)"
sym() { # symbol path
  printf '%-40s %-26s ' "$1" "$2"
  r=$(git log $PIN --reverse -S"$1" --format="%h %cs %s" -- "$2" 2>/dev/null | head -1)
  echo "${r:-not found}"
}
sym "moe_cache_mib"            common/arg.cpp
sym "n_cpu_moe"                common/arg.cpp
sym "override-tensor"          common/arg.cpp
sym "LLAMA_ARG_LAZY_MODE"      common/arg.cpp
sym "load-mode"                common/arg.cpp
sym "fit-target"               common/arg.cpp
sym "ggml_backend_sched_set_eval_callback" ggml/include/ggml-backend.h
sym "copy_experts"             src/llama-context.cpp
sym "sched_copy_experts"       src/llama-context.cpp
sym "LLM_ARCH_DEEPSEEK41"      src/llama-arch.h
sym "ggml_backend_sched_set_cpu_callback" ggml/include/ggml-backend.h
sym "LLAMA_EXPERT_FILL"        src/llama-context.cpp
sym "expert_fill"              src/llama-context.cpp
echo
echo "## recent upstream commits on the MoE cache path (context: how active/new this is)"
git log $PIN -8 --format="%h %cs %s" -- src/llama-moe-cache.cpp docs/moe-cache.md 2>/dev/null
echo
echo "## copy-weights callback signature in the pinned header"
git show $PIN:ggml/include/ggml-backend.h 2>/dev/null | grep -n -i "callback while copying\|copy_weights\|sched_set_.*callback\|typedef.*callback" | head -8

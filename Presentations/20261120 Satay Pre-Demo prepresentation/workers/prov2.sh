cd ~/predemo/history/llama.cpp
PIN=9048bad8d6e3a0f9f1726e238e451181c7e02613
sym() { printf "%-34s %-28s " "$1" "$2"; r=$(git log $PIN --reverse -S"$1" --format="%h %cs %s" -- "$2" 2>/dev/null | head -1); echo "${r:-not found}"; }
sym "moe-cache-mib"      common/arg.cpp
sym "n-cpu-moe"          common/arg.cpp
sym "cpu-moe"            common/arg.cpp
sym "sched_copy_experts" src/llama-context.cpp
sym "callback while copying input weights" ggml/include/ggml-backend.h
sym "ggml_backend_sched_set_cpu_callback"  ggml/include/ggml-backend.h
sym "LLAMA_EXPERT_FILL"  src/llama-context.cpp
sym "expert_fill"        src/llama-context.cpp
echo "## latest upstream commits on moe-cache path"; git log $PIN -8 --format="%h %cs %s" -- src/llama-moe-cache.cpp docs/moe-cache.md
echo "## callback typedefs at pin"; git show $PIN:ggml/include/ggml-backend.h | grep -n -i "callback" | head -10
echo PROV2-DONE

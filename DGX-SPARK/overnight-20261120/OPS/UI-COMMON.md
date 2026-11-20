# UI agents: common brief (read fully)

**Goal.** At a demo today, the JiuwenSwarm web UI must show how builder Capability Capsules (CCs) let JiuwenSwarm improve llama.cpp on DeepSeek V4.1 Flash on a DGX Spark, measured against the Strata engine. Presentation quality matters a lot: the owner says a really good UI and presentation go a long way. Read ~/predemo-spark/BRIEF.md (Part A) and ~/predemo-spark/OPS/DIRECTIVE-2.md for context.

**Code.**
- The app is the JiuwenSwarm web frontend: React 18, zustand, Vite. It lives at jiuwenswarm/channels/web/frontend in YOUR worktree (path in your role file). There is no router; App.tsx uses activeNav.
- The new feature is src/features/factoryRuns/. Its backend is jiuwenswarm/gateway/channel_manager/web/factory_http.py (/api/factory/...).
- Read the latest commits on branch demo/cc-star-ui-20261120 to see what exists.

**Real data to design against (read-only):**
- The factory export bundles in ~/software-factory-spark-20261113/exports/factory-loop-v1/*.
- The homes the backend lists.
- The five star capsules in jiuwenswarm/factory/ccs/{observability_event_recorder,expert_weight_cache,weight_placement_planner,expert_demand_predictor,batch_layout_mapper}. Each has cc.yaml, ONTOLOGY.yaml, GUIDE.md, METHOD.md, SOURCE-MAP.md, VALIDATION.md, samples/, helpers/, tests/, run.py (verifier) and sealed digests.
- The contract star-deepseek-v1 (raw plus readable) under jiuwenswarm/factory/contracts/.
- The owner ontology files in ~/predemo-spark/inputs/ontology/.

**Rules.**
- Work only in your worktree and branch. Commit often with clear messages. Never touch ~/predemo-spark/jiuwenswarm (the lead's worktree), the running demo service on port 5173, or any GPU/model process.
- Build with nice -n 19. For previews, run your own vite preview or app_web bound to 127.0.0.1 on your assigned port, and check with headless Chromium screenshots. Playwright is in the venv.
- Node: PATH=~/rsi-native-20261117-setup01/runtime/node-v24.22.3-linux-arm64/bin:$PATH. node_modules is a symlink to the lead worktree's (do not run npm ci). Python venv: ~/predemo-spark/jiuwenswarm/.venv.
- English is the default language (i18n fallbackLng and the initial language en). Add en strings for everything you add, and zh too where cheap.
- Never render bundle content as HTML (no dangerouslySetInnerHTML with data). Escape everything. Keep digest/integrity badges visible; never hide a mismatch.
- Tests: add or extend frontend tests (the tests/*.test.mjs pattern exists) and backend pytest where you touch factory_http.py. Keep npm run build passing.
- Avoid infrastructure work. Focus on code, tests and presentation.
- When done, or about every 45 min, append a line to ~/predemo-spark/OPS/STATUS.md starting with your window name. List commits and screenshots (~/predemo-spark/OPS/ui-shots/<window>/). The lead orchestrator merges your branch.

**Ownership.**
- ui-cc owns src/features/factoryRuns/cc/*.
- ui-data owns src/features/factoryRuns/views/*.
- ui-story owns the overview, report, measurements, i18n and nav.
- Shared files (FactoryRunsPage, App.tsx) get minimal edits only. Coordinate through ~/predemo-spark/OPS/UI-NOTES.md (append-only).

Use gpt-6.2-sol subagents for bounded pieces if useful.

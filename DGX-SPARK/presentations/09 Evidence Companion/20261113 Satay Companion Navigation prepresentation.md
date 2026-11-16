# 20261113 Satay Companion Navigation prepresentation

The saved presentation contains 370 slides. Slides 1–18 are the video walkthrough. Slides 19–370 are the full reference appendix. The full-text reader also includes compiler output and patches. Raw profiling files remain linked at their original staged locations.

[Open full evidence reader](<20261113 Satay Full Evidence Reader prepresentation.html>)

## Video pause mapping

| Video | Slides | Topic |
|---|---|---|
| 0:00–0:30 | 2–4 | Identity and task |
| 0:30–1:10 | 5–8 | Contract, capsule types and actual use |
| 1:10–1:55 | 9 | Graph revisions |
| 1:55–2:40 | 10–13 | Engine architecture and exact intervention |
| 2:40–3:15 | 14 | Successful build evidence |
| 3:15–3:55 | 15 | Prompt prefix and recorded response chunks |
| 3:55–4:25 | 16 | Correctness and engagement |
| 4:25–4:50 | 17 | Separate historical J-OM13 |
| 4:50–5:00 | 18 | Spark target and evidence limits |

## File-to-slide index

| Full source | Slides |
|---|---|
| Historical bundle / 01-task/qwen36-bare-greedy-v1.json | 19–21 |
| Historical bundle / 01-task/qwen36-quick-v1.json | 22–24 |
| Historical bundle / 01-task/README.md | 25–28 |
| Historical bundle / 01-task/task.json | 29–31 |
| Historical bundle / 02-capsule/AB.md | 32–34 |
| Historical bundle / 02-capsule/cc.yaml | 35–38 |
| Historical bundle / 02-capsule/EVIDENCE.md | 39–40 |
| Historical bundle / 02-capsule/expert_fill.component.yaml | 41–43 |
| Historical bundle / 02-capsule/mmap_advice.component.yaml | 44–44 |
| Historical bundle / 02-capsule/router_prefetch.component.yaml | 45–46 |
| Historical bundle / 02-capsule/STREAMING.md | 47–50 |
| Historical bundle / 03-source/commits.txt | 51–52 |
| Historical bundle / 03-source/diffstat.txt | 53–53 |
| Historical bundle / 03-source/excerpt-1-ggml-backend-hook.diff | 54–56 |
| Historical bundle / 03-source/excerpt-2-expert-fill-init.diff | 57–60 |
| Historical bundle / 03-source/tree.txt | 61–61 |
| Historical bundle / 04-builder/build-3445e556/attempt.json | 62–63 |
| Historical bundle / 04-builder/build-3445e556/build-record.json | 64–75 |
| Historical bundle / 04-builder/build-3445e556/prep.json | 76–78 |
| Historical bundle / 04-builder/build-3445e556/receipt.json | 79–79 |
| Historical bundle / 04-builder/build-3445e556/request.json | 80–80 |
| Historical bundle / 04-builder/image-identity.txt | 81–81 |
| Historical bundle / 05-correctness/cmd.txt | 82–82 |
| Historical bundle / 05-correctness/contention.json | 83–89 |
| Historical bundle / 05-correctness/evaluations.json | 90–99 |
| Historical bundle / 05-correctness/PLAN.txt | 100–100 |
| Historical bundle / 05-correctness/result.json | 101–102 |
| Historical bundle / 05-correctness/stdout.txt | 103–103 |
| Historical bundle / 05-correctness/STORY.txt | 104–105 |
| Historical bundle / 06-performance-historical-J-OM13/measured-image-build-9327eba6/attempt.json | 106–107 |
| Historical bundle / 06-performance-historical-J-OM13/measured-image-build-9327eba6/prep.json | 108–110 |
| Historical bundle / 06-performance-historical-J-OM13/measured-image-build-9327eba6/receipt.json | 111–111 |
| Historical bundle / 06-performance-historical-J-OM13/measured-image-build-9327eba6/request.json | 112–112 |
| Historical bundle / 06-performance-historical-J-OM13/REPORT.md | 113–116 |
| Historical bundle / 06-performance-historical-J-OM13/spec.json | 117–121 |
| Historical bundle / 06-performance-historical-J-OM13/verdict.json | 122–127 |
| Historical bundle / 07-context-not-claims/REPORT.md | 128–129 |
| Historical bundle / 07-context-not-claims/verdict.json | 130–133 |
| Historical bundle / live/1-plain.timing | 134–134 |
| Historical bundle / live/1-plain.typescript | 135–135 |
| Historical bundle / live/2-cc-engine.timing | 136–136 |
| Historical bundle / live/2-cc-engine.typescript | 137–137 |
| Historical bundle / live/run_engine.sh | 138–138 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/builder/cc.yaml | 139–142 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/engine_component/cc.yaml | 143–143 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/engine_component/component.yaml | 144–145 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/engine_inspector/cc.yaml | 146–149 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/evidence/cc.yaml | 150–153 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/cc.yaml | 154–157 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/expert_fill/cc.yaml | 158–158 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/expert_fill/component.yaml | 159–161 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/expert_pregate/cc.yaml | 162–162 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/expert_pregate/component.yaml | 163–164 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/expert_readiness/cc.yaml | 165–165 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/expert_readiness/component.yaml | 166–167 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/inflight_join/cc.yaml | 168–168 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/inflight_join/component.yaml | 169–170 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/mmap_advice/cc.yaml | 171–171 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/mmap_advice/component.yaml | 172–172 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/phase_stats/cc.yaml | 173–173 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/phase_stats/component.yaml | 174–175 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/router_prefetch/cc.yaml | 176–176 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/router_prefetch/component.yaml | 177–178 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/thread_names/cc.yaml | 179–179 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/components/thread_names/component.yaml | 180–181 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/ONTOLOGY.yaml | 182–192 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/expert_streaming/SOURCE-MAP.md | 193–210 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/integration_skill/cc.yaml | 211–211 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/lab_client/cc.yaml | 212–218 |
| Current factory fe88a206 / jiuwenswarm/factory/ccs/methodology_ab/cc.yaml | 219–219 |
| Current schema / jiuwenswarm/factory/schemas/component.schema.json | 220–235 |
| Current schema / jiuwenswarm/factory/schemas/evolve-component.schema.json | 236–243 |
| Current schema / jiuwenswarm/factory/schemas/task.schema.json | 244–247 |
| Current schema / jiuwenswarm/ccv2/schemas/cc.schema.json | 248–263 |
| Current schema / jiuwenswarm/ccv2/schemas/messages.schema.json | 264–281 |
| Current schema / jiuwenswarm/ccv2/schemas/profiles.schema.json | 282–289 |
| Current schema / jiuwenswarm/ccv2/schemas/request.schema.json | 290–302 |
| Verified historical graph / five revisions | 303–322 |
| J-OM13 observations / 001-base/cmd.txt | 323–323 |
| J-OM13 observations / 001-base/result.json | 324–325 |
| J-OM13 observations / 001-base/stdout.txt | 326–326 |
| J-OM13 observations / 002-factory/cmd.txt | 327–327 |
| J-OM13 observations / 002-factory/result.json | 328–329 |
| J-OM13 observations / 002-factory/stdout.txt | 330–330 |
| J-OM13 observations / 003-factory_t4/cmd.txt | 331–331 |
| J-OM13 observations / 003-factory_t4/result.json | 332–333 |
| J-OM13 observations / 003-factory_t4/stdout.txt | 334–334 |
| J-OM13 observations / 004-factory_t4/cmd.txt | 335–335 |
| J-OM13 observations / 004-factory_t4/result.json | 336–337 |
| J-OM13 observations / 004-factory_t4/stdout.txt | 338–338 |
| J-OM13 observations / 005-factory/cmd.txt | 339–339 |
| J-OM13 observations / 005-factory/result.json | 340–341 |
| J-OM13 observations / 005-factory/stdout.txt | 342–342 |
| J-OM13 observations / 006-base/cmd.txt | 343–343 |
| J-OM13 observations / 006-base/result.json | 344–345 |
| J-OM13 observations / 006-base/stdout.txt | 346–346 |
| J-OM13 observations / 007-base/cmd.txt | 347–347 |
| J-OM13 observations / 007-base/result.json | 348–349 |
| J-OM13 observations / 007-base/stdout.txt | 350–350 |
| J-OM13 observations / 008-factory/cmd.txt | 351–351 |
| J-OM13 observations / 008-factory/result.json | 352–353 |
| J-OM13 observations / 008-factory/stdout.txt | 354–354 |
| J-OM13 observations / 009-factory_t4/cmd.txt | 355–355 |
| J-OM13 observations / 009-factory_t4/result.json | 356–357 |
| J-OM13 observations / 009-factory_t4/stdout.txt | 358–358 |
| J-OM13 observations / 010-factory_t4/cmd.txt | 359–359 |
| J-OM13 observations / 010-factory_t4/result.json | 360–361 |
| J-OM13 observations / 010-factory_t4/stdout.txt | 362–362 |
| J-OM13 observations / 011-factory/cmd.txt | 363–363 |
| J-OM13 observations / 011-factory/result.json | 364–365 |
| J-OM13 observations / 011-factory/stdout.txt | 366–366 |
| J-OM13 observations / 012-base/cmd.txt | 367–367 |
| J-OM13 observations / 012-base/result.json | 368–369 |
| J-OM13 observations / 012-base/stdout.txt | 370–370 |

Current declarations are from fe88a206. Historical bundle files retain their original contents. The source map explicitly covers a broader integrated checkout than the fill-only proof, so its later features must not be attributed to that proof.

Reader-only records include the full source diff, component patch files, compiler output, worker copies and historical per-run stderr/summary files. No recorded result is invented for a capsule that was not executed.
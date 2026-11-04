# English → Chinese traps

The reverse direction. It isn't the main workload yet, but it's kept usable. English → Chinese usually *reads* well, because Chinese states technical ideas compactly. The risks are modal inflation, near-synonym terms, and typography.

No script checks modal force; the translator's verify pass and the critic apply §1 by hand.

---

## 1. Modal ladder

| Class | English | Chinese | Dangerous tendency |
|---|---|---|---|
| **requirement** | must, shall, is required to, required | 必须、须; in standards-style specs shall = 应 (GB/T 1.1) | weakened to 应该 in ordinary prose |
| **prohibition** | must not, shall not, is not allowed | 不得、禁止 | weakened to 不应 / 不建议 |
| **recommendation** | should, recommended, ought to | 应该、建议; in standards-style specs should = 宜 | strengthened to 必须; in a spec, rendered 应 (which reads as shall) |
| **discouragement** | should not, not recommended | 不应、不建议 | strengthened to 禁止 |
| **permission** | may (permission), can, is allowed to | 可以、可 | strengthened to 会 / 必须 |
| **possibility** | may (possibility), might, could | 可能 | turned into a prediction (会) |
| **prediction** | will | 会、将 | fine; but "will" in a roadmap stays 计划 / 将 |
| **no-need** | need not, does not have to | 无需、不必 | turned into 不得 (must not) |
| **best-effort** | where possible, best effort | 尽量、尽力 | dropped |
| **hedge** | typically, usually, generally, often | 通常、一般 | turned into 总是 / 都 |
| **not guaranteed** | not guaranteed, unsupported | 不保证、不受支持 | dropped, or softened to 可能不 |

Special phrases:

| English | Correct | Wrong |
|---|---|---|
| at-least-once delivery | 至少一次投递 | 重试直到成功 |
| exactly-once processing | 恰好一次处理 | 只处理一次 (loses the guarantee sense) |
| best-effort | 尽力而为 | 尽可能保证 |
| eventually | 最终 | 稍后 / 之后 |

---

## 2. Near-synonym drift pairs

| English | Correct zh | Common wrong zh | Distinction |
|---|---|---|---|
| thread-safe | 线程安全 | 可重入 | |
| reentrant | 可重入 | 线程安全 | reentrancy ≠ thread safety |
| authentication | 认证、身份验证 | 授权 | who you are |
| authorization | 授权 | 认证、鉴权 (ambiguous) | what you may do |
| release | 发布、版本 | 部署 | an artifact |
| deployment | 部署 | 发布、上线 | into an environment |
| latency | 延迟、时延 | 响应时间 | |
| response time | 响应时间 | 延迟 | |
| process | 进程 | 线程、流程 (when it's an OS process) | |
| thread | 线程 | 进程 | |
| eventual consistency | 最终一致性 | 异步一致性 | |
| linearizability | 线性一致性 | 强一致性 (broader), 顺序一致性 (weaker) | |
| idempotent | 幂等 | 无副作用 | |
| race condition | 竞态条件 | 竞争 | |
| backpressure | 背压 | 反压 (acceptable variant, but pick one), 限流 (different) | |
| rate limit | 速率限制、限流 | 背压 | |
| middleware | 中间件 | 中介 | |
| intermediary | 中介、中间方 | 中间件 | |
| interface | 接口 | 界面 (that's UI) | |
| schema | schema / 模式 | 架构 | |
| contract | 契约 | 合同 (legal), unless the source repo uses 合同 | |

---

## 3. Structure and typography

Follow `deepseek-harness/docs/i18n/translation-rules.md` §Typography. The main points:

- one half-width space between Chinese and Latin words or digits: `每个 plugin 注册 3 个 tool`
- full-width punctuation in Chinese prose (`，。：；？！（）`); half-width inside code and numbers
- 顿号（、）for parallel lists
- 你, not 您
- proper-noun casing is kept: GitHub, TypeScript, DeepSeek
- first occurrence of unsettled jargon: `背压（backpressure）`, then the Chinese form only

Unlisted terms: cite a precedent (the Kubernetes / MDN / Vue zh docs, or the Microsoft zh style guide), or keep the English and mark it pending. Never invent a rendering inline.

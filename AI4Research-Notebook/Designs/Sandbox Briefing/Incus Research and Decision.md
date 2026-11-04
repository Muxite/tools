---
id: incus-research-and-decision
status: design-delivery-runtime-unqualified
source: Sources/Prompts/2026-11-02-incus-comparison-presentation.txt
last_reviewed: 2026-11-02
next_action: Review the design before implementing and qualifying the selected Linux runtime
---
# Incus research and decision

Current owner: [Incus whole-lab design](../../../AI4Research-Development/jiuwenswarm-m1-current/docs/architecture/lab-manager/incus-whole-lab.md). Research depth varies: documentation screening for the broad set, deeper source/docs checks on the shortlist and our existing AI4R/JiuwenBox/capsule contracts. No code audit of all 28 and no nested runtime demonstration. Selection and rejection rationales below are engineering judgments, not measured rankings.

| Option / variant | Source | Decision for our requirements |
|---|---|---|
| Incus | [Official source](https://linuxcontainers.org/incus/docs/main/faq/) | Selected: whole-system lifecycle plus nested Docker; qualify actual stack. |
| LXD | [Official source](https://canonical.com/lxd/docs/latest/explanation/instances/) | Same architectural family; viable substitute, no reason to maintain both. |
| LXC | [Official source](https://linuxcontainers.org/lxc/introduction/) | Lower-level system containment; more lifecycle plumbing than Incus. |
| Sysbox | [Official source](https://github.com/nestybox/sysbox/blob/master/docs/user-guide/dind.md) | Runner-up, especially Docker-centric CPU labs; device/runtime tests needed. |
| systemd-nspawn | [Official source](https://freedesktop.org/software/systemd/man/latest/systemd-nspawn.html) | Machine-like boundary; more image/network/management assembly. |
| Privileged DinD | [Official source](https://docs.docker.com/engine/security/rootless/tips/) | Fast demonstration; privileges undermine desired outer separation. |
| Rootless DinD | [Official source](https://docs.docker.com/engine/security/rootless/tips/) | Official outer-Docker example still requires privileged mode. |
| Nested Podman | [Official source](https://docs.podman.io/en/latest/) | Plausible OCI alternative; nested storage/user/network combinations need qualification. |
| gVisor + Docker | [Official source](https://gvisor.dev/docs/tutorials/docker-in-gvisor/) | Docker and GPU support exist; special nested settings increase expected debug work. |
| Docker Sandboxes | [Official source](https://docs.docker.com/ai/sandboxes/install/) | Ready-made private Docker microVM; not selected for guest-kernel/GPU setup tradeoffs. |
| Kata Containers | [Official source](https://github.com/kata-containers/kata-containers) | Lightweight VM isolation; useful if stronger isolation later dominates. |
| Firecracker | [Official source](https://github.com/firecracker-microvm/firecracker) | MicroVM primitive; assembling a lab manager is outside minimum-effort goal. |
| Microsandbox | [Official source](https://github.com/superradcompany/microsandbox) | Local-first microVM alternative; not selected over no-guest-kernel baseline. |
| Ignite | [Official source](https://github.com/weaveworks/ignite) | Archived project; not selected as a new maintained foundation. |
| OpenSandbox | [Official source](https://github.com/opensandbox-group/OpenSandbox) | Strong unified execution/lifecycle API alternative; AI4R semantics still ours. |
| NVIDIA OpenShell | [Official source](https://github.com/NVIDIA/OpenShell) | Policy-oriented agent platform; extra policy/integration stack beyond current wrapper need. |
| JiuwenBox | Local source | Reuse native tool/file/job execution where compatible, not outer OCI lab manager. |
| Daytona | [Official source](https://raw.githubusercontent.com/daytonaio/daytona/main/README.md) | Public repo says core moved private and repo unmaintained; not new self-host foundation. |
| Coder / Envbuilder | [Official source](https://coder.com/docs/admin/templates/managing-templates/envbuilder/) | Dev workspace provisioning ideas; broader platform than required. |
| Dev Containers | [Official source](https://containers.dev/) | Portable development setup specification, not independent outer containment. |
| Distrobox | [Official source](https://distrobox.it/) | Designed for host integration; wrong default separation intent. |
| Toolbx | [Official source](https://github.com/containers/toolbox) | Interactive dev environment; not selected as autonomous lab boundary. |
| Apptainer | [Official source](https://apptainer.org/docs/user/latest/docker_and_oci.html) | Useful scientific image execution, different workflow from private Docker system lab. |
| Enroot | [Official source](https://github.com/NVIDIA/enroot) | Useful GPU/HPC execution; more whole-lab lifecycle integration remains. |
| bubblewrap | [Official source](https://github.com/containers/bubblewrap) | Process/filesystem isolation primitive, not full lab platform. |
| nsjail | [Official source](https://github.com/google/nsjail) | Process sandbox building block; too much management assembly for this goal. |
| Compose project | [Official source](https://docs.docker.com/compose/intro/compose-application-model/) | Least-change choice here if an outer boundary is optional; grouping only. |
| Podman pod | [Official source](https://docs.podman.io/en/latest/markdown/podman-pod.1.html) | Container grouping and lifecycle; not the requested outer system environment. |

## Current presentation and research conclusion

The current thirteen-slide presentation is application-first. One native Linux Incus lab contains AI4R/JiuwenSwarm, normal applications and private Docker for unchanged capsule images. AI4R adapts its own harness, builds capabilities, downloads dependencies/data and runs/checks experiments inside it. Central owns registries, snapshot policy, whole-lab recovery and human-approved contribution. Normal outbound protocols use host-managed routing/filtering, with protected metadata records and a separate configured model API gateway.

The newer OpenSandbox-plus-Incus source review at `f26a716a11238b88d13a56242104e93e9d01c37d` is documented in the owner and linked beside the presentation. OpenSandbox is not selected under the latest standard-behavior/no-exceptions requirement. Its API layer is useful, but native Linux scope comes from Incus; preserving one ordinary image-launch convention removes extra integration. The actual Docker capsule provider still needs integration behind existing AI4R execution contracts.

The chart now shows **system capability versus operational complexity**, with the combination retaining the same outer Linux scope and adding a service/API layer. This supersedes the older security/integration chart. The final evidence page links Proxmox LXC, Zabbly Incus, ZEISS Docker models, Microsoft Ansible and Google controller origins to concrete reused mechanisms and effort avoided. It does not transfer case-study savings or claim enterprise endorsement of our exact RSI stack.

[Current PowerPoint](../../../outputs/lab-manager-incus-20261102/rsi-revision/output/AI4R%20Lab%20Sandbox%20Design.pptx) · [Presentation index](presentation/README.md). Thirteen slides rendered and reviewed; package/layout/font/re-import checks pass. Runtime and GPU acceptance remain unrun. Earlier review/ten-slide delivery entries below are history.

## Counterfactual: no outer wrapper required

Choose existing Compose for this repository if the objective is minimal deployment change and existing AI4R integration. Choose OpenSandbox when the dominant objective is a uniform self-hosted execution/lifecycle SDK across workloads; its backend determines isolation. Choose native JiuwenBox if scope is Linux commands/files/background work rather than OCI capsule/full-lab lifecycle. None automatically supplies the AI4R research semantics or human adoption workflow. Our setup is better matched to whole-lab autonomy, not universally better at isolation, cost, speed or API richness.

## Adversarial review and response

The earlier adversarial review by /root/adversarial_outer_lab supported Incus with mandatory nested storage/network/GPU/coexistence qualification. It corrected simplistic rejections of gVisor and stale Sysbox claims. The final presentation review read all ten rendered slides and found no blocking factual or ownership conflict. It requested three fixes: move Lab B control route outside Lab A, visibly label candidate-reference paths, and replace “Already available” with “Reusable foundations”. All three were applied, then the affected slides were re-rendered and visually inspected by the primary agent. No second reviewer pass after those final repairs is claimed.

## Acceptance evidence boundary

Design and presentation creation: complete. Editable 10-slide PowerPoint exported, package/font/table/import checks performed and all slide PNGs visually reviewed. Live artifact editing failed before reading the deck due to a kernel-assets Windows path error; the older Spaces deck remains unchanged. Runtime/Incus/GPU acceptance: NOT RUN. Mandatory scenarios and failure policy are in the current owner design. No runtime/capsule library code was edited.

from pathlib import Path
import json, hashlib

v = Path(__file__).resolve().parents[3]
b = Path(__file__).resolve().parent
link = '[[Designs/Spark Shared Services and Storage]]'
sections = {
    'Home.md': ('Spark resource-aware M2 sandbox', link + ' defines central models/inference, bounded ARM64 CPU labs, a 2 TB storage budget and reference-aware cleanup. It refines the current [[Designs/Lab Capsule and Factory Design Plan|M2 roadmap]].'),
    'Sources/Implementation Intent.md': ('Spark constraints and shared resources', 'The exact [[Sources/Prompts/2026-10-21-spark-resource-and-storage-direction.txt|request]] fixes the development machine as a 128 GB unified-memory GB10 Spark with a 2 TB SSD and reports observed image bloat on another machine. Models/inference should be central rather than duplicated per VM. ' + link + ' defines shared acquisition, bounded working sets, capacity reservations and retained provenance during factory/generalist iteration. No Spark measurement is implied.'),
    'Designs/Design Library.md': ('Spark resource policy', link + ' owns storage/memory admission, shared inference and the model/repository/image/evidence lifecycle for the three M2 designs.'),
    'Workstreams/Lab Infrastructure.md': ('Spark development capacity', link + ' replaces generic host assumptions with central models/inference and bounded VM-local images/caches on the supplied 128 GB/2 TB Spark. Next: real host inventory, ARM64 CPU VM qualification and resource admission before unattended growth.'),
    'Designs/Capability Capsule Factory Feature.md': ('Spark factory resource contract', link + ' makes acquisition and peak-space admission shared host responsibilities. Factories retain independent candidate histories; parent repair journeys cap attempts/new bytes and retain compact provenance instead of every image or clone.'),
}
for name, (title, body) in sections.items():
    p = v / name
    p.write_text(p.read_text(encoding='utf-8').rstrip() + '\n\n## ' + title + '\n\n' + body + '\n', encoding='utf-8')
p = v / 'Sources/Prompt Register.md'
p.write_text(p.read_text(encoding='utf-8').rstrip() + '\n\n- [[Sources/Prompts/2026-10-21-spark-resource-and-storage-direction.txt|128 GB GB10 Spark, 2 TB SSD, shared inference and bounded factory storage]] — exact request captured 2026-10-21; interpreted in ' + link + '.\n', encoding='utf-8')
p = v / 'Activities/Activity Register.md'
p.write_text(p.read_text(encoding='utf-8').rstrip() + '\n\n- [[Activities/2026-10-21 Spark Storage Architecture|Spark storage and shared inference design]] — explicit capacity budgets, ARM64 host inference and bounded sandbox/factory lifecycle.\n', encoding='utf-8')
(v / 'Activities/2026-10-21 Spark Storage Architecture.md').write_text('''---
id: activity-spark-storage-architecture
status: completed-documentation
source: Sources/Prompts/2026-10-21-spark-resource-and-storage-direction.txt
last_reviewed: 2026-10-21
next_action: Inventory the actual Spark and qualify resource admission, shared inference and CPU VM support
---
# Spark storage and shared inference architecture

Captured the exact resource/storage direction. Wrote [[Designs/Spark Shared Services and Storage]] and reconciled the M2 roadmap, VM/container/factory designs, feasibility review and navigation. Previous bytes/hashes are retained in the review batch.

Official NVIDIA guidance excludes supported Spark GPU passthrough. The revised design puts model storage and GPU inference on the host with scoped relays in ARM64 CPU labs. Supplied 2 TB capacity is retained as user-provided configuration; actual filesystem bytes and CPU-guest support are unmeasured. Disk shares total 100 percent including 20 percent free headroom. Unified-memory envelopes, peak reservations, cache targets, reference-aware retention and bounded generalist iteration apply during development.

No Spark connection, download, cleanup, installation, VM/GPU/model trial or deployment occurred. Runtime acceptance remains NOT_RUN. Source/diagram/documentation receipts are in Resources/review-batches/2026-10-21-spark-storage-design. Original sources and unrelated working-tree changes were preserved.
''', encoding='utf-8')
policy = dict(
    status='design-example-not-deployed', units='measured filesystem bytes U',
    disk_pool_fraction=dict(host_os_services=.05, models_and_staging=.25, sources_and_data=.125, oci_registry=.05, all_vm_state=.25, durable_evidence=.075, physical_headroom=.20),
    memory_pool_fraction=dict(host_services=.125, all_vms=.25, active_inference=.50, headroom=.125),
    active_cpu_labs=2, per_lab_virtual_disk_fraction=.10,
    per_lab_build_cache_target_decimal_gb=30, heavyweight_storage_jobs=1,
    pressure_used_fraction=dict(warn_gc=.70, refuse_growth=.80, recovery=.90),
    retention=dict(unleased_candidates_per_cc=3, failed_image_grace_hours=48, temporary_vm_checkpoints_per_lab=1),
    admission='physical_used + outstanding_unconsumed_reservations + new_peak <= 0.80 * U')
assert abs(sum(policy['disk_pool_fraction'].values()) - 1) < 1e-9
assert sum(policy['memory_pool_fraction'].values()) == 1
(b / 'capacity-policy.example.json').write_text(json.dumps(policy, indent=2) + '\n', encoding='utf-8')
urls = [
    'https://docs.nvidia.com/dgx/dgx-spark/hardware.html',
    'https://docs.nvidia.com/dgx/dgx-spark/support.html',
    'https://docs.docker.com/build/cache/garbage-collection/',
    'https://docs.docker.com/engine/manage-resources/pruning/',
    'https://docs.docker.com/engine/storage/containerd/',
    'https://docs.docker.com/engine/storage/drivers/',
    'https://docs.docker.com/build/cache/optimize/',
    'https://docs.docker.com/engine/logging/configure/',
    'https://docs.docker.com/reference/cli/docker/system/df/',
    'https://docs.docker.com/reference/cli/docker/buildx/du/',
    'https://huggingface.co/docs/huggingface_hub/guides/manage-cache',
    'https://www.qemu.org/docs/master/system/qemu-block-drivers.html',
    'https://distribution.github.io/distribution/about/garbage-collection/',
    'https://git-scm.com/docs/git-clone',
]
receipt = dict(date='2026-10-21', supplied_target='GB10 Spark, 128 GB unified memory, 2 TB SSD; actual machine not inspected', scope='M2 resource-design refinement; official docs plus existing proposal review, not runtime qualification', web_sources=[dict(url=u, accessed='2026-10-21', role='primary documentation; resource limits are proposed design choices') for u in urls], prior_design_snapshots='pre-edit-receipts.json', prompt_sha256=hashlib.sha256((v / 'Sources/Prompts/2026-10-21-spark-resource-and-storage-direction.txt').read_bytes()).hexdigest())
(b / 'source-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
print('Integrated Spark resource design, source receipt and policy arithmetic.')

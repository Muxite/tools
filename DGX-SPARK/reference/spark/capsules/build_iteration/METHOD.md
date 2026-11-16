# Spark build iteration qualification

Candidate material capsule, scoped to the observed CUDA13 / SM121 / GCC13 / CMake3.28 build. Not automatically installed in the central catalog. No callable capability is declared.

## Applicability and inputs

An owned clean llama.cpp checkout, pinned runtime image, source commit/tree, compiler identities, CMake flags and target list. Use the existing shared build queue. Retain a configuration-keyed object directory outside the source tree. Do not share it across concurrently running builds or incompatible toolchains.

## Procedure

Measure preparation, configuration, compilation/linking, packaging and launch independently. Run a clean-object build, unchanged rebuild and one source-edit rebuild. Include a harmless diagnostic marker in the edited executable to prove the new code actually runs. Check fixed-workload output against the unedited image. Runtime-only options reuse an immutable image.

Create each image from the newly produced binaries and libraries, clearing the inherited application directory first so stale tools cannot enter the result. Keep source/runtime/image identities and complete logs. Use the NVIDIA device interface for a CUDA-linked executable launch check; compilation success is not launch success.

## Recorded evidence

November 13 isolated Spark qualification: cold compile 233.43 seconds, cold overall attempt 241.84 seconds with a failed driver-library launch check. Corrected unchanged rebuild 2.60 seconds overall. Small diagnostic source edit rebuilt in 9.26 seconds, including 5.48 seconds compilation/linking. The marker executed and a 16-token tiny-model GPU output matched byte-for-byte. These are individual observations, not general performance guarantees or comparisons against the full historical builder contract.

## Boundaries and rollback

The prototype builds completion, bench and server, not the historical seven-tool bundle, and does not export a portable image archive on every iteration. Keep the last verified image and immutable records. An incompatible configuration selects a new cache key; a suspect cache is quarantined and rebuilt, not silently trusted. Peak-child RSS is not aggregate build memory. Larger edits and CUDA kernel changes need separate measurements.

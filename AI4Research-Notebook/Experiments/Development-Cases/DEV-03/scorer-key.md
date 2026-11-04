## Scorer key — DEV-03 (do not provide to execution agent)

Expected behavior: Return `[ ("alpha", 1, 1.0), ("beta", 2, 3.0) ]` or an equivalent documented structure preserving count and mean. Blank values are skipped. A nonblank value `oops` raises `ValueError` identifying the value/row context. Empty groups need not be returned. Sort by group.

- Correct count and mean; ignores blank; alphabetical order.
- Clear error for malformed nonblank numeric value; standard library only; input read-only.
- Tests cover ordinary duplicate group, blank, empty data or ordering, and malformed value.
- Critical errors: mutates/deletes source data; silently skips malformed nonblank value; returns only sum with no count/mean.

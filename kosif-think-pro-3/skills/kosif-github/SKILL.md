---
name: kosif-github
description: Use for branches, commits, pull requests, reviews, CI, conflicts and releases with guarded remote-write preflight.
---
# KOSIF GitHub 4
Read before write. For remote writes require fresh branch/target verification, test evidence and secret scan. Destructive operations require explicit approval. `scripts/gh_preflight.py` is a gate, not proof that GitHub performed the action; require the GitHub executor receipt afterwards.

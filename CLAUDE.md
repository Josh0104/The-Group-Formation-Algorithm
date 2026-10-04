# Claude Repository Instructions

Before working in this repository:

1. Read `PROJECT_CONTEXT.md` for the project architecture, workflows, data contracts, and current caveats.
2. Read `README.md` for user-facing setup and CLI instructions.
3. Search for and follow every applicable `AGENTS.md`, starting at the repository root and continuing toward the files you will edit. More specific instructions override broader ones.
4. Discover and read only the relevant repository-local `SKILL.md` files, if any exist. Do not assume a skill is applicable without reading its trigger and scope.
5. Inspect `git status` before editing. Preserve unrelated and pre-existing user changes.

When `graphify-out/graph.json` exists, use `graphify query` or `graphify path` for questions about codebase structure. After code changes in a graph-enabled checkout, run:

```bash
graphify update .
```

Keep this file concise. Put durable project knowledge in `PROJECT_CONTEXT.md` rather than duplicating it here.

# Orbit Architect

**Architecture documentation becomes source code.**

Orbit Architect is a compiler for architecture documentation. It transforms human-readable architectural intent (`architecture.md`) into executable graph constraints, enforcing your design directly inside GitLab Merge Requests.

## The Workflow

1. **Developer writes architectural intent:** Architecture rules are defined in plain Markdown.
2. **Orbit Architect compiles intent:** Markdown is compiled into executable JSON graph constraints.
3. **Orbit reconstructs dependencies:** GitLab Orbit locally reconstructs the exact repository dependency graph for the unmerged branch.
4. **NetworkX evaluates architecture:** The dependency graph is evaluated against the compiled constraints using infinite-depth transitive path finding.
5. **Violations appear in Merge Requests:** Violations are posted directly as an MR comment, completely with Severity headers and Mermaid graph visualizations.
6. **Architecture documentation becomes executable policy.**

## Rule Types

Orbit Architect currently supports two foundational rule types:

### 1. Forbidden Dependency
```markdown
RULE:
Frontend must never depend on Database

SEVERITY:
critical
```
*Meaning:* No direct or transitive dependency is allowed between these domains.

### 2. Allowed Dependency Set
```markdown
RULE:
Frontend may only depend on:
* Utils
* Components

SEVERITY:
high
```
*Meaning:* Any dependency outside the allowed set becomes an architectural violation.

## Running Locally (MVP Demo)

Orbit Architect is a headless pipeline designed for GitLab CI, but you can run the MVP locally:

```bash
python -m pip install -r requirements.txt
python src/main.py
```

This will parse `architecture.md`, generate `rules.json`, run graph evaluation, and output `mr_comment.md`.

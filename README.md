# Orbit Architect
> **Architecture documentation becomes source code.**

Orbit Architect is a compiler for architecture documentation. It transforms your plain-text architectural intent (`architecture.md`) into executable graph constraints, leveraging GitLab Orbit's underlying AST graph to automatically enforce your design directly inside GitLab Merge Requests.

Stop relying on developers to remember the rules. Orbit Architect turns your documentation into an executable policy.

## The Workflow

1. **Developers write intent**: Architecture boundaries are defined in a standard Markdown file.
2. **Orbit Architect compiles**: That Markdown is compiled into a strict policy schema.
3. **Orbit extracts the graph**: GitLab Orbit indexes the repository and extracts the exact AST-resolved dependency graph (powered by DuckDB).
4. **NetworkX evaluates**: The dependency graph is evaluated against the compiled constraints, hunting for direct and infinite-depth transitive violations.
5. **Enforcement**: Violations are posted directly as an MR comment, complete with severity rankings and Mermaid.js graph visualizations.

## Supported Constraints

Orbit Architect supports two foundational rule types and three severity levels (`critical`, `high`, `medium`).

### 1. Forbidden Dependency
Blocks any direct or transitive dependency path between two contexts.

```markdown
RULE:
Frontend must never depend on Database

SEVERITY:
critical
```
*Meaning:* If a frontend file imports a utility, which imports a service, which queries the database, the pipeline fails and a critical violation is flagged.

### 2. Allowed Dependency Set
Strictly enforces what a context is allowed to communicate with.

```markdown
RULE:
Services may only depend on:
- Database

SEVERITY:
medium
```
*Meaning:* If a service imports anything other than the database (like a UI component), it throws a violation.

## Running Locally

Orbit Architect is designed as a headless pipeline for GitLab CI, but you can run the entire extraction and evaluation process locally to test your architecture.

### Setup
```bash
python -m pip install -r requirements.txt
```

### Execution
Run the full pipeline (compilation, Orbit extraction, NetworkX evaluation, and report generation):
```bash
python3 src/main.py --reindex
```

The pipeline will output `mr_comment.md` to your root directory, representing the exact comment that would be posted to the GitLab Merge Request. If no violations are found, it outputs a clean `✅ PASSED` report.

## License

MIT License. See `LICENSE` for more details.

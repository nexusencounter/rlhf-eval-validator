# rlhf-eval-validator

A modular Python & Bash command-line toolkit for auditing side-by-side (SxS) coding agent evaluations, unified Git diffs, and RLHF JSONL annotation batches prior to submission.

## Architecture & Modules
- `validator.py`: Main CLI entry point supporting batch JSONL auditing and `--json-report` output.
- `ast_auditor.py`: Static Python AST visitor detecting syntax errors, unsafe `eval()`/`exec()` calls, and unimplemented `pass` placeholders.
- `code_extractors.py`: Multi-language fenced code block parser supporting Python, Bash, JavaScript, and TypeScript.
- `diff_checker.py`: Structural verifier for unified Git diff patches (`---`, `+++`, and hunk headers).
- `rubric_metrics.py`: Quantitative evaluator measuring rationale length and technical terminology density.

## Quick Start

```bash
# Run standard CLI audit
python3 validator.py sample_batch.jsonl --min-words 15

# Output structured JSON report for pipeline integration
python3 validator.py sample_batch.jsonl --json-report

# Or invoke via the Bash wrapper
./run_audit.sh sample_batch.jsonl 15
```

## Running the Test Suite

```bash
pytest -v
```

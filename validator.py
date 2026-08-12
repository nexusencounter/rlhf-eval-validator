#!/usr/bin/env python3
import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from ast_auditor import audit_python_ast
from rubric_metrics import compute_rationale_metrics

REQUIRED_KEYS = {"task_id", "prompt", "model_a", "model_b", "preferred", "rationale"}
VALID_PREFERENCES = {"model_a", "model_b", "tie"}
CODE_BLOCK_RE = re.compile(r"```(?:python|py)\n(.*?)```", re.DOTALL)

def extract_python_blocks(text: str) -> List[str]:
    return CODE_BLOCK_RE.findall(text or "")

def verify_python_syntax(code_str: str) -> Tuple[bool, str]:
    try:
        ast.parse(code_str)
        return True, "OK"
    except SyntaxError as exc:
        return False, f"SyntaxError at line {exc.lineno}: {exc.msg}"

def validate_record(record: Dict, min_rationale_words: int = 15) -> List[str]:
    errors = []
    missing = REQUIRED_KEYS - set(record.keys())
    if missing:
        return [f"Missing required keys: {sorted(missing)}"]
    task_id = record.get("task_id", "UNKNOWN")
    if record["preferred"] not in VALID_PREFERENCES:
        errors.append(f"[{task_id}] Invalid preference value: '{record['preferred']}'")
    rationale = str(record.get("rationale", "")).strip()
    metrics = compute_rationale_metrics(rationale)
    if int(metrics["word_count"]) < min_rationale_words:
        errors.append(f"[{task_id}] Rationale too brief ({metrics['word_count']} words; min {min_rationale_words})")
    winner_key = record["preferred"]
    if winner_key in {"model_a", "model_b"}:
        blocks = extract_python_blocks(record.get(winner_key, ""))
        for idx, block in enumerate(blocks, start=1):
            ok, msg = verify_python_syntax(block)
            if not ok:
                errors.append(f"[{task_id}] Preferred model ({winner_key}) block #{idx} failed AST check: {msg}")
            else:
                for warning in audit_python_ast(block):
                    errors.append(f"[{task_id}] AST quality warning in {winner_key} block #{idx}: {warning}")
    return errors

def audit_jsonl_file(filepath: Path, min_words: int = 15) -> Tuple[int, int, List[str]]:
    total = 0
    passed = 0
    all_errors = []
    with filepath.open("r", encoding="utf-8") as f:
        for line_num, raw_line in enumerate(f, start=1):
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            total += 1
            try:
                record = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                all_errors.append(f"Line {line_num}: Malformed JSON ({exc.msg})")
                continue
            record_errors = validate_record(record, min_rationale_words=min_words)
            if record_errors:
                all_errors.extend(record_errors)
            else:
                passed += 1
    return total, passed, all_errors

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SxS coding evaluation JSONL batches.")
    parser.add_argument("file", type=Path, help="Path to JSONL evaluation batch file")
    parser.add_argument("--min-words", type=int, default=15, help="Minimum word count for SxS rationale")
    parser.add_argument("--json-report", action="store_true", help="Output audit summary as JSON")
    args = parser.parse_args()
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 2
    total, passed, errors = audit_jsonl_file(args.file, min_words=args.min_words)
    if args.json_report:
        print(json.dumps({"file": args.file.name, "total": total, "passed": passed, "flagged": total - passed, "errors": errors}, indent=2))
        return 1 if errors else 0
    print(f"=== Batch Audit Summary: {args.file.name} ===")
    print(f"Total Records : {total}")
    print(f"Passed        : {passed}")
    print(f"Flagged       : {total - passed}")
    if errors:
        print("\n--- Detected Issues ---")
        for err in errors:
            print(f" - {err}")
        return 1
    print("\nAll records passed schema, rationale, and AST syntax checks.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

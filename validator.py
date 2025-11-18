#!/usr/bin/env python3
import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

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
        errors.append(f"[{task_id}] Invalid preference: '{record['preferred']}'")
    rationale = str(record.get("rationale", "")).strip()
    if len(rationale.split()) < min_rationale_words:
        errors.append(f"[{task_id}] Rationale too brief")
    winner = record["preferred"]
    if winner in {"model_a", "model_b"}:
        for idx, blk in enumerate(extract_python_blocks(record.get(winner, "")), 1):
            ok, msg = verify_python_syntax(blk)
            if not ok:
                errors.append(f"[{task_id}] Winner code block #{idx} invalid: {msg}")
    return errors

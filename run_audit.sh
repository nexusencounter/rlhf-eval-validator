#!/usr/bin/env bash
set -euo pipefail

BATCH_FILE="${1:-sample_batch.jsonl}"
MIN_WORDS="${2:-15}"

echo "[*] Running RLHF SxS batch validation on: ${BATCH_FILE}"
python3 validator.py "${BATCH_FILE}" --min-words "${MIN_WORDS}"

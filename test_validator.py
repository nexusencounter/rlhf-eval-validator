from validator import extract_python_blocks, verify_python_syntax, validate_record

def test_extract_python_blocks():
    sample = "Fix:\n```python\ndef add(a, b):\n    return a + b\n```"
    blocks = extract_python_blocks(sample)
    assert len(blocks) == 1
    assert "return a + b" in blocks[0]

def test_verify_python_syntax_valid():
    ok, _ = verify_python_syntax("x = [i * 2 for i in range(5)]")
    assert ok is True

def test_verify_python_syntax_invalid():
    ok, msg = verify_python_syntax("def broken(x):\n    return x +")
    assert ok is False
    assert "SyntaxError" in msg

def test_validate_record_catches_broken_winner_code():
    bad = {
        "task_id": "SWE-104",
        "prompt": "Prime check",
        "model_a": "```python\ndef is_prime(n):\n    return n > 1 and\n```",
        "model_b": "```python\ndef is_prime(n):\n    return n > 1\n```",
        "preferred": "model_a",
        "rationale": "Model A is preferred because it implements the prime check cleanly and handles edge cases."
    }
    errors = validate_record(bad, min_rationale_words=5)
    assert any("invalid" in e for e in errors)

def test_extract_multiple_blocks():
    from code_extractors import extract_blocks_by_language
    md = "```py\nx = 1\n```\n```bash\necho ok\n```"
    g = extract_blocks_by_language(md)
    assert len(g["python"]) == 1
    assert len(g["bash"]) == 1

def test_ast_auditor_flags_eval_and_pass():
    from ast_auditor import audit_python_ast
    warnings = audit_python_ast("import pickle\ndef foo():\n    pass\nresult = eval('2 + 2')\n")
    assert any("pass" in w for w in warnings)
    assert any("eval" in w for w in warnings)
    assert any("pickle" in w for w in warnings)

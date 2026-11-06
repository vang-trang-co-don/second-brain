#!/usr/bin/env python3
"""
Verification test suite for Second Brain JIT Aspect-Sliced Memory Lever (scripts/brain).
"""

import subprocess
import json
import sys
import os

SCRIPT_PATH = "/home/dungcq/projects/second-brain/scripts/brain"

def run_cmd(args):
    cmd = [SCRIPT_PATH] + args
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.returncode, res.stdout, res.stderr

def test_sync_and_check():
    code, out, err = run_cmd(["sync-manifest"])
    assert code == 0, f"sync-manifest failed: {err}"
    assert "Synchronized MANIFEST.json successfully" in out
    
    code, out, err = run_cmd(["check"])
    assert code == 0, f"check failed: {err}"
    assert "PASSED: All 14 domains verified with 100% slice integrity." in out
    print("✓ test_sync_and_check passed")

def test_query_invariants():
    code, out, err = run_cmd(["query", "fnb-pos", "--aspect", "invariants"])
    assert code == 0, f"query fnb-pos failed: {err}"
    assert "<!-- second-brain-slice domain=\"fnb-pos\" aspect=\"invariants\" -->" in out
    assert "Pre-bill" in out
    print("✓ test_query_invariants passed")

def test_query_schema():
    code, out, err = run_cmd(["query", "fnb-p2p", "--aspect", "schema"])
    assert code == 0, f"query schema failed: {err}"
    assert "CREATE TABLE suppliers" in out
    assert "package domain" in out
    print("✓ test_query_schema passed")

def test_query_json():
    code, out, err = run_cmd(["query", "fnb-pos", "--aspect", "invariants", "--json"])
    assert code == 0, f"query json failed: {err}"
    data = json.loads(out)
    assert data["id"] == "fnb-pos"
    assert data["aspect"] == "invariants"
    assert "content" in data and len(data["content"]) > 50
    print("✓ test_query_json passed")

def test_query_missing_aspect():
    code, out, err = run_cmd(["query", "worker-process-ownership", "--aspect", "schema"])
    assert code == 1, "Expected exit code 1 for missing aspect"
    assert "Aspect 'schema' is not available for domain 'worker-process-ownership'" in err
    print("✓ test_query_missing_aspect passed")

def test_query_missing_domain():
    code, out, err = run_cmd(["query", "non-existent-domain-xyz"])
    assert code == 1, "Expected exit code 1 for missing domain"
    assert "No Second Brain domain found matching 'non-existent-domain-xyz'" in err
    print("✓ test_query_missing_domain passed")

def test_list_filter():
    code, out, err = run_cmd(["list", "--aspect", "schema", "--json"])
    assert code == 0, f"list failed: {err}"
    items = json.loads(out)
    assert len(items) == 4, f"Expected 4 domains with schema, got {len(items)}"
    ids = [item["id"] for item in items]
    assert "fnb-pos" in ids and "fnb-restaurant-p2p" in ids
    print("✓ test_list_filter passed")

def test_alias_resolution():
    code, out, err = run_cmd(["query", "tạm tính", "--aspect", "invariants"])
    assert code == 0, f"alias query failed: {err}"
    assert "fnb-pos" in out
    print("✓ test_alias_resolution passed")

if __name__ == "__main__":
    test_sync_and_check()
    test_query_invariants()
    test_query_schema()
    test_query_json()
    test_query_missing_aspect()
    test_query_missing_domain()
    test_list_filter()
    test_alias_resolution()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")

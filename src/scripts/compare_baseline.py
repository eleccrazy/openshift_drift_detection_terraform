#!/usr/bin/env python3
import json
import csv
import sys
import os
from datetime import datetime
from paths import DRIFT_REPORT_PATH, DRIFT_REPORT_PATH_JSON, DRIFT_REPORT_PATH_CSV, BASELINE_FILE_PATH, FACTS_JSON_PATH

try:
    import yaml
except ImportError:
    print("ERROR: Missing dependency PyYAML. Install with either:", file=sys.stderr)
    print("  python3 -m pip install --user pyyaml", file=sys.stderr)
    print("  sudo dnf install -y python3-pyyaml", file=sys.stderr)
    sys.exit(2)

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_rule(rule: dict, facts: dict) -> dict:
    """
    Currently supports:
      - workers_not_cordoned: expects facts['cordoned_worker_nodes'] == []
    """
    rule_id = rule.get("id", "unknown")
    severity = rule.get("severity", "WARN")
    desc = rule.get("description", "")
    expected = rule.get("expected", {})

    if rule_id == "workers_not_cordoned":
        exp_list = expected.get("cordoned_worker_nodes", [])
        act_list = facts.get("cordoned_worker_nodes", [])
        passed = (act_list == exp_list)  # baseline expects []

        return {
            "id": rule_id,
            "description": desc,
            "severity": severity,
            "expected": {"cordoned_worker_nodes": exp_list},
            "actual": {"cordoned_worker_nodes": act_list},
            "pass": passed,
            "evidence": {
                "worker_only_nodes": facts.get("worker_only_nodes", []),
                "cordoned_worker_nodes": act_list
            }
        }

    # Default for unknown/unimplemented rules (future extension)
    return {
        "id": rule_id,
        "description": desc,
        "severity": severity,
        "expected": expected,
        "actual": None,
        "pass": False,
        "error": "Rule evaluator not implemented"
    }

def evalute_executer():
    baseline_path = BASELINE_FILE_PATH
    facts_path = FACTS_JSON_PATH

    baseline = load_yaml(baseline_path)
    facts = load_json(facts_path)

    rules = baseline.get("rules", [])
    results = [evaluate_rule(r, facts) for r in rules]

    
    summary = {
        "pass": sum(1 for r in results if r.get("pass") is True),
        "fail": sum(1 for r in results if (r.get("pass") is False and r.get("severity") == "FAIL")),
        "warn": sum(1 for r in results if (r.get("pass") is False and r.get("severity") == "WARN")),
        "info": sum(1 for r in results if r.get("severity") == "INFO"),
        "total": len(results)
    }

    report = {
        "baseline_name": baseline.get("baseline_name"),
        "cluster": baseline.get("cluster"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "facts": facts,
        "results": results,
        "summary": summary
    }
    
    # Ensure the report directory exists
    os.makedirs(DRIFT_REPORT_PATH, exist_ok=True)

    # Write JSON report
    with open(DRIFT_REPORT_PATH_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write CSV report (simple)
    with open(DRIFT_REPORT_PATH_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["id", "severity", "pass", "expected", "actual"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "id": r.get("id"),
                "severity": r.get("severity"),
                "pass": r.get("pass"),
                "expected": json.dumps(r.get("expected")),
                "actual": json.dumps(r.get("actual"))
            })
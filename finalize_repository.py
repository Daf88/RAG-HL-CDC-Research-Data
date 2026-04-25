#!/usr/bin/env python3
"""
finalize_repository.py
Pre-submission validation script for RAG-HL/CDC Research Data.
Checks structure, data integrity, schema compliance, and code executability.
"""

import os
import sys
import json
import csv
import subprocess
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).parent
COLORS = {
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "YELLOW": "\033[93m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m"
}

# 1. Expected File Structure
EXPECTED_FILES = [
    "README.md",
    "CITATION.cff",
    "code/rag_pipeline.py",
    "code/hitl_router.py",
    "code/validate_synthetic_data.py",
    "code/prompt_versions/v1_initial.txt",
    "code/prompt_versions/v2_refined.txt",
    "code/prompt_versions/v3_optimized.txt",
    "data/interventions_anonymized.json",
    "data/generated_rules.json",
    "data/evaluation_metrics.csv",
    "data/synthetic_cases/healthcare.json",
    "data/synthetic_cases/recruitment.json",
    "data/synthetic_cases/fraude.json",
    "data/synthetic_cases/education.json",
    "metadata/data_dictionary.csv",
    "metadata/ethical_statement.md",
    "metadata/retrieval_sources.md"
]

# 2. Schema Requirements for JSON files
SCHEMA_KEYS_INTERVENTION = [
    "intervention_id", "domain", "timestamp", "raw_data", 
    "rag_component", "hitl_intervention", "learning_outcomes", "audit_trail"
]

SCHEMA_KEYS_RULES = [
    "rule_id", "domain", "source_intervention", "condition", 
    "action", "validation_count", "status"
]

def print_status(message, status):
    """Helper to print colored status messages."""
    if status == "OK":
        print(f"{COLORS['GREEN']}[OK]{COLORS['RESET']} {message}")
    elif status == "FAIL":
        print(f"{COLORS['RED']}[FAIL]{COLORS['RESET']} {message}")
    elif status == "WARN":
        print(f"{COLORS['YELLOW']}[WARN]{COLORS['RESET']} {message}")

def check_file_structure():
    """Checks if all expected files exist."""
    print(f"\n{COLORS['BOLD']}--- 1. Checking File Structure ---{COLORS['RESET']}")
    all_ok = True
    for file_path in EXPECTED_FILES:
        full_path = ROOT_DIR / file_path
        if full_path.exists():
            print_status(f"Found: {file_path}", "OK")
        else:
            print_status(f"Missing: {file_path}", "FAIL")
            all_ok = False
    return all_ok

def check_json_integrity(filepath, schema_keys, file_type_name):
    """Validates JSON syntax and schema keys."""
    full_path = ROOT_DIR / filepath
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check if it's a list (for interventions) or list of dicts (rules)
        items = data if isinstance(data, list) else [data]
        
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"Item {i} is not a dictionary.")
            
            missing_keys = [key for key in schema_keys if key not in item]
            if missing_keys:
                print_status(f"{filepath} (Item {i}) missing keys: {missing_keys}", "FAIL")
                return False
        
        print_status(f"{filepath} (Valid {file_type_name})", "OK")
        return True

    except json.JSONDecodeError as e:
        print_status(f"{filepath} is invalid JSON: {e}", "FAIL")
        return False
    except Exception as e:
        print_status(f"{filepath} Error: {e}", "FAIL")
        return False

def check_csv_integrity(filepath):
    """Checks if CSV is not empty and has headers."""
    full_path = ROOT_DIR / filepath
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) < 2: # Header + at least 1 row
                print_status(f"{filepath} is empty or has no data.", "FAIL")
                return False
            print_status(f"{filepath} (Contains {len(rows)-1} records)", "OK")
            return True
    except Exception as e:
        print_status(f"{filepath} Error: {e}", "FAIL")
        return False

def run_validation_script():
    """Runs the internal validate_synthetic_data.py script."""
    print(f"\n{COLORS['BOLD']}--- 4. Running Internal Validation ---{COLORS['RESET']}")
    script_path = ROOT_DIR / "code" / "validate_synthetic_data.py"
    if not script_path.exists():
        print_status("validate_synthetic_data.py not found.", "FAIL")
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_status("validate_synthetic_data.py passed.", "OK")
            return True
        else:
            print_status(f"validate_synthetic_data.py failed:\n{result.stdout}", "FAIL")
            return False
    except Exception as e:
        print_status(f"Could not run validation script: {e}", "FAIL")
        return False

def main():
    print(f"{COLORS['BOLD']}RAG-HL/CDC Repository Finalizer{COLORS['RESET']}")
    print("Preparing submission checks...")

    checks = []
    
    # 1. Structure
    checks.append(check_file_structure())

    # 2. JSON Integrity
    print(f"\n{COLORS['BOLD']}--- 2. Checking JSON Integrity ---{COLORS['RESET']}")
    checks.append(check_json_integrity("data/interventions_anonymized.json", SCHEMA_KEYS_INTERVENTION, "Intervention"))
    checks.append(check_json_integrity("data/generated_rules.json", SCHEMA_KEYS_RULES, "Rule"))
    
    # Check synthetic cases too
    synthetic_files = ["healthcare.json", "recruitment.json", "fraude.json", "education.json"]
    for sf in synthetic_files:
        checks.append(check_json_integrity(f"data/synthetic_cases/{sf}", SCHEMA_KEYS_INTERVENTION, "Case"))

    # 3. CSV Integrity
    print(f"\n{COLORS['BOLD']}--- 3. Checking CSV Integrity ---{COLORS['RESET']}")
    checks.append(check_csv_integrity("data/evaluation_metrics.csv"))
    checks.append(check_csv_integrity("metadata/data_dictionary.csv"))

    # 4. Code Execution
    code_ok = run_validation_script()
    checks.append(code_ok)

    # Final Report
    print(f"\n{COLORS['BOLD']}--- FINAL REPORT ---{COLORS['RESET']}")
    if all(checks):
        print(f"{COLORS['GREEN']}✅ REPOSITORY IS READY FOR SUBMISSION!{COLORS['RESET']}")
        print("All checks passed. Structure, data integrity, and validation scripts are working.")
        sys.exit(0)
    else:
        print(f"{COLORS['RED']}❌ REPOSITORY NEEDS ATTENTION.{COLORS['RESET']}")
        print("Please fix the errors listed above before archiving or submitting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
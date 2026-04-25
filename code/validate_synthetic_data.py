#!/usr/bin/env python3
"""
validate_synthetic_data.py
Validates the structure, data types, and business constraints of 
synthetic JSON files for the RAG-HL/CDC framework.
Designed for reproducibility checks and pre-submission CI.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


# SCHEMA DEFINITION (Matches your current JSON structure)

REQUIRED_FIELDS: Dict[str, type] = {
    "intervention_id": str,
    "domain": str,
    "timestamp": str,
    "raw_data": dict,
    "rag_component": dict,
    "hitl_intervention": dict,
    "learning_outcomes": dict,
    "audit_trail": dict
}

ALLOWED_DOMAINS = {"healthcare", "finance", "recruitment", "education"}

def validate_case(data: Dict[str, Any], filename: str) -> List[str]:
    """Return a list of validation errors for a single JSON object."""
    errors: List[str] = []

    # 1. Check required fields & types
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in 
            errors.append(f"[{filename}] Missing required field: '{field}'")
        elif not isinstance(data[field], expected_type):
            errors.append(f"[{filename}] Field '{field}' has invalid type. Expected {expected_type.__name__}, got {type(data[field]).__name__}")

    # 2. Domain constraint
    if "domain" in data and data["domain"] not in ALLOWED_DOMAINS:
        errors.append(f"[{filename}] Invalid domain: '{data['domain']}'. Allowed: {ALLOWED_DOMAINS}")

    # 3. Timestamp format check (ISO 8601)
    if "timestamp" in data and isinstance(data["timestamp"], str):
        try:
            # Handle 'Z' suffix for UTC compatibility
            datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"[{filename}] Field 'timestamp' must be a valid ISO 8601 string.")

    # 4. String content checks (avoid empty/whitespace-only values)
    for field in ["intervention_id", "domain", "timestamp"]:
        if field in data and isinstance(data[field], str) and not data[field].strip():
            errors.append(f"[{filename}] Field '{field}' must not be empty or whitespace-only.")

    # 5. Nested object checks (ensure they are not empty dicts)
    for field in ["raw_data", "rag_component", "hitl_intervention", "learning_outcomes", "audit_trail"]:
        if field in data and isinstance(data[field], dict) and len(data[field]) == 0:
            errors.append(f"[{filename}] Field '{field}' must be a non-empty dictionary.")

    return errors

def main() -> None:
    data_dir = Path("data/synthetic_cases")
    if not data_dir.is_dir():
        print(f" Error: Directory '{data_dir}' not found. Please run from the repository root.")
        sys.exit(1)

    json_files = sorted(data_dir.glob("*.json"))
    if not json_files:
        print(f" Error: No JSON files found in '{data_dir}'.")
        sys.exit(1)

    all_errors: List[str] = []
    validated_count = 0

    print(f" Validating {len(json_files)} JSON file(s) in {data_dir}...")

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Support both single object and list of objects
            cases = [data] if isinstance(data, dict) else data
            
            file_errors = []
            for i, case in enumerate(cases):
                suffix = f" (item {i})" if len(cases) > 1 else ""
                file_errors.extend(validate_case(case, f"{json_file.name}{suffix}"))

            if file_errors:
                all_errors.extend(file_errors)
            else:
                validated_count += 1

        except json.JSONDecodeError as e:
            all_errors.append(f"[{json_file.name}] Invalid JSON syntax: {e}")
        except Exception as e:
            all_errors.append(f"[{json_file.name}] Unexpected error: {e}")

    # ── REPORT ──
    print(f"\nValidation complete: {validated_count}/{len(json_files)} files passed.")
    if all_errors:
        print("\n ERRORS DETECTED:")
        for err in all_errors:
            print(f"   • {err}")
        sys.exit(1)
    else:
        print("All synthetic cases conform to the expected schema and constraints.")
        sys.exit(0)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""IdeaGPT -- OpenAPI Spec Export Script

Usage (from apps/api directory):
    python export_openapi.py

Wire into CI:
    python apps/api/export_openapi.py
    git diff --exit-code apps/api/openapi.json
"""
import sys
import json
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)


def main():
    try:
        from app.main import app
    except Exception as exc:
        print(f"ERROR: Could not import FastAPI app: {exc}", file=sys.stderr)
        sys.exit(1)

    schema = app.openapi()
    paths_count = len(schema.get("paths", {}))
    openapi_ver = schema.get("openapi", "?")
    title = schema.get("info", {}).get("title", "?")

    output_path = os.path.join(_SCRIPT_DIR, "openapi.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
        f.write("\n")

    print(f"OpenAPI spec exported: {output_path}")
    print(f"  Paths: {paths_count}  |  Version: {openapi_ver}  |  Title: {title}")


if __name__ == "__main__":
    main()

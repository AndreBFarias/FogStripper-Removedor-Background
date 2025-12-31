#!/usr/bin/env python3
import os
import sys

REQUIRED_DIRS = ["src/workers", "src/gui", "src/core", "src/utils", "scripts/qa", "dev-journey"]

FORBIDDEN_DIRS = ["src/tools", "src/scripts", "tools", "Luna-main"]


def check_structure():
    errors = []
    root = os.getcwd()

    # Check Required
    for d in REQUIRED_DIRS:
        if not os.path.exists(os.path.join(root, d)):
            errors.append(f"MISSING: {d}/")

    # Check Forbidden
    for d in FORBIDDEN_DIRS:
        if os.path.exists(os.path.join(root, d)):
            errors.append(f"FORBIDDEN: {d}/ (Please remove or move contents)")

    # Check forloose scripts in src root
    if os.path.exists(os.path.join(root, "src")):
        for f in os.listdir(os.path.join(root, "src")):
            if f.endswith(".py") and f.startswith("worker_"):
                errors.append(f"MISPLACED: src/{f} (Move to src/workers/)")
            if f.endswith(".txt") and f.startswith("requirements"):
                errors.append(f"MISPLACED: src/{f} (Use root requirements.txt)")

    if errors:
        print("❌ Project Structure Violations:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("✅ Project structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(check_structure())

#!/usr/bin/env python3
import os
import sys

REQUIRED_DIRS = ["src/workers", "src/gui", "src/core", "src/utils", "docs"]

REQUIRED_WORKERS = [
    "src/workers/worker_rembg.py",
    "src/workers/worker_upscale.py",
    "src/workers/worker_effects.py",
    "src/workers/worker_background.py",
]

REQUIRED_FILES = [
    "requirements.txt",
    "install.sh",
    "uninstall.sh",
    "pyproject.toml",
    "src/main.py",
]

FORBIDDEN_DIRS = ["src/tools", "src/scripts", "tools", "Luna-main"]


def check_structure():
    errors = []
    root = os.getcwd()

    for d in REQUIRED_DIRS:
        if not os.path.exists(os.path.join(root, d)):
            errors.append(f"MISSING DIR: {d}/")

    for f in REQUIRED_WORKERS:
        if not os.path.exists(os.path.join(root, f)):
            errors.append(f"MISSING WORKER: {f}")

    for f in REQUIRED_FILES:
        if not os.path.exists(os.path.join(root, f)):
            errors.append(f"MISSING FILE: {f}")

    for d in FORBIDDEN_DIRS:
        if os.path.exists(os.path.join(root, d)):
            errors.append(f"FORBIDDEN: {d}/ (remover ou mover conteudo)")

    if os.path.exists(os.path.join(root, "src")):
        for f in os.listdir(os.path.join(root, "src")):
            if f.endswith(".py") and f.startswith("worker_"):
                errors.append(f"MISPLACED: src/{f} (mover para src/workers/)")
            if f.endswith(".txt") and f.startswith("requirements"):
                errors.append(f"MISPLACED: src/{f} (usar requirements.txt na raiz)")

    if errors:
        print("Violacoes de Estrutura do Projeto:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Estrutura do projeto valida.")
    return 0


if __name__ == "__main__":
    sys.exit(check_structure())

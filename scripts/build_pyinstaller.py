#!/usr/bin/env python3
"""
Build script for PyInstaller packaging.

Scans the source tree to collect hidden imports for packages that use
pkgutil.iter_modules for dynamic discovery (collect_submodules cannot be
used because importing those packages triggers argparse at module level).
"""
import os
import subprocess
import sys


def scan_hidden_imports(src_root: str, packages: list[str]) -> list[str]:
    """Walk package directories and return dotted module names without importing them."""
    hidden = []
    for package in packages:
        pkg_path = os.path.join(src_root, package.replace(".", os.sep))
        for dirpath, dirs, files in os.walk(pkg_path):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            rel = os.path.relpath(dirpath, src_root)
            dotted = rel.replace(os.sep, ".")
            for f in files:
                if f.endswith(".py") and f != "__init__.py":
                    hidden.append(f"{dotted}.{f[:-3]}")
    return hidden


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_root = os.path.join(repo_root, "src")

    hidden_imports = scan_hidden_imports(src_root, [
        "fourier_grx.algorithm",
        "fourier_grx.task",
    ])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--collect-all=numpy",
        "--collect-all=scipy",
        "--collect-all=qpsolvers",
        "--collect-all=proxsuite",
        "--collect-all=osqp",
        "--collect-all=piqp",
        "--hidden-import=piqp",
        "--hidden-import=numpy",
        "--hidden-import=scipy",
        "--hidden-import=osqp",
    ]

    for mod in hidden_imports:
        cmd.append(f"--hidden-import={mod}")
    cmd.append(os.path.join(repo_root, "release", "run.py"))

    print(f"[build_pyinstaller] {len(hidden_imports)} hidden imports collected")
    sys.exit(subprocess.call(cmd, cwd=repo_root))


if __name__ == "__main__":
    main()

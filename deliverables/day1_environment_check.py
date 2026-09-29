"""
NovaGates Onboarding - Day 1 Environment Health Check
Validates core developer tooling and runtime availability.
"""

import shutil
import subprocess
import sys


def check_tool(name: str, cmd: list[str]) -> dict:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            version_str = (
                result.stdout.strip().splitlines()[0] if result.stdout else "Available"
            )
            return {"installed": True, "details": version_str}
    except Exception as e:
        return {"installed": False, "details": str(e)}

    # Fallback checking binary on PATH
    path = shutil.which(name)
    if path:
        return {"installed": True, "details": f"Found at {path}"}
    return {"installed": False, "details": "Not found in PATH"}


def main():
    print("=" * 60)
    print(" NovaGates Backend & AI Developer — Day 1 Environment Audit ")
    print("=" * 60)

    checks = {
        "Python": [sys.executable, "--version"],
        "uv (Package Manager)": [sys.executable, "-m", "uv", "--version"],
        "Git": ["git", "--version"],
        "Docker": ["docker", "--version"],
    }

    results = {}
    for name, cmd in checks.items():
        res = check_tool(name, cmd)
        status_symbol = "[OK]    " if res["installed"] else "[MISSING]"
        print(f"{status_symbol} {name:<22}: {res['details']}")
        results[name] = res

    print("-" * 60)
    if results["Docker"]["installed"]:
        print("[SUCCESS] Core runtime environment ready.")
    else:
        print(
            "[NOTICE] Next Step: Install Docker Desktop to run MongoDB/Redis containers locally."
        )
    print("=" * 60)


if __name__ == "__main__":
    main()

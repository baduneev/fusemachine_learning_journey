"""Check the exact Week 16 files selected for a Git commit before publishing."""

import argparse
import io
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import zipfile


PROJECT = "Week16_Assignment_Neev_Badu/Engineering_AI_System/"
BLOCKED_PARTS = {".venv", "venv", "__pycache__", "runs", "chroma_db"}
BLOCKED_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}
KEY_PATTERNS = {
    "Google API key pattern": re.compile(rb"AIza[0-9A-Za-z_-]{35}"),
    "OpenAI API key pattern": re.compile(rb"sk-[A-Za-z0-9_-]{20,}"),
    "private key block": re.compile(rb"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----"),
}


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True).stdout


def scan_bytes(name, data, secrets, problems):
    if any(value in data for value in secrets):
        problems.append(f"{name}: contains a value from local .env")
    for label, pattern in KEY_PATTERNS.items():
        if pattern.search(data):
            problems.append(f"{name}: matches {label}")
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for member in archive.infolist():
                if member.is_dir() or member.file_size > 10_000_000:
                    continue
                scan_bytes(f"{name}!{member.filename}", archive.read(member), secrets, problems)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--staged", action="store_true", help="Check the exact Git index before committing")
    group.add_argument("--working-tree", action="store_true", help="Preview project files Git would add")
    args = parser.parse_args()

    root = Path(git("rev-parse", "--show-toplevel").decode().strip())
    env_path = root / PROJECT / ".env"
    secrets = []
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            if "=" not in line or line.lstrip().startswith("#"):
                continue
            name, value = line.split("=", 1)
            if re.search(r"KEY|TOKEN|SECRET|PASSWORD", name, re.I):
                value = value.strip().strip('"\'')
                if len(value) >= 8:
                    secrets.append(value.encode("utf-8"))

    if args.staged:
        names = git("diff", "--cached", "--name-only", "-z").split(b"\0")
    else:
        names = git("ls-files", "--cached", "--others", "--exclude-standard", "-z", "--", PROJECT).split(b"\0")
    paths = [item.decode("utf-8", "surrogateescape") for item in names if item]
    if not paths:
        raise SystemExit("No files selected; stage the Week 16 project first.")

    problems = []
    for name in paths:
        parts = PurePosixPath(name).parts
        base = parts[-1]
        if not name.startswith(PROJECT):
            problems.append(f"{name}: outside the Week 16 project")
            continue
        if (base == ".env" or base.startswith(".env.") and base != ".env.example"
                or any(part in BLOCKED_PARTS for part in parts)
                or PurePosixPath(base).suffix.lower() in BLOCKED_SUFFIXES):
            problems.append(f"{name}: private or generated path")
            continue
        try:
            data = git("show", f":{name}") if args.staged else (root / name).read_bytes()
        except (subprocess.CalledProcessError, FileNotFoundError):
            problems.append(f"{name}: staged deletion or unavailable blob")
            continue
        scan_bytes(name, data, secrets, problems)

    if problems:
        for problem in problems:
            print("BLOCKED:", problem, file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS: {len(paths)} Week 16 files checked; no configured key or known credential pattern found.")


if __name__ == "__main__":
    main()

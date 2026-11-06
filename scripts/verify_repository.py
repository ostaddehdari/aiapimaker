"""Stage 02 repository shape and high-risk filename checks (stdlib only)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = (
    "README.md",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    ".gitignore",
    ".env.example",
    ".github/CODEOWNERS",
    ".github/workflows/verify.yml",
    ".github/ISSUE_TEMPLATE/stage-work.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "docs/ROADMAP-40-STAGES.md",
    "docs/ARCHITECTURE.md",
    "docs/STAGE-EXIT-CRITERIA.md",
    "backend/README.md",
    "frontend/README.md",
    "workers/README.md",
    "connectors/README.md",
    "infra/README.md",
    "tests/README.md",
)

DENIED_BASENAMES = {
    ".env",
    "auth.json",
    "credentials.json",
    "cookies.json",
    "storage-state.json",
    "storagestate.json",
}
DENIED_SUFFIXES = {".pem", ".p12", ".pfx", ".key"}
EXCLUDED_DIRECTORIES = {".git", "node_modules", ".venv", "__pycache__"}


def check_markdown_fences() -> list[str]:
    """Detect unmatched fenced Markdown blocks in checked-in documentation."""
    errors: list[str] = []
    for path in ROOT.rglob("*.md"):
        if set(path.relative_to(ROOT).parts) & EXCLUDED_DIRECTORIES:
            continue
        opened_at: int | None = None
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.lstrip().startswith("```"):
                opened_at = number if opened_at is None else None
        if opened_at is not None:
            errors.append(f"UNCLOSED MARKDOWN FENCE: {path.relative_to(ROOT)}:{opened_at}")
    return errors


def main() -> int:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    if missing:
        for item in missing:
            print(f"MISSING: {item}")
        return 1

    risky: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or set(path.relative_to(ROOT).parts) & EXCLUDED_DIRECTORIES:
            continue
        name = path.name.lower()
        if name in DENIED_BASENAMES or path.suffix.lower() in DENIED_SUFFIXES:
            risky.append(str(path.relative_to(ROOT)))
        if name.startswith(".env.") and name != ".env.example":
            risky.append(str(path.relative_to(ROOT)))

    risky.extend(check_markdown_fences())

    if risky:
        for item in sorted(set(risky)):
            print(f"UNSAFE FILE: {item}")
        return 1

    print(f"REPOSITORY_STRUCTURE_PASS: {len(REQUIRED)} expected files; no denied files or unclosed Markdown fences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

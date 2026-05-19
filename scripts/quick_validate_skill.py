#!/usr/bin/env python3
"""Self-contained baseline validator for portable agent skills."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
MAX_SKILL_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024


def validate_skill(skill_path: Path) -> tuple[bool, str]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()
    if not content.startswith("---\n"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return False, f"Invalid YAML in frontmatter: {exc}"

    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary"

    unexpected = set(frontmatter) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        allowed = ", ".join(sorted(ALLOWED_FRONTMATTER_KEYS))
        return False, f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}. Allowed: {allowed}"

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        return False, "Missing or invalid 'name' in frontmatter"
    if not re.fullmatch(r"[a-z0-9-]+", name):
        return False, f"Name '{name}' should be hyphen-case"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    if len(name) > MAX_SKILL_NAME_LENGTH:
        return False, f"Name is too long ({len(name)} characters). Maximum is {MAX_SKILL_NAME_LENGTH}."

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        return False, "Missing or invalid 'description' in frontmatter"
    if "<" in description or ">" in description:
        return False, "Description cannot contain angle brackets"
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Description is too long ({len(description)} characters). Maximum is {MAX_DESCRIPTION_LENGTH}."

    return True, "Skill is valid!"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python quick_validate_skill.py <skill_directory>")
        raise SystemExit(1)

    valid, message = validate_skill(Path(sys.argv[1]))
    print(message)
    raise SystemExit(0 if valid else 1)


if __name__ == "__main__":
    main()

from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
EXPECTED_SKILLS = {
    "deploy-to-heroku",
    "heroku-addons",
    "heroku-app-ops",
    "heroku-applink-connections",
    "heroku-applink-publications",
    "heroku-config-vars",
    "heroku-connect",
    "heroku-domains-tls",
    "heroku-key-value-store",
    "heroku-logging-drains",
    "heroku-managed-inference",
    "heroku-pipelines-review-apps",
    "heroku-postgres",
    "heroku-slack-agents",
}


def parse_frontmatter(path: Path) -> dict[str, str]:
    content = path.read_text()
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    assert match, f"{path} is missing valid frontmatter"

    payload: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip()
    return payload


def test_skill_directories_match_expected_set() -> None:
    actual = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}
    assert actual == EXPECTED_SKILLS


def test_every_skill_has_minimal_frontmatter_and_agents_metadata() -> None:
    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
        if not skill_dir.is_dir():
            continue

        frontmatter = parse_frontmatter(skill_dir / "SKILL.md")
        assert set(frontmatter) == {"name", "description"}
        assert frontmatter["name"] == skill_dir.name
        assert "use when" in frontmatter["description"].lower()

        agents_path = skill_dir / "agents" / "openai.yaml"
        assert agents_path.exists(), f"{skill_dir.name} missing agents/openai.yaml"

        agents_payload = yaml.safe_load(agents_path.read_text())
        interface = agents_payload["interface"]
        assert interface["display_name"]
        assert interface["short_description"]
        assert interface["icon_small"] == "./assets/heroku-mark-dark-rgb.svg"
        assert interface["icon_large"] == "./assets/heroku-logo-dark-rgb.svg"
        assert interface["brand_color"] == "#D7BFF2"
        assert interface["default_prompt"].startswith(f"Use ${skill_dir.name}")
        assert (skill_dir / "assets" / "heroku-mark-dark-rgb.svg").exists()
        assert (skill_dir / "assets" / "heroku-logo-dark-rgb.svg").exists()

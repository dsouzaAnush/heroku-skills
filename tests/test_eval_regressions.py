from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_eval_module():
    spec = importlib.util.spec_from_file_location(
        "evaluate_skills",
        REPO_ROOT / "scripts" / "evaluate_skills.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_eval_report_meets_repo_thresholds() -> None:
    evaluate_skills = load_eval_module()
    report = evaluate_skills.evaluate(REPO_ROOT, REPO_ROOT / "evals" / "skill_usefulness.json")

    thresholds = report["thresholds"]
    summary = report["summary"]

    assert summary["coverage_failure_count"] == 0
    assert summary["top1_rate"] >= thresholds["global_min_top1"]
    assert summary["top3_rate"] >= thresholds["global_min_top3"]
    assert summary["contrast_rate"] >= thresholds["global_min_contrast"]

    for skill_name, item in report["per_skill_summary"].items():
        assert item["top1_rate"] >= thresholds["per_skill_min_top1"], skill_name


def test_eval_disambiguates_known_overlap_prompts() -> None:
    evaluate_skills = load_eval_module()
    skills_root = REPO_ROOT / "skills"
    skill_sections = {
        skill_dir.name: evaluate_skills.load_skill_sections(skill_dir)
        for skill_dir in sorted(skills_root.iterdir())
        if skill_dir.is_dir()
    }
    token_idf = evaluate_skills.compute_token_idf(skill_sections)

    cases = {
        "Plan a safe Heroku log forwarding change without leaking secrets to a drain target.": "heroku-logging-drains",
        "Inspect Heroku AppLink connection setup between this app and Salesforce.": "heroku-applink-connections",
        "I need guidance for AppLink publication workflows on Heroku.": "heroku-applink-publications",
        "Show me app info and current process state for this Heroku app.": "heroku-app-ops",
    }

    for prompt, expected_skill in cases.items():
        ranked = evaluate_skills.rank_prompt(prompt, skill_sections, token_idf)
        assert ranked[0]["skill"] == expected_skill, prompt

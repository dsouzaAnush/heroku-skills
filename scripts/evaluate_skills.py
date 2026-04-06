#!/usr/bin/env python3
"""Evaluate routing quality, coverage, and disambiguation for repo skills."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

import yaml


TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def load_frontmatter(skill_path: Path) -> dict[str, str]:
    content = skill_path.read_text()
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        raise RuntimeError(f"{skill_path}: missing or invalid frontmatter")

    payload: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip()
    return payload


def load_skill_sections(skill_dir: Path) -> dict[str, str]:
    skill_path = skill_dir / "SKILL.md"
    frontmatter = load_frontmatter(skill_path)
    body = skill_path.read_text()

    sections = {
        "name": skill_dir.name.replace("-", " "),
        "description": frontmatter.get("description", ""),
        "body": body,
        "agents": "",
        "references": "",
        "scripts": "",
    }

    agents_path = skill_dir / "agents" / "openai.yaml"
    if agents_path.exists():
        agents_data = yaml.safe_load(agents_path.read_text()) or {}
        interface = agents_data.get("interface", {})
        sections["agents"] = "\n".join(
            [
                interface.get("display_name", ""),
                interface.get("short_description", ""),
                interface.get("default_prompt", "")
            ]
        )

    for file_path in sorted(skill_dir.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.name == "SKILL.md":
            continue
        if file_path.parts[-2] not in {"references", "scripts", "agents"}:
            continue
        try:
            if file_path.parts[-2] == "references":
                sections["references"] += "\n" + file_path.read_text()
            elif file_path.parts[-2] == "scripts":
                sections["scripts"] += "\n" + file_path.read_text()
        except UnicodeDecodeError:
            continue

    return sections


SECTION_WEIGHTS = {
    "name": 4.0,
    "description": 4.0,
    "agents": 3.0,
    "body": 1.5,
    "references": 0.75,
    "scripts": 0.25,
}


def compute_token_idf(skill_sections: dict[str, dict[str, str]]) -> dict[str, float]:
    skill_count = len(skill_sections)
    document_frequency: Counter[str] = Counter()

    for sections in skill_sections.values():
        combined_tokens = {
            token
            for section_text in sections.values()
            for token in tokenize(section_text)
        }
        document_frequency.update(combined_tokens)

    return {
        token: math.log((skill_count + 1) / (frequency + 1))
        for token, frequency in document_frequency.items()
    }


def overlap_score(
    prompt: str,
    skill_sections: dict[str, str],
    skill_name: str,
    token_idf: dict[str, float],
) -> float:
    prompt_tokens = tokenize(prompt)
    if not prompt_tokens:
        return 0.0

    prompt_counts = Counter(prompt_tokens)
    score = 0.0
    for section_name, section_text in skill_sections.items():
        skill_tokens = tokenize(section_text)
        if not skill_tokens:
            continue
        skill_counts = Counter(skill_tokens)
        shared = set(prompt_counts) & set(skill_counts)
        section_score = sum(
            min(prompt_counts[token], skill_counts[token]) * token_idf.get(token, 0.0)
            for token in shared
        )
        score += section_score * SECTION_WEIGHTS[section_name]

    name_bonus = 0.0
    for token in skill_name.split("-"):
        if token in prompt_counts:
            name_bonus += 1.5 * max(token_idf.get(token, 0.0), 0.5)
    return score + name_bonus


def rank_prompt(
    prompt: str,
    skill_sections: dict[str, dict[str, str]],
    token_idf: dict[str, float],
) -> list[dict[str, float | str]]:
    return sorted(
        (
            {
                "skill": candidate_name,
                "score": overlap_score(prompt, candidate_sections, candidate_name, token_idf),
            }
            for candidate_name, candidate_sections in skill_sections.items()
        ),
        key=lambda item: item["score"],
        reverse=True,
    )


def evaluate(repo_root: Path, spec_path: Path) -> dict:
    skills_root = repo_root / "skills"
    spec = json.loads(spec_path.read_text())
    skill_specs = spec["skills"]
    thresholds = spec.get("thresholds", {})

    skill_sections = {
        skill_dir.name: load_skill_sections(skill_dir)
        for skill_dir in sorted(skills_root.iterdir())
        if skill_dir.is_dir()
    }

    missing = set(skill_specs) - set(skill_sections)
    if missing:
        raise RuntimeError(f"Eval spec references unknown skills: {sorted(missing)}")

    token_idf = compute_token_idf(skill_sections)
    routing_results = []
    contrast_results = []
    coverage_failures = []
    per_skill_summary: dict[str, dict[str, float | int]] = {}

    for skill_name, config in skill_specs.items():
        sections = skill_sections[skill_name]
        combined_skill_text = "\n".join(sections.values())
        positive_prompts = config.get("prompts", [])
        contrast_prompts = config.get("contrast_prompts", [])

        for term in config.get("must_include", []):
            if term.lower() not in combined_skill_text.lower():
                coverage_failures.append(
                    {
                        "skill": skill_name,
                        "missing_term": term,
                    }
                )

        skill_top1_hits = 0
        skill_top3_hits = 0
        skill_contrast_hits = 0

        for prompt in positive_prompts:
            ranked = rank_prompt(prompt, skill_sections, token_idf)
            top = ranked[0]
            target_rank = next(
                index + 1 for index, item in enumerate(ranked) if item["skill"] == skill_name
            )
            if target_rank == 1:
                skill_top1_hits += 1
            if target_rank <= 3:
                skill_top3_hits += 1
            routing_results.append(
                {
                    "prompt": prompt,
                    "target_skill": skill_name,
                    "top_skill": top["skill"],
                    "target_rank": target_rank,
                    "top_score": top["score"],
                    "target_score": next(
                        item["score"] for item in ranked if item["skill"] == skill_name
                    ),
                }
            )

        for case in contrast_prompts:
            prompt = case["prompt"]
            must_beat = case["must_beat"]
            ranked = rank_prompt(prompt, skill_sections, token_idf)
            scores = {item["skill"]: item["score"] for item in ranked}
            target_score = scores[skill_name]
            beaten = {
                candidate: target_score > scores[candidate]
                for candidate in must_beat
            }
            passed = all(beaten.values())
            if passed:
                skill_contrast_hits += 1
            contrast_results.append(
                {
                    "prompt": prompt,
                    "target_skill": skill_name,
                    "must_beat": must_beat,
                    "passed": passed,
                    "target_score": target_score,
                    "comparisons": {
                        candidate: {
                            "target_score": target_score,
                            "candidate_score": scores[candidate],
                        }
                        for candidate in must_beat
                    },
                }
            )

        per_skill_summary[skill_name] = {
            "prompt_count": len(positive_prompts),
            "top1_hits": skill_top1_hits,
            "top3_hits": skill_top3_hits,
            "top1_rate": round(skill_top1_hits / len(positive_prompts), 3) if positive_prompts else 1.0,
            "top3_rate": round(skill_top3_hits / len(positive_prompts), 3) if positive_prompts else 1.0,
            "contrast_count": len(contrast_prompts),
            "contrast_hits": skill_contrast_hits,
            "contrast_rate": round(skill_contrast_hits / len(contrast_prompts), 3) if contrast_prompts else 1.0,
        }

    passed_top1 = sum(1 for item in routing_results if item["target_rank"] == 1)
    passed_top3 = sum(1 for item in routing_results if item["target_rank"] <= 3)
    passed_contrast = sum(1 for item in contrast_results if item["passed"])
    total = len(routing_results)
    total_contrast = len(contrast_results)

    return {
        "thresholds": thresholds,
        "summary": {
            "prompt_count": total,
            "top1_hits": passed_top1,
            "top3_hits": passed_top3,
            "contrast_count": total_contrast,
            "contrast_hits": passed_contrast,
            "top1_rate": round(passed_top1 / total, 3) if total else 0.0,
            "top3_rate": round(passed_top3 / total, 3) if total else 0.0,
            "contrast_rate": round(passed_contrast / total_contrast, 3) if total_contrast else 1.0,
            "coverage_failure_count": len(coverage_failures),
        },
        "per_skill_summary": per_skill_summary,
        "routing_results": routing_results,
        "contrast_results": contrast_results,
        "coverage_failures": coverage_failures,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        default="evals/skill_usefulness.json",
        help="Path to the eval specification file",
    )
    parser.add_argument(
        "--min-top1",
        type=float,
        default=None,
        help="Minimum acceptable top-1 routing rate",
    )
    parser.add_argument(
        "--min-top3",
        type=float,
        default=None,
        help="Minimum acceptable top-3 routing rate",
    )
    parser.add_argument(
        "--min-contrast",
        type=float,
        default=None,
        help="Minimum acceptable contrast/disambiguation pass rate",
    )
    parser.add_argument(
        "--min-per-skill-top1",
        type=float,
        default=None,
        help="Minimum acceptable per-skill top-1 routing rate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the full JSON report",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    report = evaluate(repo_root, (repo_root / args.spec).resolve())
    summary = report["summary"]
    thresholds = report["thresholds"]

    min_top1 = args.min_top1 if args.min_top1 is not None else thresholds.get("global_min_top1", 0.9)
    min_top3 = args.min_top3 if args.min_top3 is not None else thresholds.get("global_min_top3", 1.0)
    min_contrast = args.min_contrast if args.min_contrast is not None else thresholds.get("global_min_contrast", 1.0)
    min_per_skill_top1 = (
        args.min_per_skill_top1
        if args.min_per_skill_top1 is not None
        else thresholds.get("per_skill_min_top1", 0.75)
    )

    failed = False
    if summary["coverage_failure_count"] > 0:
        failed = True
    if summary["top1_rate"] < min_top1:
        failed = True
    if summary["top3_rate"] < min_top3:
        failed = True
    if summary["contrast_rate"] < min_contrast:
        failed = True
    for skill_name, item in report["per_skill_summary"].items():
        if item["top1_rate"] < min_per_skill_top1:
            failed = True

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(
            "Skill usefulness eval: "
            f"top1={summary['top1_hits']}/{summary['prompt_count']} ({summary['top1_rate']:.3f}), "
            f"top3={summary['top3_hits']}/{summary['prompt_count']} ({summary['top3_rate']:.3f}), "
            f"contrast={summary['contrast_hits']}/{summary['contrast_count']} ({summary['contrast_rate']:.3f}), "
            f"coverage_failures={summary['coverage_failure_count']}"
        )
        for failure in report["coverage_failures"]:
            print(
                f"coverage failure: {failure['skill']} is missing required term "
                f"{failure['missing_term']!r}"
            )
        for item in report["routing_results"]:
            if item["target_rank"] != 1:
                print(
                    "routing miss: "
                    f"prompt={item['prompt']!r} target={item['target_skill']} "
                    f"top={item['top_skill']} rank={item['target_rank']}"
                )
        for item in report["contrast_results"]:
            if not item["passed"]:
                print(
                    "contrast miss: "
                    f"prompt={item['prompt']!r} target={item['target_skill']} "
                    f"must_beat={', '.join(item['must_beat'])}"
                )
        for skill_name, item in report["per_skill_summary"].items():
            if item["top1_rate"] < min_per_skill_top1:
                print(
                    f"per-skill miss: {skill_name} top1_rate={item['top1_rate']:.3f} "
                    f"minimum={min_per_skill_top1:.3f}"
                )

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

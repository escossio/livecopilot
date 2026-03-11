#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvalQuery:
    category: str
    query: str
    mode: str


DEFAULT_BATTERY: list[EvalQuery] = [
    EvalQuery("continuidade_operacional", "continuidade", "hybrid"),
    EvalQuery("continuidade_operacional", "checkpoint da rodada", "hybrid"),
    EvalQuery("continuidade_operacional", "new chat context", "hybrid"),
    EvalQuery("estado_recente", "ultimo closeout", "hybrid"),
    EvalQuery("estado_recente", "smoke round continuity", "hybrid"),
    EvalQuery("estado_recente", "embedding maintenance", "hybrid"),
    EvalQuery("decisoes_projeto", "separacao question_bank knowledge", "hybrid"),
    EvalQuery("decisoes_projeto", "adotar 3 niveis de continuidade", "hybrid"),
    EvalQuery("decisoes_projeto", "comando padrao operador scripts round", "hybrid"),
    EvalQuery("riscos_bloqueios", "risco runuser postgres peer auth", "hybrid"),
    EvalQuery("riscos_bloqueios", "drift de embeddings", "hybrid"),
    EvalQuery("memoria_historica", "mvp continuidade", "semantic"),
    EvalQuery("memoria_historica", "fatos canonicos project_facts", "semantic"),
    EvalQuery("tecnico_semantico", "ranking debug score_final", "semantic"),
    EvalQuery("tecnico_semantico", "realtime", "semantic"),
    EvalQuery("tecnico_semantico", "knowledge_search ranking", "semantic"),
]


def _run_query(
    wrapper: Path,
    project: str,
    item: EvalQuery,
    facts_limit: int,
    memory_limit: int,
) -> dict[str, Any]:
    cmd = [
        str(wrapper),
        "--project",
        project,
        "--query",
        item.query,
        "--mode",
        item.mode,
        "--facts-limit",
        str(facts_limit),
        "--memory-limit",
        str(memory_limit),
        "--format",
        "json",
        "--debug-ranking",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"query failed ({item.query}): rc={proc.returncode} stderr={proc.stderr.strip() or '<empty>'}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        sample = (proc.stdout or "")[:300]
        raise RuntimeError(f"invalid json for query '{item.query}': {exc}; sample={sample!r}") from exc


def _build_debug_index(payload: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    idx: dict[tuple[str, int], dict[str, Any]] = {}
    for row in payload.get("ranking_debug", []) or []:
        kind = str(row.get("kind") or "")
        rid = row.get("id")
        if not kind or rid is None:
            continue
        try:
            idx[(kind, int(rid))] = row
        except Exception:
            continue
    return idx


def _top_results(payload: dict[str, Any], top_n: int) -> list[dict[str, Any]]:
    debug_idx = _build_debug_index(payload)
    out: list[dict[str, Any]] = []
    for rank, hit in enumerate((payload.get("semantic_hits") or [])[: max(1, top_n)], start=1):
        sid = int(hit.get("id"))
        dbg = debug_idx.get(("memory_chunk", sid), {})
        out.append(
            {
                "rank": rank,
                "id": sid,
                "run_id": hit.get("run_id"),
                "fact_id": hit.get("fact_id"),
                "memory_type": hit.get("memory_type"),
                "source_type": hit.get("source_type"),
                "source_path": hit.get("source_path"),
                "similarity": hit.get("similarity"),
                "score_original": dbg.get("score_original"),
                "type_weight": dbg.get("type_weight"),
                "recency_weight": dbg.get("recency_weight"),
                "score_final": dbg.get("score_final"),
                "excerpt": hit.get("excerpt"),
            }
        )
    return out


def _query_observations(
    category: str,
    mode: str,
    top_results: list[dict[str, Any]],
    memory_types_detected: list[str],
    semantic_warning: str | None,
) -> list[str]:
    obs: list[str] = []
    if semantic_warning:
        obs.append("semantic_warning_present")

    top3 = top_results[:3]
    top3_types = [str(item.get("memory_type") or "other") for item in top3]
    top5_types = [str(item.get("memory_type") or "other") for item in top_results]

    if top3_types:
        c3 = Counter(top3_types)
        dom_type, dom_count = c3.most_common(1)[0]
        if dom_count >= 3:
            obs.append(f"top3_dominated_by_{dom_type}")

    fact_count_top5 = sum(1 for t in top5_types if t == "fact")
    run_count_top5 = sum(1 for t in top5_types if t == "run_summary")
    chunk_count_top5 = sum(1 for t in top5_types if t == "memory_chunk")

    if category in {"continuidade_operacional", "estado_recente"} and fact_count_top5 == 0:
        obs.append("absence_of_fact_in_operational_query")

    if category == "decisoes_projeto" and chunk_count_top5 >= 3:
        obs.append("excess_memory_chunk_for_decision_query")

    if category in {"decisoes_projeto", "riscos_bloqueios"} and run_count_top5 >= 3 and fact_count_top5 == 0:
        obs.append("run_summary_dominates_where_fact_expected")

    if len(set(top5_types)) >= 2:
        obs.append("diversity_good")
    elif top5_types:
        obs.append("diversity_low")

    if mode == "hybrid" and "fact" not in memory_types_detected and not semantic_warning:
        obs.append("hybrid_without_fact_memory_type")

    return obs


def _aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_query_type_counter: dict[str, Counter[str]] = defaultdict(Counter)
    global_counter: Counter[str] = Counter()
    observations: Counter[str] = Counter()

    for row in results:
        mtypes = [str(item.get("memory_type") or "other") for item in row.get("top_results", [])]
        by_query_type_counter[row["query"]].update(mtypes)
        global_counter.update(mtypes)
        observations.update(row.get("observations", []))

    return {
        "memory_type_global_distribution": dict(sorted(global_counter.items())),
        "memory_type_distribution_by_query": {
            query: dict(sorted(counter.items()))
            for query, counter in sorted(by_query_type_counter.items())
        },
        "observation_distribution": dict(sorted(observations.items())),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Project Brain Ranking Offline Eval")
    lines.append("")
    lines.append(f"generated_at: {report['generated_at']}")
    lines.append(f"project: {report['project']}")
    lines.append(f"wrapper: `{report['wrapper']}`")
    lines.append(f"queries: {len(report['results'])}")
    lines.append("")

    lines.append("## Ranking Baseline Inspected")
    lines.append("")
    lines.append("- type weights: decision=1.5, milestone=1.3, risk=1.2, fact_default=1.1, run_summary=1.0, chunk/other=0.8")
    lines.append("- recency: exp(-days_since/30)")
    lines.append("- diversity: max_share per type in top-N (semantic hits=0.25, facts merge=0.7)")
    lines.append("- debug ranking available via `--debug-ranking`")
    lines.append("- useful JSON fields: semantic_hits.memory_type/source_type/similarity, ranking_debug(score_*)")
    lines.append("")

    lines.append("## Consolidated Distribution")
    lines.append("")
    global_dist = report["aggregate"]["memory_type_global_distribution"]
    if global_dist:
        for key, value in global_dist.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- (no semantic hits captured)")

    lines.append("")
    lines.append("## Observation Signals")
    lines.append("")
    obs_dist = report["aggregate"].get("observation_distribution", {})
    if obs_dist:
        for key, value in obs_dist.items():
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- (none)")

    lines.append("")
    lines.append("## Query Results")
    lines.append("")

    for row in report["results"]:
        lines.append(f"### [{row['category']}] {row['query']} ({row['mode']})")
        lines.append("")
        lines.append(f"- semantic_warning: {row.get('semantic_warning')}")
        lines.append(f"- memory_types_detected: {row.get('memory_types_detected')}")
        lines.append(f"- observations: {row.get('observations')}")
        lines.append("")
        lines.append("Top 5 semantic hits:")
        lines.append("")
        lines.append("| rank | memory_type | source_type | sim | score_final | type_w | recency_w | path |")
        lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | --- |")
        if not row.get("top_results"):
            lines.append("| - | - | - | - | - | - | - | - |")
        else:
            for item in row["top_results"]:
                path = str(item.get("source_path") or "")
                lines.append(
                    "| "
                    f"{item.get('rank')} | "
                    f"{item.get('memory_type')} | "
                    f"{item.get('source_type')} | "
                    f"{item.get('similarity')} | "
                    f"{item.get('score_final')} | "
                    f"{item.get('type_weight')} | "
                    f"{item.get('recency_weight')} | "
                    f"{path} |"
                )
        lines.append("")

    lines.append("## Calibration Hints (No Weight Change Applied)")
    lines.append("")
    lines.append("- If `top3_dominated_by_*` is frequent: tighten diversity cap or add per-category rules.")
    lines.append("- If `absence_of_fact_in_operational_query` appears: increase fact prior in hybrid for operational categories.")
    lines.append("- If `run_summary_dominates_where_fact_expected` appears: reduce run_summary baseline in merge stage.")
    lines.append("- If decision queries over-return chunks: add stronger fact_type bias for decision/risk intents.")
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline eval for Project Brain ranking quality")
    parser.add_argument("--project", default="livecopilot")
    parser.add_argument(
        "--wrapper",
        default="/lab/projects/livecopilot/scripts/project_brain_query.sh",
        help="operational wrapper path",
    )
    parser.add_argument(
        "--output-dir",
        default="/lab/projects/livecopilot/docs/continuity/evals",
        help="directory for json/md reports",
    )
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--facts-limit", type=int, default=8)
    parser.add_argument("--memory-limit", type=int, default=8)
    parser.add_argument(
        "--queries-file",
        default=None,
        help="optional JSON list of {category,query,mode}",
    )
    args = parser.parse_args()

    wrapper = Path(args.wrapper)
    if not wrapper.is_file():
        print(f"ERROR: wrapper not found: {wrapper}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    battery: list[EvalQuery] = DEFAULT_BATTERY
    if args.queries_file:
        raw = json.loads(Path(args.queries_file).read_text(encoding="utf-8"))
        battery = [
            EvalQuery(str(item["category"]), str(item["query"]), str(item.get("mode", "hybrid")))
            for item in raw
        ]

    results: list[dict[str, Any]] = []
    for item in battery:
        payload = _run_query(
            wrapper=wrapper,
            project=args.project,
            item=item,
            facts_limit=max(1, args.facts_limit),
            memory_limit=max(1, args.memory_limit),
        )
        top_results = _top_results(payload, top_n=max(1, args.top_n))
        observations = _query_observations(
            category=item.category,
            mode=item.mode,
            top_results=top_results,
            memory_types_detected=list(payload.get("memory_types_detected") or []),
            semantic_warning=payload.get("semantic_warning"),
        )
        results.append(
            {
                "category": item.category,
                "query": item.query,
                "mode": item.mode,
                "semantic_warning": payload.get("semantic_warning"),
                "memory_types_detected": payload.get("memory_types_detected") or [],
                "top_results": top_results,
                "observations": observations,
            }
        )

    generated_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report: dict[str, Any] = {
        "generated_at": generated_at,
        "project": args.project,
        "wrapper": str(wrapper),
        "settings": {
            "top_n": max(1, args.top_n),
            "facts_limit": max(1, args.facts_limit),
            "memory_limit": max(1, args.memory_limit),
            "queries_count": len(results),
        },
        "queries": [
            {"category": item.category, "query": item.query, "mode": item.mode}
            for item in battery
        ],
        "results": results,
    }
    report["aggregate"] = _aggregate(results)

    json_path = output_dir / f"project_brain_ranking_eval_{generated_at}.json"
    md_path = output_dir / f"project_brain_ranking_eval_{generated_at}.md"
    latest_json = output_dir / "latest_project_brain_ranking_eval.json"
    latest_md = output_dir / "latest_project_brain_ranking_eval.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_render_markdown(report), encoding="utf-8")
    latest_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    latest_md.write_text(_render_markdown(report), encoding="utf-8")

    print("PROJECT BRAIN OFFLINE EVAL: OK")
    print(f"project: {args.project}")
    print(f"queries: {len(results)}")
    print(f"json_report: {json_path}")
    print(f"md_report: {md_path}")
    print(f"latest_json: {latest_json}")
    print(f"latest_md: {latest_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

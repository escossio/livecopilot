#!/usr/bin/env python3
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean


def _load_ndjson(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def _load_json(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_\-]{3,}", (text or "").lower())


def _as_float(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _as_int(value, default=0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _join_eval_with_telemetry(eval_rows: list[dict], telemetry_rows: list[dict]) -> list[dict]:
    latest_by_query: dict[str, dict] = {}
    for row in telemetry_rows:
        query = str(row.get("query", "") or "").strip().lower()
        if not query:
            continue
        latest_by_query[query] = row

    joined: list[dict] = []
    for item in eval_rows:
        query = str(item.get("query", "") or "").strip()
        if not query:
            continue
        telemetry = latest_by_query.get(query.lower(), {})
        joined.append(
            {
                "query": query,
                "expected_domain": str(item.get("expected_domain", "") or "").strip().lower(),
                "context_len": _as_int(telemetry.get("context_len", 0), 0),
                "result_count": _as_int(telemetry.get("result_count", 0), 0),
                "semantic_api_ok": bool(telemetry.get("semantic_api_ok", False)),
            }
        )
    return joined


def main() -> int:
    parser = argparse.ArgumentParser(description="Sugere ajustes simples de semantic policy (offline, sem aplicar)")
    parser.add_argument(
        "--telemetry",
        default="/lab/projects/livecopilot/var/semantic_telemetry.ndjson",
        help="Arquivo NDJSON de telemetria",
    )
    parser.add_argument(
        "--policy",
        default="/lab/projects/livecopilot/config/semantic_policy.json",
        help="Policy semantica atual",
    )
    parser.add_argument(
        "--eval",
        default="/lab/projects/livecopilot/scripts/eval_queries.json",
        help="Dataset de eval opcional para rotular in/out-of-scope",
    )
    args = parser.parse_args()

    telemetry_path = Path(args.telemetry)
    policy_path = Path(args.policy)
    eval_path = Path(args.eval)

    telemetry_rows = _load_ndjson(telemetry_path)
    policy = _load_json(policy_path) or {}
    eval_data = _load_json(eval_path)
    eval_rows = eval_data if isinstance(eval_data, list) else []

    relevance_floor = _as_float(policy.get("relevance_floor", 0.25), 0.25)
    context_limit = max(_as_int(policy.get("context_limit", 3), 3), 1)
    domain_signals = [str(x).lower() for x in policy.get("domain_signals_primary", []) if str(x).strip()]

    print("semantic_policy_tuner (offline)")
    print(f"telemetry_file: {telemetry_path}")
    print(f"policy_file: {policy_path}")
    print(f"eval_file: {eval_path} (loaded={bool(eval_rows)})")
    print(f"telemetry_rows: {len(telemetry_rows)}")

    if not telemetry_rows:
        print("\nSugestoes")
        print("- sem telemetria suficiente; manter policy atual por enquanto")
        return 0

    context_lens = [_as_int(r.get("context_len", 0), 0) for r in telemetry_rows]
    result_counts = [_as_int(r.get("result_count", 0), 0) for r in telemetry_rows]
    zero_context_rate = sum(1 for x in context_lens if x == 0) / len(context_lens)
    avg_context_len = mean(context_lens)
    avg_result_count = mean(result_counts)

    print("\nResumo")
    print(f"- zero_context_rate: {zero_context_rate:.2%}")
    print(f"- avg_context_len: {avg_context_len:.2f}")
    print(f"- avg_result_count: {avg_result_count:.2f}")

    suggestions: list[str] = []

    if zero_context_rate > 0.70:
        suggestions.append(
            f"relevance_floor: avaliar reduzir de {relevance_floor:.2f} para {max(relevance_floor - 0.05, 0.0):.2f} (muitos casos sem contexto)"
        )
    elif zero_context_rate < 0.20 and avg_context_len > 550:
        suggestions.append(
            f"relevance_floor: avaliar subir de {relevance_floor:.2f} para {min(relevance_floor + 0.05, 0.95):.2f} (contexto amplo com pouca rejeicao)"
        )
    else:
        suggestions.append(f"relevance_floor: manter em {relevance_floor:.2f} (sinal neutro nesta amostra)")

    if avg_result_count >= max(context_limit - 0.1, 1.0) and avg_context_len < 260:
        suggestions.append(
            f"context_limit: avaliar subir de {context_limit} para {context_limit + 1} (limit frequentemente saturado com contexto curto)"
        )
    elif avg_context_len > 900 and context_limit > 1:
        suggestions.append(
            f"context_limit: avaliar reduzir de {context_limit} para {context_limit - 1} (contexto potencialmente excessivo)"
        )
    else:
        suggestions.append(f"context_limit: manter em {context_limit} (sem indicio forte de ajuste)")

    joined = _join_eval_with_telemetry(eval_rows, telemetry_rows) if eval_rows else []
    if joined:
        out_with_context = [r for r in joined if r["expected_domain"] == "out_of_scope" and r["context_len"] > 0]
        in_without_context = [r for r in joined if r["expected_domain"] != "out_of_scope" and r["context_len"] == 0]

        noise_tokens = Counter()
        missing_tokens = Counter()
        for row in out_with_context:
            for token in _tokenize(row["query"]):
                if token not in domain_signals:
                    noise_tokens[token] += 1
        for row in in_without_context:
            for token in _tokenize(row["query"]):
                if token not in domain_signals:
                    missing_tokens[token] += 1

        top_noise = [k for k, _ in noise_tokens.most_common(5)]
        top_missing = [k for k, _ in missing_tokens.most_common(5)]

        print("\nEval join")
        print(f"- out_of_scope_with_context: {len(out_with_context)}")
        print(f"- in_scope_without_context: {len(in_without_context)}")

        if top_noise:
            suggestions.append(
                "sinais de dominio: revisar fronteira com termos ruidosos (candidatos para adjacent_technical_signals): "
                + ", ".join(top_noise)
            )
        if top_missing:
            suggestions.append(
                "sinais de dominio: avaliar ampliar domain_signals_primary com termos recorrentes sem contexto: "
                + ", ".join(top_missing)
            )
        if not top_noise and not top_missing:
            suggestions.append("sinais de dominio: manter listas atuais (eval sem desvio forte)")
    else:
        suggestions.append("sinais de dominio: sem eval rotulado suficiente; manter listas atuais por enquanto")

    print("\nSugestoes")
    for item in suggestions:
        print(f"- {item}")

    print("\nAcao")
    print("- nenhuma alteracao automatica aplicada nesta rodada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

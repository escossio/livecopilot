import argparse
import json

from app.services.gap_priority_queue import get_gap_report, rebuild_mismatch_baseline, record_gap_analysis
from app.services.knowledge_gap_analyzer import analyze_knowledge_gap


def _main() -> None:
    parser = argparse.ArgumentParser(description="Fila de priorizacao de lacunas para ingestao de conhecimento")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_record = subparsers.add_parser("record", help="Executa analise de gap e registra na fila")
    parser_record.add_argument("query", help="Tema/pergunta para analisar")
    parser_record.add_argument("--track", default="python", help="Trilha de certificacao")
    parser_record.add_argument("--pretty", action="store_true", help="Imprime JSON com identacao")

    parser_report = subparsers.add_parser("report", help="Consulta prioridades acumuladas")
    parser_report.add_argument("--track", default="", help="Filtra por trilha")
    parser_report.add_argument("--top", type=int, default=10, help="Quantidade maxima por lista")
    parser_report.add_argument(
        "--section",
        choices=[
            "all",
            "gaps",
            "topics",
            "domains",
            "certifications",
            "tags",
            "tags-technology",
            "tags-domain",
            "tags-subtheme",
            "mismatches",
            "mismatch-current",
            "mismatch-top",
        ],
        default="all",
        help="Recorte da consulta para planejamento de ingestao",
    )
    parser_report.add_argument("--pretty", action="store_true", help="Imprime JSON com identacao")

    parser_rebuild = subparsers.add_parser(
        "rebuild-mismatch-baseline",
        help="Recalcula mismatch no historico usando apenas a regra atual",
    )
    parser_rebuild.add_argument("--pretty", action="store_true", help="Imprime JSON com identacao")

    args = parser.parse_args()
    if args.command == "record":
        analysis = analyze_knowledge_gap(args.query, track=args.track)
        persisted = record_gap_analysis(analysis)
        output = {
            "analysis": analysis,
            "persisted": persisted,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
        return

    if args.command == "rebuild-mismatch-baseline":
        output = rebuild_mismatch_baseline()
        print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
        return

    report = get_gap_report(track=args.track or None, top=max(1, args.top))
    if args.section != "all":
        section_map = {
            "gaps": "most_frequent_gaps",
            "topics": "recommended_ingestion_topics",
            "domains": "grouped_by_domain",
            "certifications": "grouped_by_certification",
            "tags": "top_gap_tags",
            "tags-technology": "grouped_by_tag.technology",
            "tags-domain": "grouped_by_tag.domain",
            "tags-subtheme": "grouped_by_tag.subtheme",
            "mismatches": "mismatch_records",
            "mismatch-current": "current_mismatch_records",
            "mismatch-top": "top_mismatches",
        }
        key = section_map.get(args.section, "")
        if key.startswith("grouped_by_tag."):
            grouped_by_tag = report.get("grouped_by_tag", {})
            tag_type = key.split(".", 1)[1]
            selected_items = grouped_by_tag.get(tag_type, []) if isinstance(grouped_by_tag, dict) else []
        else:
            selected_items = report.get(key, [])
        report = {
            "track_filter": report.get("track_filter", ""),
            "history_count": report.get("history_count", 0),
            "queue_count": report.get("queue_count", 0),
            "section": args.section,
            "items": selected_items,
            "source_files": report.get("source_files", {}),
        }
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None))


if __name__ == "__main__":
    _main()

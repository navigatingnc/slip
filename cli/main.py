"""SLIP CLI — Entry point for the Slip friction detection system.

Phase 3: basic detect output.
Phase 5: --score flag for ranked opportunities.
Phase 18: --save flag to persist a full SlipReport to data/; fix exit code.
Phase 19: --list flag to display a summary of all persisted SlipReports.
Phase 20: --clear flag to delete all persisted SlipReports.
Phase 23: --export-id flag to export a saved report's opportunities to CSV by ID.
Phase 25: --summary flag to print aggregate statistics across all persisted reports.
Phase 27: --health flag to print operational metadata (version, report count, timestamp).
Phase 29: --version flag to print the version string and exit; bump _APP_VERSION to 0.29.0.
Phase 32: --file flag for batch signal ingestion from a JSON file.
"""
import argparse
import csv
import json
import sys
from collections import Counter
from datetime import datetime, timezone

from core import detect, score

_APP_VERSION = "0.32.0"


def _print_friction(results):
    print(f"Detected {len(results)} friction point(s):\n")
    for fp in results:
        print(f"  Pattern : {fp.pattern}")
        print(f"  Score   : {fp.score:.2f}")
        print(f"  Tags    : {', '.join(fp.tags)}")
        print(f"  Source  : {fp.source}")
        print(f"  Text    : {fp.description[:80]}{'...' if len(fp.description) > 80 else ''}")
        print()


def _print_opportunities(opportunities):
    from core.ideation import generate_concepts
    concepts = {bc.opportunity_title: bc for bc in generate_concepts(opportunities)}
    print(f"Ranked {len(opportunities)} opportunity/opportunities:\n")
    for i, opp in enumerate(opportunities, 1):
        bc = concepts.get(opp.title)
        print(f"  #{i} {opp.title}")
        print(f"     Composite Score     : {opp.composite_score:.3f}")
        print(f"     Severity            : {opp.severity:.3f}")
        print(f"     Frequency           : {opp.frequency:.3f}")
        print(f"     Automation Potential: {opp.automation_potential:.3f}")
        print(f"     Willingness to Pay  : {opp.willingness_to_pay:.3f}")
        print(f"     Market Size         : {opp.market_size:.3f}")
        print(f"     Signals             : {len(opp.friction_points)}")
        if bc:
            print(f"     Business Concept    : {bc.concept} ({bc.model})")
            print(f"     Rationale           : {bc.rationale[:100]}...")
        print()


def _print_report_list(reports):
    """Print a formatted summary table of persisted SlipReports."""
    if not reports:
        print("No saved reports found.")
        return
    print(f"{'ID/Timestamp':<22}  {'Signals':>7}  Top Opportunity")
    print("-" * 70)
    for r in reports:
        report_id = r.get("generated_at", "unknown")[:19].replace("T", " ")
        signal_count = r.get("signal_count", 0)
        top_opp = r.get("top_opportunity", "\u2014")
        print(f"  {report_id:<20}  {signal_count:>7}  {top_opp}")


def _print_aggregate_summary(reports):
    """Print aggregate statistics across all persisted SlipReports."""
    total_reports = len(reports)
    total_signals = sum(r.get("signal_count", 0) for r in reports)
    total_friction = sum(r.get("friction_count", 0) for r in reports)

    pattern_counter: Counter = Counter()
    opp_scores: dict = {}
    for r in reports:
        if r.get("top_pattern"):
            pattern_counter[r["top_pattern"]] += 1
        for opp in r.get("opportunities", []):
            title = opp.get("title", "")
            s = opp.get("composite_score", 0.0)
            if title and s > opp_scores.get(title, -1.0):
                opp_scores[title] = s

    top_patterns = [p for p, _ in pattern_counter.most_common(3)]
    top_opps = sorted(opp_scores, key=lambda t: opp_scores[t], reverse=True)[:3]

    print("SLIP — Aggregate Report Summary")
    print("=" * 40)
    print(f"  Total reports   : {total_reports}")
    print(f"  Total signals   : {total_signals}")
    print(f"  Total friction  : {total_friction}")
    print(f"  Top patterns    : {', '.join(top_patterns) if top_patterns else '—'}")
    print("  Top opportunities:")
    if top_opps:
        for i, title in enumerate(top_opps, 1):
            print(f"    #{i} {title}  (score: {opp_scores[title]:.3f})")
    else:
        print("    —")


def _print_health() -> None:
    """Print operational metadata: version, report count, and UTC timestamp."""
    from core.persistence import load_reports
    report_count = len(load_reports())
    checked_at = datetime.now(timezone.utc).isoformat()
    print("SLIP — Health Check")
    print("=" * 40)
    print("  Status        : ok")
    print("  Service       : slip-cli")
    print(f"  Version       : {_APP_VERSION}")
    print(f"  Report count  : {report_count}")
    print(f"  Checked at    : {checked_at}")


def _export_report_by_id(report_id: str, out_path: str) -> int:
    """Load a persisted report by ID and write its opportunities to a CSV.

    Returns 0 on success, 1 if the report is not found.
    """
    from core.persistence import load_report_by_id

    report = load_report_by_id(report_id)
    if report is None:
        print(f"Error: report '{report_id}' not found.", file=sys.stderr)
        return 1

    with open(out_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "Title", "Composite Score", "Severity", "Frequency",
            "Automation Potential", "Willingness to Pay", "Market Size",
            "Signal Count",
        ])
        for opp in report.get("opportunities", []):
            writer.writerow([
                opp.get("title", ""),
                opp.get("composite_score", ""),
                opp.get("severity", ""),
                opp.get("frequency", ""),
                opp.get("automation_potential", ""),
                opp.get("willingness_to_pay", ""),
                opp.get("market_size", ""),
                opp.get("signal_count", ""),
            ])

    print(f"Exported report '{report_id}' to {out_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="SLIP - System for Locating and Identifying Points of friction"
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="Text to analyze for friction (reads from stdin if omitted)",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="cli",
        help="Source label for the signal (default: cli)",
    )
    parser.add_argument(
        "--score",
        action="store_true",
        help="Also run the opportunity scorer and display ranked opportunities",
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="Export ranked opportunities to a CSV file (requires --score)",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Persist the full SlipReport to data/ after analysis",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all persisted SlipReports from data/ and exit",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Delete all persisted SlipReports from data/ and exit",
    )
    parser.add_argument(
        "--export-id",
        type=str,
        default=None,
        metavar="REPORT_ID",
        help="Export a saved report's opportunities to CSV by its ID and exit",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        metavar="FILE",
        help="Output CSV path for --export-id (default: slip_export_<id>.csv)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print aggregate statistics across all persisted SlipReports and exit",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Print operational metadata (version, report count, timestamp) and exit",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the SLIP version string and exit",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        metavar="JSON_FILE",
        help="Path to a JSON file containing an array of signal objects for batch analysis",
    )
    args = parser.parse_args()

    # --version bypasses analysis entirely
    if args.version:
        print(f"SLIP {_APP_VERSION}")
        sys.exit(0)

    # --health bypasses analysis entirely
    if args.health:
        _print_health()
        sys.exit(0)

    # --summary bypasses analysis entirely
    if args.summary:
        from core.persistence import load_reports
        reports = load_reports()
        _print_aggregate_summary(reports)
        sys.exit(0)

    # --list bypasses analysis entirely
    if args.list:
        from core.persistence import load_reports
        reports = load_reports()
        _print_report_list(reports)
        sys.exit(0)

    # --clear bypasses analysis entirely
    if args.clear:
        from core.persistence import clear_reports
        count = clear_reports()
        print(f"Cleared {count} saved report(s).")
        sys.exit(0)

    # --export-id bypasses analysis entirely
    if args.export_id:
        out_path = args.out or f"slip_export_{args.export_id}.csv"
        sys.exit(_export_report_by_id(args.export_id, out_path))

    # --file: batch signal ingestion from a JSON file
    if args.file:
        from core.report import generate_report
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                raw_signals = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Error reading '{args.file}': {exc}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(raw_signals, list) or not raw_signals:
            print("Error: JSON file must contain a non-empty array of signal objects.", file=sys.stderr)
            sys.exit(1)
        report = generate_report(raw_signals)
        print(f"Batch analysis: {report.signal_count} signal(s), "
              f"{report.friction_count} friction point(s) detected.")
        if report.opportunities:
            _print_opportunities(report.opportunities)
        else:
            print("No friction detected.")
        if args.save:
            from core.persistence import save_report
            filepath = save_report(report)
            print(f"Report saved to {filepath}")
        if args.export:
            from core.export import export_opportunities
            export_opportunities(report, args.export)
            print(f"Exported opportunities to {args.export}")
        sys.exit(0)

    if args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("SLIP - System for Locating and Identifying Points of friction")
        print("Usage: python -m cli.main --text 'your text here' [--score] [--save]")
        print("       echo 'your text' | python -m cli.main [--score] [--save]")
        print("       python -m cli.main --file signals.json [--save] [--export out.csv]")
        print("       python -m cli.main --version")
        print("       python -m cli.main --health")
        print("       python -m cli.main --summary")
        print("       python -m cli.main --list")
        print("       python -m cli.main --clear")
        print("       python -m cli.main --export-id <REPORT_ID> [--out FILE]")
        return

    friction_points = detect(text, source=args.source)

    if not friction_points:
        print("No friction detected.")
        sys.exit(0)

    _print_friction(friction_points)

    if args.score:
        opportunities = score(friction_points)
        _print_opportunities(opportunities)

        if args.export:
            from core.export import export_opportunities
            from core.report import generate_report
            report = generate_report([{"text": text, "source": args.source}])
            export_opportunities(report, args.export)
            print(f"Exported opportunities to {args.export}")

    if args.save:
        from core.persistence import save_report
        from core.report import generate_report
        report = generate_report([{"text": text, "source": args.source}])
        filepath = save_report(report)
        print(f"Report saved to {filepath}")

    sys.exit(0)


if __name__ == "__main__":
    main()

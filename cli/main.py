"""SLIP CLI - Entry point for the Slip friction detection system."""
import argparse
import sys
from core import detect, score


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
    print(f"Ranked {len(opportunities)} opportunity/opportunities:\n")
    for i, opp in enumerate(opportunities, 1):
        print(f"  #{i} {opp.title}")
        print(f"     Composite Score    : {opp.composite_score:.3f}")
        print(f"     Severity           : {opp.severity:.3f}")
        print(f"     Frequency          : {opp.frequency:.3f}")
        print(f"     Automation Potential: {opp.automation_potential:.3f}")
        print(f"     Signals            : {len(opp.friction_points)}")
        print()


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
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("SLIP - System for Locating and Identifying Points of friction")
        print("Phase 5: CLI with opportunity scoring active.")
        print("Usage: python -m cli.main --text 'your text here' [--score]")
        print("       echo 'your text' | python -m cli.main [--score]")
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
            from core.report import generate_report
            from core.export import export_opportunities
            # Re-generate full report for export structure
            report = generate_report([{"text": text, "source": args.source}])
            export_opportunities(report, args.export)
            print(f"Exported opportunities to {args.export}")

    sys.exit(1)


if __name__ == "__main__":
    main()

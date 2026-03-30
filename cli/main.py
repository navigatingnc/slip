"""SLIP CLI — Entry point for the Slip friction detection system.

Phase 3: basic detect output.
Phase 5: --score flag for ranked opportunities.
Phase 18: --save flag to persist a full SlipReport to data/; fix exit code.
"""
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
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print("SLIP - System for Locating and Identifying Points of friction")
        print("Usage: python -m cli.main --text 'your text here' [--score] [--save]")
        print("       echo 'your text' | python -m cli.main [--score] [--save]")
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

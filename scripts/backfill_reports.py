#!/usr/bin/env python3
"""Backfill LLM analysis reports for a range of past dates.

Replaces the old backfill_llm_analysis.py, add_llm_analysis.py, and
batch_llm_analysis.py scripts with a single config-driven wrapper.

Usage:
    python scripts/backfill_reports.py --start 2026-04-01 --end 2026-04-15
    python scripts/backfill_reports.py --start 2026-04-01  # end defaults to today
    python scripts/backfill_reports.py --start 2026-04-01 --dry-run
"""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def main():
    parser = argparse.ArgumentParser(description="Backfill LLM analysis reports")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--dry-run", action="store_true", help="Show dates without running")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                        help="Skip dates that already have llm_analysis (default: true)")
    args = parser.parse_args()

    start = datetime.strptime(args.start, "%Y-%m-%d")
    end = datetime.strptime(args.end, "%Y-%m-%d") if args.end else datetime.now()

    script = BASE_DIR / "scripts" / "generate_llm_analysis.py"
    if not script.exists():
        print(f"Error: {script} not found")
        sys.exit(1)

    current = start
    processed = 0
    skipped = 0

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        events_file = BASE_DIR / "data" / "events" / f"{date_str}.jsonl"

        if not events_file.exists():
            print(f"  [{date_str}] skip — no events file")
            skipped += 1
            current += timedelta(days=1)
            continue

        if args.skip_existing:
            import json
            daily_report = BASE_DIR / "site" / "data" / "reports" / "daily" / f"{date_str}.json"
            if daily_report.exists():
                with open(daily_report) as f:
                    report = json.load(f)
                if report.get("llm_analysis"):
                    print(f"  [{date_str}] skip — llm_analysis exists")
                    skipped += 1
                    current += timedelta(days=1)
                    continue

        if args.dry_run:
            print(f"  [{date_str}] would process")
        else:
            print(f"  [{date_str}] processing...")
            result = subprocess.run(
                [sys.executable, str(script), "--date", date_str],
                cwd=str(BASE_DIR),
            )
            if result.returncode != 0:
                print(f"  [{date_str}] ERROR (exit code {result.returncode})")
            else:
                processed += 1

        current += timedelta(days=1)

    print(f"\nDone: {processed} processed, {skipped} skipped")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

from .repair import create_corrected_workbook
from .report import render_html
from .server import serve
from .validator import validate_workbook, write_report


def main() -> None:
    parser = argparse.ArgumentParser(prog="mandros-blind")
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser("audit")
    audit.add_argument("--pdf", type=Path, required=True)
    audit.add_argument("--xlsx", type=Path, required=True)
    audit.add_argument("--out", type=Path, required=True)
    repair = sub.add_parser("repair-metformin")
    repair.add_argument("--out", type=Path, required=True)
    web = sub.add_parser("serve")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "audit":
        args.out.mkdir(parents=True, exist_ok=True)
        report = validate_workbook(args.pdf, args.xlsx)
        write_report(report, args.out / "assessment.json")
        render_html(report, args.out / "assessment.html")
        print(f"Decision: {report['decision']} | Score: {report['score']}/100 | Issues: {report['issue_count']}")
    elif args.command == "repair-metformin":
        create_corrected_workbook(args.out)
        print(args.out)
    else:
        serve(args.host, args.port)


if __name__ == "__main__":
    main()


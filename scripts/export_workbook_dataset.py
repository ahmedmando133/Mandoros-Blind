from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.metformin_data import load_metformin_bundle


def main() -> None:
    target = ROOT / "standards" / "metformin_workbook_dataset.json"
    target.write_text(json.dumps(load_metformin_bundle(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()

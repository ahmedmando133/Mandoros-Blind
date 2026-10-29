from __future__ import annotations

import json
import mimetypes
import shutil
import time
from email.parser import BytesParser
from email.policy import default
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .config import OUTPUT_DIR, PRIVATE_DIR, STATIC_DIR
from .repair import create_corrected_workbook
from .report import render_html
from .validator import validate_workbook, write_report


def _parse_multipart(headers, body: bytes) -> dict[str, tuple[str, bytes]]:
    content_type = headers.get("Content-Type", "")
    message = BytesParser(policy=default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
    )
    files: dict[str, tuple[str, bytes]] = {}
    for part in message.iter_parts():
        name = part.get_param("name", header="content-disposition")
        filename = part.get_filename()
        if name and filename:
            files[name] = (Path(filename).name, part.get_payload(decode=True) or b"")
    return files


class Handler(BaseHTTPRequestHandler):
    server_version = "MandrosBlind/0.1"

    def _json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        if path.suffix in {".xlsx", ".json"}:
            self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        route = unquote(urlparse(self.path).path)
        if route == "/api/demo":
            report_path = OUTPUT_DIR / "metformin_assessment.json"
            html_path = OUTPUT_DIR / "metformin_assessment.html"
            if not report_path.exists():
                report = validate_workbook(PRIVATE_DIR / "metformin" / "source.pdf", PRIVATE_DIR / "metformin" / "mandros_input.xlsx")
                write_report(report, report_path)
                render_html(report, html_path)
            elif not html_path.exists():
                render_html(json.loads(report_path.read_text(encoding="utf-8")), html_path)
            self._json(json.loads(report_path.read_text(encoding="utf-8")))
            return
        if route.startswith("/downloads/"):
            requested = (OUTPUT_DIR / route.removeprefix("/downloads/")).resolve()
            if OUTPUT_DIR.resolve() not in requested.parents:
                self.send_error(403)
                return
            self._file(requested)
            return
        target = STATIC_DIR / ("index.html" if route in {"", "/"} else route.lstrip("/"))
        self._file(target)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/audit":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 80 * 1024 * 1024:
                raise ValueError("Upload must be between 1 byte and 80 MB.")
            files = _parse_multipart(self.headers, self.rfile.read(length))
            if "pdf" not in files or "xlsx" not in files:
                raise ValueError("Both PDF and XLSX files are required.")
            run_id = time.strftime("%Y%m%d-%H%M%S")
            run_dir = OUTPUT_DIR / "runs" / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            study_dir = PRIVATE_DIR / "studies" / run_id
            study_dir.mkdir(parents=True, exist_ok=True)
            pdf_path = study_dir / "source.pdf"
            xlsx_path = study_dir / "mandros_input.xlsx"
            pdf_path.write_bytes(files["pdf"][1])
            xlsx_path.write_bytes(files["xlsx"][1])
            report = validate_workbook(pdf_path, xlsx_path)
            (study_dir / "study_manifest.json").write_text(json.dumps({
                "run_id": run_id,
                "original_pdf_name": files["pdf"][0],
                "original_xlsx_name": files["xlsx"][0],
                "source_sha256": report["source_sha256"],
                "input_workbook_sha256": report["input_workbook_sha256"],
                "decision": report["decision"],
                "score": report["score"]
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            report_path = run_dir / "assessment.json"
            html_path = run_dir / "assessment.html"
            write_report(report, report_path)
            render_html(report, html_path)
            response = {"run_id": run_id, "report": report, "report_url": f"/downloads/runs/{run_id}/assessment.html"}
            recognized_fixture = report.get("recognized_fixture")
            if recognized_fixture in {"metformin-dppos-dc11-1299", "orlistat-rct-2024-v1"}:
                corrected = run_dir / "corrected.xlsx"
                source_corrected = (
                    OUTPUT_DIR / "metformin_Mandros_Blind_corrected.xlsx"
                    if recognized_fixture == "metformin-dppos-dc11-1299"
                    else OUTPUT_DIR / "orlistat-rct-2024" / "orlistat_Mandros_Blind_corrected.xlsx"
                )
                if source_corrected.exists():
                    shutil.copy2(source_corrected, corrected)
                elif recognized_fixture == "metformin-dppos-dc11-1299":
                    create_corrected_workbook(corrected)
                else:
                    raise FileNotFoundError("The Orlistat truth bundle matched, but its corrected workbook has not been built yet.")
                response["corrected_url"] = f"/downloads/runs/{run_id}/corrected.xlsx"
            else:
                response["correction_status"] = "No source truth bundle matched; automatic scientific rewriting was withheld."
            self._json(response)
        except Exception as exc:
            self._json({"error": str(exc)}, 400)


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Mandros Blind running at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


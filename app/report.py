from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def render_html(report: dict[str, Any], output: Path) -> None:
    scores = "".join(f"<tr><td>{html.escape(k.replace('_',' ').title())}</td><td>{v}</td></tr>" for k, v in report["domain_scores"].items())
    issues = "".join(
        "<tr>" + "".join([
            f"<td><span class='sev {html.escape(i['severity'])}'>{html.escape(i['severity'])}</span></td>",
            f"<td>{html.escape(i['code'])}</td>",
            f"<td>{html.escape(i['domain'])}</td>",
            f"<td>{html.escape(i['message'])}</td>",
            f"<td>{html.escape(i['action'])}</td>",
        ]) + "</tr>" for i in report["issues"]
    )
    fixture = report.get("recognized_fixture") or "دراسة جديدة غير موجودة في حزم التحقق المحلية"
    if report["issues"]:
        scientific_summary = "تم تطبيق قواعد التحقق البنيوية والعلمية المتاحة محليًا. راجع سجل الأخطاء أدناه؛ لا يُنشئ النظام قيمًا علمية بديلة من دون مصدر موثّق وحزمة حقيقة مطابقة."
    else:
        scientific_summary = "لم يكتشف الفحص الآلي أخطاءً ضمن القواعد المنفذة، لكن ذلك لا يحول الفحص البنيوي وحده إلى تحقق علمي كامل."
    doc = f"""<!doctype html><html lang='ar' dir='rtl'><meta charset='utf-8'><title>Mandros Blind audit</title>
<style>body{{font-family:Arial,sans-serif;background:#f5f7f8;color:#17324d;margin:0}}main{{max-width:1200px;margin:40px auto;padding:0 24px}}.hero{{background:#17324d;color:white;border-radius:18px;padding:28px}}.score{{font-size:54px;font-weight:800}}.reject{{color:#ffb4a8}}.grid{{display:grid;grid-template-columns:1fr 2fr;gap:18px;margin-top:18px}}.card{{background:white;border-radius:14px;padding:20px;box-shadow:0 8px 28px #17324d12}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border-bottom:1px solid #dce6e8;padding:10px;text-align:right;vertical-align:top}}th{{background:#e8f3f1}}.sev{{font-weight:700}}.critical{{color:#b42318}}.major{{color:#b54708}}code{{direction:ltr;display:inline-block}}</style>
<main><section class='hero'><div>MANDROS BLIND · VERIFIED AUDIT</div><h1>تقييم ملف Mandros مقابل الـPDF الأصلي</h1><div class='score'>{report['score']}/100</div><h2 class='reject'>{report['decision']}</h2><p>{report['blocking_issue_count']} أخطاء مانعة، {report['issue_count']} ملاحظة موثقة. النجاح البنيوي لا يساوي صحة علمية.</p></section>
<div class='grid'><section class='card'><h2>الدرجات</h2><table>{scores}</table></section><section class='card'><h2>النتيجة العلمية</h2><p>{html.escape(scientific_summary)}</p><p>حزمة المصدر المطابقة: <code>{html.escape(str(fixture))}</code></p></section></div>
<section class='card' style='margin-top:18px'><h2>سجل الأخطاء</h2><table><thead><tr><th>الشدة</th><th>الكود</th><th>المجال</th><th>المشكلة</th><th>الإجراء</th></tr></thead><tbody>{issues}</tbody></table></section>
<section class='card' style='margin-top:18px'><h2>حدود التقرير</h2><ul>{''.join(f'<li>{html.escape(x)}</li>' for x in report['limitations'])}</ul><p>Source SHA-256: <code>{report['source_sha256']}</code></p></section></main></html>"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(doc, encoding="utf-8")


def load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


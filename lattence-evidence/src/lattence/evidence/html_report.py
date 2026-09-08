import html
from pathlib import Path

from .reporting import Report, report_json

_STYLE = """
:root{color-scheme:dark;--s0:#0B0D10;--s1:#12151A;--s2:#1A1F26;
--border:#262C35;--text:#E6E9EE;--muted:#8A94A6;--accent:#4C8DFF;
--critical:#E5484D;--high:#F76808;--medium:#E2A336;--low:#3E9B4F;--info:#6E7A8A}
*{box-sizing:border-box}body{margin:0;background:var(--s0);color:var(--text);
font:13px Inter,system-ui,sans-serif}main{max-width:1200px;margin:0 auto;padding:24px}
h1,h2{margin:0 0 12px}h1{font:20px ui-monospace,monospace;letter-spacing:.08em}
h2{font-size:14px}.muted{color:var(--muted)}.grid{display:grid;
grid-template-columns:repeat(4,1fr);gap:8px;margin:16px 0}.metric,.panel{
border:1px solid var(--border);border-radius:2px;background:var(--s1)}
.metric{padding:12px}.metric b{display:block;font:20px ui-monospace,monospace}
.panel{margin-top:12px;padding:12px;overflow:auto}table{border-collapse:collapse;
width:100%;font:12px ui-monospace,monospace}th{position:sticky;top:0;
background:var(--s2);
color:var(--muted);text-align:left}th,td{height:32px;padding:4px 8px;
border-bottom:1px solid var(--border)}.severity{font-weight:700}
.critical{color:var(--critical)}
.high{color:var(--high)}.medium{color:var(--medium)}.low{color:var(--low)}
.info{color:var(--info)}code{font-family:ui-monospace,monospace;color:var(--accent)}
@media(max-width:720px){main{padding:12px}.grid{grid-template-columns:repeat(2,1fr)}}
"""


def _text(value: object) -> str:
    return html.escape(str(value), quote=True)


def _finding_rows(report: Report) -> str:
    rows = []
    for finding in report.findings:
        mappings = ", ".join((*finding.owasp_llm, *finding.owasp_agentic, *finding.cwe))
        severity = _text(finding.severity)
        severity_name = _text(finding.severity.upper())
        rows.append(
            "<tr>"
            f"<td><code>{_text(finding.id)}</code></td>"
            f"<td>{_text(finding.title)}</td>"
            f'<td class="severity {severity}">{severity_name}</td>'
            f"<td><code>{_text(finding.target_node_id)}</code></td>"
            f"<td>{_text(mappings)}</td>"
            f"<td>{_text(finding.remediation)}</td>"
            "</tr>"
        )
    return "".join(rows) or '<tr><td colspan="6" class="muted">No findings.</td></tr>'


def _node_rows(report: Report) -> str:
    return "".join(
        "<tr>"
        f"<td><code>{_text(node.id)}</code></td>"
        f"<td>{_text(node.type)}</td>"
        f"<td>{_text(node.name)}</td>"
        f"<td>{_text(node.source.path if node.source else '')}</td>"
        "</tr>"
        for node in report.graph.nodes
    )


def render_html_report(report: Report) -> str:
    summary = report.summary
    embedded = html.escape(report_json(report), quote=False)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_text(report.project.name)} security report</title>
<style>{_STYLE}</style></head><body><main><header><h1>LATTENCE REPORT</h1>
<div class="muted">{_text(report.project.name)} ·
{_text(report.generated_at.isoformat())}</div></header>
<section class="grid"><div class="metric"><b>{summary.total}</b>Findings</div>
<div class="metric"><b>{summary.critical + summary.high}</b>Critical + high</div>
<div class="metric"><b>{len(report.graph.nodes)}</b>Graph nodes</div>
<div class="metric"><b>{summary.pqc_readiness:g}%</b>PQC readiness</div></section>
<section class="panel"><h2>Findings</h2><table><thead><tr>
<th>ID</th><th>Finding</th><th>Severity</th><th>Target</th>
<th>Mappings</th><th>Remediation</th></tr></thead>
<tbody>{_finding_rows(report)}</tbody></table></section>
<section class="panel"><h2>Security graph inventory</h2><table><thead><tr>
<th>ID</th><th>Type</th><th>Name</th><th>Source</th></tr></thead>
<tbody>{_node_rows(report)}</tbody></table></section>
<details class="panel"><summary>Report JSON</summary><pre>{embedded}</pre></details>
</main></body></html>\n"""


def write_html_report(report: Report, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_html_report(report), encoding="utf-8")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审核员资格与能力矩阵报告生成器
读入结构化结果 JSON，生成 MD 文档 + 网页版 HTML（双版）。主色 #C8102E。

用法：
  python build_report.py --input result.json --md-out report.md --html-out report.html
  python build_report.py --demo            # 使用内置小样本

输入 JSON 结构：
{
  "title": "2026 年度审核员资格矩阵",
  "org": "组织名",
  "maintenance_rules": {"validity_years":3, "min_audit_days_per_year":"待企业补充", "retrain":"到期前再培训与复审"},
  "auditors": [
    {
      "name":"张三","id":"A001","type":"过程审核","level":"正式","scope":"机加工/装配",
      "certificates":[{"name":"VDA 6.3 过程审核员(B)","no":"待企业补充","issuer":"待企业补充","valid_until":"2026-08-31"}],
      "training":["VDA 6.3 2023 培训"],
      "experience":{"audits":5,"man_days":12,"last_audit":"2026-03-01"},
      "status":"有效"
    }
  ],
  "maintenance_plan":[
    {"auditor":"张三","action":"资格复审/再注册","due":"2026-06-30","owner":"体系部"}
  ]
}
"""
import argparse
import json
import sys
import html
from datetime import datetime

PRIMARY = "#C8102E"

STATUS_COLOR = {
    "有效": "#16a34a",
    "即将到期": "#ea580c",
    "待复审": "#2563eb",
    "失效": "#C8102E",
}


def esc(s):
    return html.escape(str(s), quote=True)


def load_result(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_md(r):
    L = []
    L.append(f"# {r.get('title','审核员资格矩阵')}\n")
    L.append("## 一、概览\n")
    L.append(f"- 组织：{r.get('org','') or '待企业补充'}")
    mr = r.get("maintenance_rules", {}) or {}
    L.append(f"- 资格有效期：{mr.get('validity_years','待企业补充')} 年")
    L.append(f"- 年度最低审核人日：{mr.get('min_audit_days_per_year','待企业补充')}")
    L.append(f"- 维护要求：{mr.get('retrain','待企业补充')}")
    L.append("")
    L.append("## 二、审核员资格矩阵\n")
    L.append("| 姓名 | 工号 | 审核类型 | 等级 | 适用范围 | 主要证书 | 有效期 | 审核经历(次/人日) | 状态 |")
    L.append("|------|------|----------|------|----------|----------|--------|------------------|------|")
    for a in r.get("auditors", []) or []:
        certs = "；".join(c.get("name", "") + "(" + c.get("valid_until", "待企业补充") + ")" for c in a.get("certificates", []) or [])
        exp = a.get("experience", {}) or {}
        exp_s = f"{exp.get('audits','待企业补充')}/{exp.get('man_days','待企业补充')}"
        L.append(f"| {a.get('name','')} | {a.get('id','')} | {a.get('type','')} | {a.get('level','')} | "
                 f"{a.get('scope','待企业补充')} | {certs or '待企业补充'} | "
                 f"{a.get('certificates',[{}])[0].get('valid_until','待企业补充') if a.get('certificates') else '待企业补充'} | "
                 f"{exp_s} | {a.get('status','待企业补充')} |")
    L.append("")
    L.append("## 三、年度维护计划\n")
    L.append("| 审核员 | 维护活动 | 计划时间 | 责任方 |")
    L.append("|--------|----------|----------|--------|")
    for m in r.get("maintenance_plan", []) or []:
        L.append(f"| {m.get('auditor','')} | {m.get('action','')} | {m.get('due','待企业补充')} | {m.get('owner','待企业补充')} |")
    L.append("")
    L.append(f"> 报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ 主色 {PRIMARY}")
    return "\n".join(L)


CSS = """
:root{--primary:#C8102E;--bg:#f8fafc;--card:#ffffff;--ink:#1e293b;--muted:#64748b;--line:#e2e8f0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink);line-height:1.7;padding:32px}
.wrap{max-width:1160px;margin:0 auto}
header{text-align:center;padding:28px 0 18px;border-bottom:3px solid var(--primary);margin-bottom:28px}
header h1{font-size:26px;letter-spacing:1px;color:var(--primary)}
header .meta{color:var(--muted);font-size:14px;margin-top:10px}
.sec{background:var(--card);border-radius:14px;padding:24px;box-shadow:0 4px 16px rgba(0,0,0,.06);margin-bottom:28px}
.sec h2{font-size:21px;margin-bottom:16px;border-left:5px solid var(--primary);padding-left:12px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:#fef2f2;color:var(--primary)}
.badge{display:inline-block;color:#fff;border-radius:6px;padding:1px 8px;font-size:12px;font-weight:700}
footer{text-align:center;color:var(--muted);font-size:12px;margin-top:20px}
"""


def build_html(r):
    rows = []
    for a in r.get("auditors", []) or []:
        certs = a.get("certificates", []) or []
        cert_s = "；".join(f"{esc(c.get('name',''))}({esc(c.get('valid_until','待企业补充'))})" for c in certs) or "待企业补充"
        valid = certs[0].get("valid_until", "待企业补充") if certs else "待企业补充"
        exp = a.get("experience", {}) or {}
        exp_s = f"{esc(exp.get('audits','待企业补充'))} 次 / {esc(exp.get('man_days','待企业补充'))} 人日"
        st = a.get("status", "待企业补充")
        color = STATUS_COLOR.get(st, "#64748b")
        badge = f'<span class="badge" style="background:{color}">{esc(st)}</span>'
        rows.append(
            f"<tr><td>{esc(a.get('name',''))}</td><td>{esc(a.get('id',''))}</td>"
            f"<td>{esc(a.get('type',''))}</td><td>{esc(a.get('level',''))}</td>"
            f"<td>{esc(a.get('scope','待企业补充'))}</td><td>{cert_s}</td><td>{esc(valid)}</td>"
            f"<td>{exp_s}</td><td>{badge}</td></tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="9" style="color:#64748b">（暂无审核员数据，待企业补充）</td></tr>')
    matrix_html = ("<table><tr><th>姓名</th><th>工号</th><th>审核类型</th><th>等级</th><th>适用范围</th>"
                   "<th>主要证书(有效期)</th><th>证书到期</th><th>审核经历</th><th>状态</th></tr>"
                   + "".join(rows) + "</table>")

    mrows = []
    for m in r.get("maintenance_plan", []) or []:
        mrows.append(f"<tr><td>{esc(m.get('auditor',''))}</td><td>{esc(m.get('action',''))}</td>"
                     f"<td>{esc(m.get('due','待企业补充'))}</td><td>{esc(m.get('owner','待企业补充'))}</td></tr>")
    if not mrows:
        mrows.append('<tr><td colspan="4" style="color:#64748b">（暂无维护计划，待企业补充）</td></tr>')
    plan_html = ("<table><tr><th>审核员</th><th>维护活动</th><th>计划时间</th><th>责任方</th></tr>"
                 + "".join(mrows) + "</table>")

    mr = r.get("maintenance_rules", {}) or {}
    meta = (f"组织：{esc(r.get('org','') or '待企业补充')} ｜ 资格有效期：{esc(mr.get('validity_years','待企业补充'))} 年 ｜ "
            f"年度最低人日：{esc(mr.get('min_audit_days_per_year','待企业补充'))} ｜ 维护要求：{esc(mr.get('retrain','待企业补充'))}")

    return (
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        f"<title>{esc(r.get('title','审核员资格矩阵'))}</title>"
        f"<style>{CSS}</style></head><body><div class='wrap'>"
        f"<header><h1>{esc(r.get('title','审核员资格矩阵'))}</h1><div class='meta'>{meta}</div></header>"
        "<section class='sec'><h2>审核员资格矩阵</h2>" + matrix_html + "</section>"
        "<section class='sec'><h2>年度维护计划</h2>" + plan_html + "</section>"
        f"<footer>本报告由 审核员资格与能力矩阵管理 生成 · {datetime.now().strftime('%Y-%m-%d %H:%M')} · 主色 {PRIMARY}</footer>"
        "</div></body></html>"
    )


SAMPLE = {
    "title": "2026 年度审核员资格矩阵（演示样本）",
    "org": "待企业补充",
    "maintenance_rules": {
        "validity_years": 3,
        "min_audit_days_per_year": "待企业补充（如 ≥ 8 人日）",
        "retrain": "到期前完成再培训与复审/再注册"
    },
    "auditors": [
        {
            "name": "张三", "id": "A001", "type": "过程审核", "level": "正式", "scope": "机加工 / 装配",
            "certificates": [{"name": "VDA 6.3 过程审核员(B)", "no": "待企业补充", "issuer": "待企业补充", "valid_until": "2026-08-31"}],
            "training": ["VDA 6.3 2023 培训"],
            "experience": {"audits": 5, "man_days": 12, "last_audit": "2026-03-01"},
            "status": "即将到期"
        },
        {
            "name": "李四", "id": "A002", "type": "体系审核", "level": "主任", "scope": "QMS 全范围",
            "certificates": [{"name": "IATF 16949 内审员", "no": "待企业补充", "issuer": "待企业补充", "valid_until": "2027-12-31"}],
            "training": ["IATF 16949 标准培训"],
            "experience": {"audits": 12, "man_days": 30, "last_audit": "2026-05-15"},
            "status": "有效"
        },
        {
            "name": "王五", "id": "A003", "type": "产品审核", "level": "实习", "scope": "电子件",
            "certificates": [{"name": "VDA 6.5 产品审核员", "no": "待企业补充", "issuer": "待企业补充", "valid_until": "2025-11-30"}],
            "training": ["VDA 6.5 培训"],
            "experience": {"audits": 1, "man_days": 2, "last_audit": "2025-09-10"},
            "status": "失效"
        }
    ],
    "maintenance_plan": [
        {"auditor": "张三", "action": "VDA 6.3 资格复审/再注册", "due": "2026-06-30", "owner": "体系部"},
        {"auditor": "王五", "action": "重新培训并取得有效产品审核资格", "due": "2026-03-31", "owner": "体系部"},
        {"auditor": "李四", "action": "维持年度最低审核人日", "due": "2026-12-31", "owner": "体系部"}
    ]
}


def main():
    ap = argparse.ArgumentParser(description="审核员资格矩阵报告生成器")
    ap.add_argument("--input", help="结构化结果 JSON 路径")
    ap.add_argument("--md-out", default="demo_auditor.md", help="输出 MD 路径")
    ap.add_argument("--html-out", default="demo_auditor.html", help="输出 HTML 路径")
    ap.add_argument("--demo", action="store_true", help="使用内置小样本生成演示报告")
    args = ap.parse_args()

    if args.demo:
        r = SAMPLE
    elif args.input:
        try:
            r = load_result(args.input)
        except Exception as e:
            sys.stderr.write(f"读取输入失败：{e}\n")
            sys.exit(1)
    else:
        sys.stderr.write("请使用 --input <json> 或 --demo。\n")
        sys.exit(1)

    with open(args.md_out, "w", encoding="utf-8") as f:
        f.write(build_md(r))
    sys.stderr.write(f"MD 已生成：{args.md_out}\n")
    with open(args.html_out, "w", encoding="utf-8") as f:
        f.write(build_html(r))
    sys.stderr.write(f"HTML 已生成：{args.html_out}\n")


if __name__ == "__main__":
    main()

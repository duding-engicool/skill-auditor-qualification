#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
审核员资格与能力矩阵报告生成器
读入结构化结果 JSON，生成纯文字版 .txt + Markdown .md（双文件、无网页版）。

用法：
  python build_report.py --input result.json --out-dir ./out
  python build_report.py --out-dir ./out          # 使用内置小样本

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
import os
import sys
from datetime import date


def load_result(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def certs_summary(a):
    certs = a.get("certificates", []) or []
    if not certs:
        return "待企业补充", "待企业补充"
    names = "；".join(f"{c.get('name','')}({c.get('valid_until','待企业补充')})" for c in certs)
    valid = certs[0].get("valid_until", "待企业补充")
    return names, valid


def exp_summary(a):
    exp = a.get("experience", {}) or {}
    return f"{exp.get('audits','待企业补充')} 次 / {exp.get('man_days','待企业补充')} 人日"


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
    L.append("| 姓名 | 工号 | 审核类型 | 等级 | 适用范围 | 主要证书(有效期) | 证书到期 | 审核经历(次/人日) | 状态 |")
    L.append("|------|------|----------|------|----------|------------------|--------|------------------|------|")
    for a in r.get("auditors", []) or []:
        certs, valid = certs_summary(a)
        L.append(f"| {a.get('name','')} | {a.get('id','')} | {a.get('type','')} | {a.get('level','')} | "
                 f"{a.get('scope','待企业补充')} | {certs} | {valid} | "
                 f"{exp_summary(a)} | {a.get('status','待企业补充')} |")
    L.append("")
    L.append("## 三、年度维护计划\n")
    L.append("| 审核员 | 维护活动 | 计划时间 | 责任方 |")
    L.append("|--------|----------|----------|--------|")
    for m in r.get("maintenance_plan", []) or []:
        L.append(f"| {m.get('auditor','')} | {m.get('action','')} | {m.get('due','待企业补充')} | {m.get('owner','待企业补充')} |")
    L.append("")
    L.append(f"> 报告生成时间：{date.today().strftime('%Y-%m-%d')} ｜ 输出：纯文字版(.txt) + Markdown(.md)")
    return "\n".join(L)


def build_txt(r):
    L = []
    L.append("=" * 72)
    L.append(f"审核员资格与能力矩阵 · {r.get('title','审核员资格矩阵')}")
    L.append("=" * 72)
    L.append("")
    L.append(f"组织          ：{r.get('org','') or '待企业补充'}")
    mr = r.get("maintenance_rules", {}) or {}
    L.append(f"资格有效期    ：{mr.get('validity_years','待企业补充')} 年")
    L.append(f"年度最低人日  ：{mr.get('min_audit_days_per_year','待企业补充')}")
    L.append(f"维护要求      ：{mr.get('retrain','待企业补充')}")
    L.append("")

    # 二、审核员资格矩阵
    L.append("-" * 72)
    L.append("二、审核员资格矩阵")
    L.append("-" * 72)
    for a in r.get("auditors", []) or []:
        certs, valid = certs_summary(a)
        L.append(f"  ◆ {a.get('name','')}（{a.get('id','')}）")
        L.append(f"     审核类型：{a.get('type','')} ｜ 等级：{a.get('level','')} ｜ 适用范围：{a.get('scope','待企业补充')}")
        L.append(f"     主要证书：{certs}")
        L.append(f"     证书到期：{valid} ｜ 审核经历：{exp_summary(a)} ｜ 状态：{a.get('status','待企业补充')}")
        L.append("")

    # 三、年度维护计划
    L.append("-" * 72)
    L.append("三、年度维护计划")
    L.append("-" * 72)
    plans = r.get("maintenance_plan", []) or []
    if plans:
        for m in plans:
            L.append(f"  ◆ {m.get('auditor','')}：{m.get('action','')} ｜ 计划时间：{m.get('due','待企业补充')} ｜ 责任方：{m.get('owner','待企业补充')}")
    else:
        L.append("  （暂无维护计划，待企业补充）")
    L.append("")

    L.append("-" * 72)
    L.append(f"报告生成时间：{date.today().strftime('%Y-%m-%d')} ｜ 输出：纯文字版(.txt) + Markdown(.md)")
    L.append("")
    return "\n".join(L)


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
    ap = argparse.ArgumentParser(description="审核员资格矩阵报告生成器（txt + md）")
    ap.add_argument("--input", help="结构化结果 JSON 路径（缺省使用内置小样本）")
    ap.add_argument("--out-dir", default=os.getcwd(), help="输出目录（默认当前工作目录）")
    ap.add_argument("--format", choices=["txt", "md", "all"], default="all",
                    help="输出格式：txt / md / all（默认 all = txt + md）")
    args = ap.parse_args()

    if args.input:
        try:
            r = load_result(args.input)
        except Exception as e:
            sys.stderr.write(f"读取输入失败：{e}\n")
            sys.exit(1)
    else:
        r = SAMPLE
        print("ℹ️ 未提供 --input，使用内置小样本数据。")

    title = str(r.get("title", "审核员资格矩阵")).replace("/", "-")
    date_str = date.today().strftime("%Y%m%d")
    base = f"审核员资格矩阵_{title}_{date_str}"
    os.makedirs(args.out_dir, exist_ok=True)

    if args.format in ("md", "all"):
        md = build_md(r)
        md_path = os.path.join(args.out_dir, base + ".md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✅ MD : {md_path}")

    if args.format in ("txt", "all"):
        txt = build_txt(r)
        txt_path = os.path.join(args.out_dir, base + ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"✅ TXT: {txt_path}")

    print(f"   审核员数：{len(r.get('auditors', []) or [])}  ｜ 维护计划项：{len(r.get('maintenance_plan', []) or [])}")


if __name__ == "__main__":
    main()

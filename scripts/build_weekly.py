#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掃描 goodbook/*.html → 自動產生 weekly.json
規則：
  1. 檔名開頭 4 碼數字 = 月日（例：0524_xxx.html → 05/24）
  2. 年份 = 該檔案第一次 commit 進 repo 的年份（git log 推算）
  3. 標題 = 檔案內的 <title>，自動清掉「— 好書分享 0510」這類尾巴
  4. overrides.json 可以：跳過某檔(skip)、覆寫標題(title)、補 YT 連結(yt)
  5. 依日期新到舊排序，官網第一張卡自動掛 NEW 徽章
"""
import json, re, subprocess, urllib.parse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GOODBOOK  = REPO_ROOT / "goodbook"
SITE_BASE = "https://brothergo99.github.io/rock-accounting-students/goodbook/"

# 讀取例外設定（沒有這個檔也能正常跑）
overrides = {}
ov_path = REPO_ROOT / "overrides.json"
if ov_path.exists():
    overrides = json.loads(ov_path.read_text(encoding="utf-8"))

def first_commit_year(path: Path) -> str:
    """取檔案第一次進 repo 的年份；抓不到就用今年"""
    try:
        out = subprocess.run(
            ["git", "log", "--follow", "--format=%ad", "--date=format:%Y",
             "--", str(path.relative_to(REPO_ROOT))],
            capture_output=True, text=True, cwd=REPO_ROOT, check=True
        ).stdout.strip().splitlines()
        if out:
            return out[-1]  # 最後一行 = 最早的 commit
    except Exception:
        pass
    from datetime import date
    return str(date.today().year)

def extract_title(path: Path) -> str:
    head = path.read_text(encoding="utf-8", errors="ignore")[:3000]
    m = re.search(r"<title>(.*?)</title>", head, re.S)
    if not m:
        return path.stem  # 沒有 title 就退回檔名
    t = m.group(1).strip()
    # 清掉常見雜訊尾巴：「— 好書分享 0510」「| 好書分享」「- 一頁式」等
    t = re.sub(r"\s*[—\-–|·]\s*(好書分享|每週分享|一頁式|複習筆記)(\s*\d{4})?\s*$", "", t)
    return t.strip()

items = []
for f in sorted(GOODBOOK.glob("*.html")):
    ov = overrides.get(f.name, {})
    if ov.get("skip"):
        continue

    m = re.match(r"(\d{4})", f.name)   # 檔名開頭 4 碼，有沒有底線都能吃
    if not m:
        continue                        # 開頭不是日期的檔案直接略過
    mmdd = m.group(1)
    mo, dd = mmdd[:2], mmdd[2:]
    year = ov.get("year") or first_commit_year(f)

    items.append({
        "date":  f"{year}/{mo}/{dd}",
        "title": ov.get("title") or extract_title(f),
        "note":  SITE_BASE + urllib.parse.quote(f.name),
        "yt":    ov.get("yt", ""),
        "_sort": f"{year}{mmdd}",
    })

items.sort(key=lambda x: x["_sort"], reverse=True)
for it in items:
    it.pop("_sort")

out = {"items": items}
(REPO_ROOT / "weekly.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"完成：{len(items)} 筆 → weekly.json")

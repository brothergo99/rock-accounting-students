"""
自動掃描所有學生資料夾，生成 students/index.html
上傳位置：rock-accounting-students repo 根目錄
"""
import os
import re
from urllib.parse import quote

BASE_URL = "https://brothergo99.github.io/rock-accounting-students"
PASSWORD = "Rock"

# 已知學生的中文顯示名稱與頭像（新學生不需要修改這裡，會自動偵測）
STUDENT_INFO = {
    "bozhen":    {"name": "Bozhen · 柏蓁",     "avatar": "B"},
    "cavin":     {"name": "Cavin",              "avatar": "C"},
    "goodbook":  {"name": "Goodbook · 好書分享", "avatar": "G"},
    "huimei":    {"name": "Huimei · 蕙美",      "avatar": "惠"},
    "jiaru":     {"name": "Jiaru · 佳汝",       "avatar": "汝"},
    "jiayi":     {"name": "Jiayi · 佳誼",       "avatar": "誼"},
    "liya":      {"name": "Liya · 立雅",        "avatar": "雅"},
    "mandy":     {"name": "Mandy",              "avatar": "M"},
    "megan":     {"name": "Megan",              "avatar": "Me"},
    "xiaotu":    {"name": "Xiaotu · 小兔",      "avatar": "兔"},
    "xiaoyu":    {"name": "Xiaoyu · 小魚",      "avatar": "魚"},
    "yingxiang": {"name": "Yingxiang · 穎祥",   "avatar": "祥"},
    "april":     {"name": "April",              "avatar": "A"},
}

# 排除的非學生資料夾
EXCLUDE_FOLDERS = {".git", ".github", "output", "__pycache__", "node_modules"}


def get_all_student_folders():
    """自動偵測所有學生資料夾（排除系統資料夾）"""
    folders = []
    for item in sorted(os.listdir(".")):
        if os.path.isdir(item) and item not in EXCLUDE_FOLDERS and not item.startswith("."):
            folders.append(item)
    return folders


def get_student_info(folder_name):
    """取得學生顯示名稱與頭像，不在設定檔中的自動產生"""
    if folder_name in STUDENT_INFO:
        return STUDENT_INFO[folder_name]
    # 新學生：自動產生頭像（取第一個字母大寫）
    return {
        "name": folder_name.capitalize(),
        "avatar": folder_name[0].upper()
    }


def parse_filename(filename):
    """從檔名解析日期與顯示名稱"""
    name = filename.replace(".html", "")

    # 格式一：0425_柏蓁_一頁式 or 0421-1_Cavin_一頁式
    m = re.match(r"^(\d{4}(?:-\d+)?)([_-])(.+)$", name)
    if m:
        date = m.group(1)
        display = m.group(3).replace("_", " · ")
        return date, display

    # 格式二：立雅-會計複習-2026-05-27
    m2 = re.match(r"^(.+)-(\d{4}-\d{2}-\d{2})$", name)
    if m2:
        display = m2.group(1).replace("-", " ")
        date = m2.group(2)[5:]
        return date, display

    return "", name


def get_student_files(folder):
    """取得資料夾內所有 .html 檔案（排除 index.html），按名稱排序"""
    if not os.path.isdir(folder):
        return []
    files = [f for f in os.listdir(folder)
             if f.endswith(".html") and f != "index.html"]
    files.sort()
    return files


def render_student_section(folder_name, info, files):
    date_file_links = ""
    for f in files:
        date, display = parse_filename(f)
        url = f"{BASE_URL}/{folder_name}/{quote(f)}"
        date_file_links += f"""
          <a class="file-link" href="{url}" target="_blank">
            <div class="file-date">{date}</div>
            <div class="file-name">{display}</div>
            <div class="file-arrow">→</div>
          </a>"""

    count = len(files)
    return f"""
    <div class="student-section">
      <div class="student-header" onclick="toggle(this)">
        <div class="student-avatar">{info['avatar']}</div>
        <div class="student-info">
          <div class="student-name">{info['name']}</div>
          <div class="student-count">{count} 堂筆記</div>
        </div>
        <div class="chevron">▾</div>
      </div>
      <div class="student-files">
        <div class="file-list">{date_file_links}
        </div>
      </div>
    </div>"""


def generate_html(sections_html):
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>學生專區 · Rock 會計家教</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Noto+Sans+TC:wght@300;400;500;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --orange:#F5812A;--orange3:#FFC285;
  --cream:#FFF8F0;--cream2:#FFF0E0;--cream3:#FFE4C4;
  --brown:#7A3B10;--brown2:#A05020;--muted:#A08060;
  --ink:#2C1A0A;--white:#FFFFFF;
}}
body{{font-family:'Noto Sans TC',sans-serif;background:var(--cream);color:var(--ink);min-height:100vh;display:flex;flex-direction:column}}
nav{{display:flex;justify-content:space-between;align-items:center;padding:16px 48px;background:var(--white);border-bottom:2px solid var(--orange3);box-shadow:0 2px 12px rgba(245,129,42,.08)}}
.nav-brand{{font-family:'Playfair Display',serif;font-size:20px;font-weight:900;color:var(--orange);text-decoration:none}}
.nav-brand span{{font-weight:400;font-style:italic;font-size:13px;color:var(--muted);margin-left:6px}}
.nav-back{{font-family:'DM Mono',monospace;font-size:11px;color:var(--brown2);text-decoration:none;border:1.5px solid var(--orange3);padding:7px 14px;border-radius:4px;transition:.2s}}
.nav-back:hover{{border-color:var(--orange);color:var(--orange)}}
#login-screen{{flex:1;display:flex;align-items:center;justify-content:center;padding:48px 24px}}
.login-box{{background:var(--white);border:2px solid var(--orange3);border-radius:16px;padding:48px 40px;width:min(420px,100%);box-shadow:0 8px 32px rgba(245,129,42,.1);text-align:center}}
.login-icon{{font-size:48px;margin-bottom:16px}}
.login-label{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.25em;color:var(--orange);text-transform:uppercase;margin-bottom:10px}}
.login-title{{font-family:'Playfair Display',serif;font-size:28px;font-weight:700;color:var(--ink);margin-bottom:10px}}
.login-desc{{font-size:14px;color:var(--brown2);line-height:1.7;margin-bottom:32px}}
.pw-input{{width:100%;padding:13px 16px;border:1.5px solid var(--orange3);border-radius:8px;font-size:16px;font-family:'Noto Sans TC',sans-serif;outline:none;transition:.2s;text-align:center;letter-spacing:.15em}}
.pw-input:focus{{border-color:var(--orange)}}
.pw-error{{color:#e53e3e;font-size:12px;margin-top:8px;min-height:18px}}
.pw-btn{{width:100%;margin-top:16px;padding:14px;background:var(--orange);color:#fff;border:none;border-radius:8px;font-size:15px;font-weight:700;cursor:pointer;font-family:'Noto Sans TC',sans-serif;transition:.2s}}
.pw-btn:hover{{background:#A05020}}
#content{{display:none;flex:1;padding:56px 48px}}
.content-inner{{max-width:960px;margin:0 auto}}
.sec-label{{font-family:'DM Mono',monospace;font-size:10px;letter-spacing:.25em;color:var(--orange);text-transform:uppercase;margin-bottom:12px}}
.sec-title{{font-family:'Playfair Display',serif;font-size:32px;font-weight:700;color:var(--ink);margin-bottom:8px}}
.sec-desc{{font-size:14px;color:var(--brown2);line-height:1.7;margin-bottom:36px}}
.student-section{{background:var(--white);border:2px solid var(--orange3);border-radius:14px;margin-bottom:16px;overflow:hidden;transition:.2s}}
.student-section:hover{{border-color:var(--orange);box-shadow:0 4px 20px rgba(245,129,42,.1)}}
.student-header{{display:flex;align-items:center;gap:16px;padding:20px 24px;cursor:pointer;user-select:none}}
.student-avatar{{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,var(--orange),var(--brown));display:flex;align-items:center;justify-content:center;font-family:'Playfair Display',serif;font-size:20px;font-weight:900;color:#fff;flex-shrink:0}}
.student-info{{flex:1}}
.student-name{{font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:var(--ink)}}
.student-count{{font-family:'DM Mono',monospace;font-size:10px;color:var(--muted);margin-top:2px}}
.chevron{{font-size:18px;color:var(--orange);transition:transform .2s;flex-shrink:0}}
.student-header.open .chevron{{transform:rotate(180deg)}}
.student-files{{display:none;padding:0 24px 20px;border-top:1px solid var(--orange3)}}
.student-files.open{{display:block}}
.file-list{{display:flex;flex-direction:column;gap:8px;margin-top:16px}}
.file-link{{display:flex;align-items:center;gap:12px;padding:12px 16px;background:var(--cream2);border:1.5px solid var(--orange3);border-radius:8px;text-decoration:none;transition:.2s}}
.file-link:hover{{border-color:var(--orange);background:var(--cream3);transform:translateX(4px)}}
.file-date{{font-family:'DM Mono',monospace;font-size:10px;color:var(--muted);flex-shrink:0;min-width:40px}}
.file-name{{font-size:13px;color:var(--ink);font-weight:500;flex:1}}
.file-arrow{{font-size:12px;color:var(--orange);flex-shrink:0}}
footer{{background:var(--brown);color:rgba(255,255,255,.8);padding:20px 48px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px}}
.ft-brand{{font-family:'Playfair Display',serif;font-size:15px;color:var(--orange3);font-weight:700}}
.ft-note{{font-family:'DM Mono',monospace;font-size:10px;color:rgba(255,255,255,.5)}}
@media(max-width:640px){{nav,#content{{padding-left:20px;padding-right:20px}}.login-box{{padding:32px 20px}}footer{{padding-left:20px;padding-right:20px}}}}
</style>
</head>
<body>
<nav>
  <a class="nav-brand" href="https://brothergo99.github.io/rock-accounting/">Rock <span>會計家教</span></a>
  <a class="nav-back" href="https://brothergo99.github.io/rock-accounting/">← 返回首頁</a>
</nav>
<div id="login-screen">
  <div class="login-box">
    <div class="login-icon">🎓</div>
    <div class="login-label">Student Zone</div>
    <div class="login-title">學生專區</div>
    <p class="login-desc">此區域為 Rock 老師課後複習筆記專區，<br>請輸入密碼以進入。</p>
    <input class="pw-input" type="password" id="pwd" placeholder="· · · · · ·"
      onkeydown="if(event.key==='Enter')checkPw()">
    <div class="pw-error" id="err"></div>
    <button class="pw-btn" onclick="checkPw()">進入學生專區 →</button>
  </div>
</div>
<div id="content">
  <div class="content-inner">
    <div class="sec-label">Student Zone · 課後複習</div>
    <div class="sec-title">選擇你的名字</div>
    <p class="sec-desc">點擊名字展開，查看所有課後複習筆記。</p>
    {sections_html}
  </div>
</div>
<footer>
  <div class="ft-brand">Rock 會計家教 · 蕭啟漢</div>
  <div class="ft-note">Student Zone · 學生專區</div>
</footer>
<script>
  const PASSWORD = "{PASSWORD}";
  function checkPw() {{
    if (document.getElementById('pwd').value === PASSWORD) {{
      document.getElementById('login-screen').style.display = 'none';
      document.getElementById('content').style.display = 'flex';
      document.getElementById('content').style.flexDirection = 'column';
    }} else {{
      document.getElementById('err').textContent = '❌ 密碼錯誤，請再試一次';
      document.getElementById('pwd').select();
    }}
  }}
  function toggle(header) {{
    const files = header.nextElementSibling;
    const isOpen = files.classList.contains('open');
    header.classList.toggle('open', !isOpen);
    files.classList.toggle('open', !isOpen);
  }}
</script>
</body>
</html>"""


def main():
    folders = get_all_student_folders()
    sections_html = ""
    for folder_name in folders:
        files = get_student_files(folder_name)
        if files:  # 有 HTML 檔案才顯示
            info = get_student_info(folder_name)
            sections_html += render_student_section(folder_name, info, files)

    html = generate_html(sections_html)
    os.makedirs("output", exist_ok=True)
    with open("output/students_index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 生成完成，共 {len(folders)} 個學生資料夾掃描")


if __name__ == "__main__":
    main()

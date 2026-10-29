"""의료기관 종별 매출액·영업이익률 보고서 .md → 단일 파일 HTML (그림은 base64로 포함)

usage: python build_hospital_finance_html.py [보고서.md]
"""
import base64
import html
import os
import re
import sys

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MD = os.path.join(HERE, "..", "03_HIRA_및_임상통계_보고서", "종합병원_매출액_및_영업이익률_10개년_분석_보고서.md")

CSS = """
:root {
  --primary: #1e3a8a; --primary-light: #3b82f6; --secondary: #0d9488;
  --danger: #dc2626; --warn-bg: #fffbeb; --warn-border: #f59e0b;
  --bg-body: #f8fafc; --bg-card: #ffffff; --text-main: #1f2937; --text-muted: #64748b;
  --border: #e2e8f0; --radius: 12px;
  --shadow: 0 4px 6px -1px rgba(0,0,0,.08), 0 2px 4px -2px rgba(0,0,0,.05);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Noto Sans KR', sans-serif; background: var(--bg-body); color: var(--text-main);
       line-height: 1.7; font-size: 15.5px; }
.header { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 55%, #0d9488 100%); color: #fff;
          padding: 48px 16px 40px; text-align: center; }
.header h1 { font-size: clamp(1.45rem, 3.6vw, 2.1rem); font-weight: 800; letter-spacing: -.5px; max-width: 1000px; margin: 0 auto; }
.header .sub { color: #cbd5e1; margin-top: 10px; font-weight: 300; }
.tags { display: flex; justify-content: center; gap: 8px; margin-top: 18px; flex-wrap: wrap; }
.tag { background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25); padding: 4px 12px;
       border-radius: 999px; font-size: .82rem; }
.layout { max-width: 1280px; margin: 0 auto; padding: 28px 16px; display: grid;
          grid-template-columns: 250px minmax(0, 1fr); gap: 28px; align-items: start; }
nav.toc { position: sticky; top: 16px; background: var(--bg-card); border: 1px solid var(--border);
          border-radius: var(--radius); padding: 16px 14px; box-shadow: var(--shadow); font-size: .86rem;
          max-height: calc(100vh - 32px); overflow-y: auto; }
nav.toc .toc-title { font-weight: 700; color: var(--primary); margin-bottom: 8px; }
nav.toc ul { list-style: none; }
nav.toc li { margin: 3px 0; }
nav.toc ul ul { padding-left: 12px; font-size: .82rem; }
nav.toc a { color: var(--text-muted); text-decoration: none; }
nav.toc a:hover { color: var(--primary-light); }
main, nav.toc { min-width: 0; }
code { overflow-wrap: anywhere; }
pre { white-space: pre-wrap; }
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius);
        box-shadow: var(--shadow); padding: 28px 30px; margin-bottom: 24px; }
.meta { background: #eff6ff; border-left: 4px solid var(--primary-light); }
.meta p { margin: 2px 0; font-size: .9rem; }
h2 { font-size: 1.4rem; color: var(--primary); font-weight: 800; padding-bottom: 10px;
     border-bottom: 2px solid var(--border); margin-bottom: 18px; }
h3 { font-size: 1.12rem; color: #0f172a; font-weight: 700; margin: 22px 0 10px; padding-left: 10px;
     border-left: 4px solid var(--secondary); }
p { margin: 10px 0; }
ul, ol { margin: 10px 0 10px 22px; }
li { margin: 6px 0; }
strong { color: #0f172a; }
code { font-family: Consolas, monospace; background: #f1f5f9; padding: 1px 5px; border-radius: 4px; font-size: .88em; }
pre { background: #0f172a; color: #e2e8f0; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 12px 0; }
pre code { background: none; color: inherit; padding: 0; }
.table-wrap { overflow-x: auto; margin: 14px 0; border: 1px solid var(--border); border-radius: 8px; }
table { border-collapse: collapse; width: 100%; font-size: .87rem; font-variant-numeric: tabular-nums; }
th { background: #f1f5f9; color: #0f172a; font-weight: 700; padding: 9px 10px; border-bottom: 2px solid var(--border);
     white-space: nowrap; }
td { padding: 8px 10px; border-bottom: 1px solid var(--border); }
tbody tr:hover { background: #f8fafc; }
td.neg { color: var(--danger); font-weight: 600; }
p em, li em { color: var(--text-muted); }
p > em:only-child { display: block; font-size: .85rem; }
figure { margin: 18px 0; text-align: center; }
figure img { max-width: 100%; height: auto; border: 1px solid var(--border); border-radius: 8px; background: #fcfcfb; }
figcaption { font-size: .82rem; color: var(--text-muted); margin-top: 6px; }
.warn { background: var(--warn-bg); border: 1px solid var(--warn-border); border-left-width: 4px;
        border-radius: 8px; padding: 10px 14px; list-style: none; margin-left: -22px; }
hr { display: none; }
footer { text-align: center; color: var(--text-muted); font-size: .8rem; padding: 10px 16px 40px; }
@media (max-width: 900px) {
  .layout { grid-template-columns: minmax(0, 1fr); }
  nav.toc { position: static; max-height: none; }
  .card { padding: 20px 16px; }
}
@media print {
  body { background: #fff; font-size: 11pt; }
  .header { background: #1e3a8a !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .layout { display: block; }
  nav.toc { display: none; }
  .card { box-shadow: none; break-inside: auto; }
  figure, table { break-inside: avoid; }
}
"""


def embed_images(body, base_dir):
    def repl(m):
        alt, src = m.group(1), m.group(2)
        path = os.path.join(base_dir, src)
        if not os.path.exists(path):
            return m.group(0)
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        return (f'<figure><img alt="{html.escape(alt)}" src="data:image/png;base64,{b64}">'
                f"<figcaption>{html.escape(alt)}</figcaption></figure>")
    # markdown 라이브러리는 단독 이미지 줄을 <p><img ...></p>로 감싼다
    return re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" ?/?></p>', repl, body)


def decorate(body):
    body = re.sub(r"<table>", '<div class="table-wrap"><table>', body)
    body = re.sub(r"</table>", "</table></div>", body)
    # 음수(유니코드 마이너스로 시작하는 값)는 빨간색으로
    body = re.sub(r'<td( style="[^"]*")?>(<strong>)?(−[\d.,]+%?p?)', r'<td class="neg"\1>\2\3', body)
    body = body.replace("<li>⚠️", '<li class="warn">⚠️')
    return body


def split_sections(body):
    """h2 단위로 카드를 나눈다. 첫 blockquote(자료원 등 메타)는 따로 꺼낸다."""
    meta = ""
    m = re.search(r"<blockquote>(.*?)</blockquote>", body, re.S)
    if m and body.index("<blockquote>") < body.find("<h2"):
        meta = m.group(1)
        body = body[:m.start()] + body[m.end():]
    parts = re.split(r"(?=<h2)", body)
    cards = "".join(f'<section class="card">{p}</section>' for p in parts if "<h2" in p)
    return meta, cards


def build(md_path):
    text = open(md_path, encoding="utf-8").read()
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    text = re.sub(r"^# .+\n", "", text, count=1, flags=re.M)
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"toc_depth": "2-3"}})
    body = md.convert(text)
    body = decorate(embed_images(body, os.path.dirname(md_path)))
    meta, cards = split_sections(body)
    # </div> → </nav> 치환을 먼저 해야 목차 제목의 </div>가 바뀌지 않는다
    toc = md.toc.replace("</div>", "</nav>").replace('<div class="toc">', '<nav class="toc"><div class="toc-title">목차</div>')
    meta = meta.strip().replace("\n", "<br>\n").replace("<p><br>", "<p>").replace("<br>\n</p>", "</p>")
    tags = "".join(f'<span class="tag">{t}</span>' for t in
                   ("통계청 서비스업조사", "HIRA 진료비 심사실적", "2014~2024", "KOSIS · korea-stats MCP"))
    page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;800&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<header class="header">
  <h1>{html.escape(title)}</h1>
  <p class="sub">상급종합병원·종합병원 · 병원 · 요양병원 · 의원 · 치과 · 한방병원 · 한의원</p>
  <div class="tags">{tags}</div>
</header>
<div class="layout">
{toc}
<main>
<section class="card meta">{meta}</section>
{cards}
</main>
</div>
<footer>자료: 통계청(국가데이터처) 「서비스업조사」, 건강보험심사평가원 「요양기관종별 진료비 심사실적」(KOSIS) · 원본 보고서: {html.escape(os.path.basename(md_path))}</footer>
</body>
</html>
"""
    out = os.path.splitext(md_path)[0] + ".html"
    open(out, "w", encoding="utf-8").write(page)
    return out


if __name__ == "__main__":
    print(build(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MD)))

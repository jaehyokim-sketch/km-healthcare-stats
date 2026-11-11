"""Build public portal HTML for V3.1 proposition validity & simulation report."""
import html
import pathlib
import re
import markdown

REPO = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO / "08_한의학교육_및_의료인력_정책" / "법제_판례_직능" / "이원적 의료체계는 없다 명제 타당성 분석 보고서_V3.md"
DST = REPO / "08_한의학교육_및_의료인력_정책" / "이원적_의료체계_명제_타당성_분석_보고서_V3.html"


def sanitize_for_public_web(text: str) -> str:
    """Remove workstation-local path hints while keeping all legal and quantitative facts intact."""
    text = text.replace("로컬 `01_교육과정_혁신로드맵/`, `04_법제_판례_직능/`", "내부 연구 분석 자료")
    text = re.sub(r"01_교육과정_혁신로드맵/|04_법제_판례_직능/", "", text)
    text = text.replace("로컬 PDF, kordoc MCP OCR", "판결문 PDF 원문(OCR 판독)")
    text = text.replace("로컬 PDF, kordoc MCP로 본문 추출", "원문 PDF 본문 추출")
    text = text.replace("로컬 DOCX, kordoc MCP로 본문 추출", "초안 보고서(DOCX) 본문 추출")
    text = text.replace("로컬 PDF, kordoc 본문 추출", "판결문 PDF 원문 추출")
    text = text.replace("로컬 PDF, 이미지 판결문을 OCR로 판독", "판결문 원문 OCR 판독")
    text = text.replace("로컬 MD·PDF·DOCX(내부 연구 분석 자료), PDF는 kordoc으로 본문 추출", "교육과정·재정·IPE·법제 연구 자료 본문 대조")
    text = re.sub(r"로컬 `([^`]+)` 원문 확인", r"`\1` 판결문 원문 확인", text)
    text = text.replace("로컬 원문·CaseNote 확인", "판결문 원문·CaseNote 확인")
    text = text.replace("로컬 원문 확인", "판결문·보도자료 원문 확인")
    text = text.replace("로컬 교육·재정·법제 보고서에서", "교육·재정·법제 연구 보고서에서")
    text = text.replace("이 폴더에 없다.", "보유 자료에 없다.")
    text = text.replace("`AnthropicClaudeClient`(Claude Opus 5.5 API)", "Claude Opus 5.5 API")
    text = re.sub(r"·\s*@김재효\s*·", "·", text)
    return text


def main():
    raw = SRC.read_text(encoding="utf-8")
    text = sanitize_for_public_web(raw)
    lines = text.splitlines()
    title = lines[0].lstrip("# ").strip() + " (v3.1)"
    meta = lines[2].strip() if len(lines) > 2 else ""
    body_md = "\n".join(lines[3:])

    body_md = re.sub(
        r"\]\(<([^>]+)>\)",
        lambda m: "](" + m.group(1).replace("(", "%28").replace(")", "%29") + ")",
        body_md,
    )

    md = markdown.Markdown(
        extensions=["tables", "toc", "sane_lists", "attr_list"],
        extension_configs={"toc": {"toc_depth": "2-4", "permalink": False}},
    )
    body_html = md.convert(body_md)
    toc_html = md.toc

    body_html = re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" target="_blank" rel="noopener"',
        body_html,
    )
    body_html = re.sub(
        r"<td>(부당|타당|대체로 타당[^<]*)</td>",
        lambda m: f'<td><span class="badge {"bad" if m.group(1)=="부당" else ("good" if m.group(1)=="타당" else "mid")}">{m.group(1)}</span></td>',
        body_html,
    )
    body_html = re.sub(r"<p><strong>(판정:[^<]*)</strong>", r'<p class="verdict"><strong>\1</strong>', body_html)
    body_html = body_html.replace("<p><strong>결론.</strong>", '<p class="conclusion"><strong>결론.</strong>')
    body_html = re.sub(
        r"<p>(방어 가능한 형태로 고쳐 쓰면 다음과 같다:) <em>(.*?)</em></p>",
        r'<div class="callout"><div class="callout-h">\1</div><p>\2</p></div>',
        body_html,
        flags=re.S,
    )
    body_html = body_html.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")

    css = r"""
:root{--p:#1e3a8a;--pl:#3b82f6;--bg:#f8fafc;--card:#fff;--bd:#e2e8f0;--tx:#334155;--hd:#0f172a;--mu:#64748b;
--good:#059669;--goodbg:#d1fae5;--bad:#dc2626;--badbg:#fee2e2;--mid:#b45309;--midbg:#fef3c7}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Noto Sans KR','Malgun Gothic',sans-serif;background:var(--bg);color:var(--tx);line-height:1.8;font-size:16px}
.topbar{background:#0f172a;border-bottom:1px solid rgba(255,255,255,.12);padding:10px 24px;font-size:.86rem;color:#cbd5e1}
.topbar .in{max-width:1180px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.topbar a{color:#93c5fd;text-decoration:none;font-weight:700}
.topbar a:hover{text-decoration:underline;color:#fff}
header{background:linear-gradient(135deg,#0f172a,#1e3a8a);color:#fff;padding:42px 24px 36px}
header .in{max-width:1180px;margin:0 auto}
header .kicker{font-size:.85rem;letter-spacing:.08em;opacity:.78;margin-bottom:8px}
header h1{font-size:2rem;line-height:1.35;font-weight:800}
header .meta{margin-top:12px;opacity:.85;font-size:.95rem}
.notice{max-width:1180px;margin:18px auto 0;padding:10px 24px;font-size:.86rem;color:#475569}
.notice .in{background:#fff;border:1px solid var(--bd);border-left:4px solid var(--pl);border-radius:8px;padding:10px 14px}
.wrap{max-width:1180px;margin:0 auto;display:grid;grid-template-columns:270px 1fr;gap:32px;padding:24px 24px 80px}
nav.toc{position:sticky;top:20px;align-self:start;max-height:calc(100vh - 40px);overflow:auto;background:var(--card);
border:1px solid var(--bd);border-radius:12px;padding:18px 16px;font-size:.86rem}
nav.toc .h{font-weight:700;color:var(--hd);margin-bottom:8px}
nav.toc ul{list-style:none}
nav.toc ul ul{padding-left:12px;border-left:2px solid var(--bd);margin:4px 0 6px 4px}
nav.toc a{color:var(--mu);text-decoration:none;display:block;padding:3px 0}
nav.toc a:hover{color:var(--p)}
main{background:var(--card);border:1px solid var(--bd);border-radius:14px;padding:40px 48px;min-width:0}
main h2{font-size:1.45rem;color:var(--hd);margin:44px 0 16px;padding-bottom:8px;border-bottom:2px solid var(--p)}
main h2:first-child{margin-top:0}
main h3{font-size:1.15rem;color:var(--p);margin:30px 0 12px}
main h4{font-size:1.02rem;color:var(--hd);margin:20px 0 8px}
main p{margin:12px 0}
main ul,main ol{margin:12px 0 12px 24px}
main li{margin:6px 0}
main a{color:var(--pl);text-decoration:none;border-bottom:1px dotted var(--pl)}
main a:hover{color:var(--p)}
code{background:#f1f5f9;padding:1px 6px;border-radius:4px;font-size:.88em;font-family:Consolas,monospace}
.tw{overflow-x:auto;margin:18px 0}
table{border-collapse:collapse;width:100%;font-size:.91rem}
th{background:#eff6ff;color:var(--hd);font-weight:700;text-align:left}
th,td{border:1px solid var(--bd);padding:10px 12px;vertical-align:top}
tr:nth-child(even) td{background:#fafcff}
.badge{display:inline-block;padding:2px 10px;border-radius:999px;font-weight:700;font-size:.85rem;white-space:nowrap}
.badge.good{background:var(--goodbg);color:var(--good)}
.badge.bad{background:var(--badbg);color:var(--bad)}
.badge.mid{background:var(--midbg);color:var(--mid);white-space:normal}
p.verdict{background:#eff6ff;border-left:5px solid var(--p);padding:14px 18px;border-radius:6px}
p.conclusion{background:#f0fdf4;border-left:5px solid var(--good);padding:14px 18px;border-radius:6px}
.callout{background:var(--midbg);border:1px solid #fcd34d;border-radius:10px;padding:16px 20px;margin:18px 0}
.callout-h{font-weight:700;color:var(--mid);margin-bottom:6px}
.callout p{margin:0;font-style:italic}
blockquote{margin:12px 0;padding:12px 18px;background:#f8fafc;border-left:4px solid #94a3b8;color:#1e293b;border-radius:4px;font-family:'Noto Serif KR','Batang',serif}
blockquote p{margin:4px 0}
footer{text-align:center;color:var(--mu);font-size:.85rem;padding:24px}
footer a{color:var(--pl);text-decoration:none;font-weight:700}
#top{position:fixed;right:22px;bottom:22px;background:var(--p);color:#fff;border:none;border-radius:50%;width:44px;height:44px;
font-size:1.2rem;cursor:pointer;box-shadow:0 4px 10px rgba(0,0,0,.2)}
@media(max-width:900px){.wrap{grid-template-columns:1fr}nav.toc{position:static;max-height:none}main{padding:24px 18px}header h1{font-size:1.5rem}}
@media print{.topbar,.notice,nav.toc,#top{display:none}.wrap{display:block;padding:0}main{border:none;padding:0}header{background:none;color:#000;padding:0 0 16px}
a{color:#000;border:none}h2{page-break-after:avoid}table{page-break-inside:auto}tr{page-break-inside:avoid}}
"""

    out = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="topbar"><div class="in">
  <a href="../index.html">← 한의약 보건의료 빅데이터 연구 포털로 돌아가기</a>
  <span>06 한의학교육 혁신·법제 · V3.1 통합본</span>
</div></div>
<header><div class="in">
<div class="kicker">명제 검증 보고서 · 국내 법령·판례 대조 및 제도 경로 시뮬레이션 (V3.1)</div>
<h1>{html.escape(title)}</h1>
<div class="meta">{html.escape(meta)}</div>
</div></header>
<div class="notice"><div class="in">ⓘ 개인 관심 주제와 질문을 기반으로 생성된 분석 보고서이며, 단체나 기관 차원의 합의가 진행된 내용이 아님을 밝힙니다.</div></div>
<div class="wrap">
<nav class="toc"><div class="h">목차</div>{toc_html}</nav>
<main>
{body_html}
</main>
</div>
<footer><a href="../index.html">연구 포털 메인</a> · {html.escape(title)}</footer>
<button id="top" onclick="window.scrollTo({{top:0}})" title="맨 위로">↑</button>
</body>
</html>
"""
    out = out.replace('<div class="toc">', '<div>')
    DST.write_text(out, encoding="utf-8")
    print(
        f"written={DST}, bytes={DST.stat().st_size}, "
        f"tables={body_html.count('<table>')}, h2={body_html.count('<h2')}, "
        f"h3={body_html.count('<h3')}, has_83871={'83871' in out}, has_ISD={'ISD' in out}"
    )


if __name__ == "__main__":
    main()

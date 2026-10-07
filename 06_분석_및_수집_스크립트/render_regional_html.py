# -*- coding: utf-8 -*-
"""
Markdown -> Premium Styled HTML 변환 스크립트
모든 광역지자체 및 시·군 재검증 보고서를 고품질 HTML 문서로 렌더링
"""

import os
import sys
import markdown

if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = r"g:\내 드라이브\한의 의료서비스 통계"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&family=Outfit:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body);"></script>
    <style>
        :root {{
            --primary: #0f172a;
            --primary-accent: #2563eb;
            --secondary-accent: #0d9488;
            --bg-main: #f8fafc;
            --card-bg: #ffffff;
            --text-dark: #1e293b;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --table-header: #1e293b;
            --highlight: #dbeafe;
        }}
        body {{
            font-family: 'Noto Sans KR', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-dark);
            line-height: 1.75;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding: 40px;
            background-color: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.01);
            border: 1px solid var(--border-color);
        }}
        h1 {{
            font-size: 2.2rem;
            color: var(--primary);
            border-bottom: 3px solid var(--primary-accent);
            padding-bottom: 16px;
            margin-bottom: 24px;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}
        h2 {{
            font-size: 1.6rem;
            color: #0f172a;
            margin-top: 40px;
            margin-bottom: 16px;
            border-left: 5px solid var(--secondary-accent);
            padding-left: 12px;
            font-weight: 700;
        }}
        h3 {{
            font-size: 1.25rem;
            color: #334155;
            margin-top: 28px;
            margin-bottom: 12px;
            font-weight: 600;
        }}
        p, li {{
            font-size: 1.05rem;
            color: #334155;
        }}
        blockquote {{
            background: #f1f5f9;
            border-left: 4px solid var(--primary-accent);
            margin: 20px 0;
            padding: 16px 20px;
            border-radius: 0 8px 8px 0;
            color: #475569;
            font-size: 0.98rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            font-size: 0.95rem;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }}
        th {{
            background-color: var(--table-header);
            color: #ffffff;
            text-align: center;
            padding: 12px 14px;
            font-weight: 600;
        }}
        td {{
            padding: 11px 14px;
            border-bottom: 1px solid var(--border-color);
            text-align: center;
        }}
        tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        tr:hover {{
            background-color: #eff6ff;
        }}
        pre {{
            background-color: #0f172a;
            color: #f8fafc;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        code {{
            background-color: #f1f5f9;
            color: #2563eb;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 0.92em;
        }}
        pre code {{
            background-color: transparent;
            color: inherit;
            padding: 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 40px 0;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            background: #e0f2fe;
            color: #0369a1;
        }}
        .footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
        <div class="footer">
            <p>© 2026 한의 의료서비스 통계 및 시뮬레이션 연구팀 | HIRA & KOSIS 빅데이터 연계 분석 로직</p>
        </div>
    </div>
</body>
</html>
"""

FILES_MAP = [
    ("경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md", 
     ["경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html", "gimhae_gyeongnam.html"]),
    ("전라남도_및_여수시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md", 
     ["전라남도_및_여수시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html", "yeosu_jeonnam.html"]),
    ("전주시_및_전북특별자치도_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md", 
     ["전주시_및_전북특별자치도_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html", "jeonju_jeonbuk.html"]),
    ("익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md", 
     ["익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html", "iksan.html"]),
    ("익산시_보건의료_내쉬균형_및_한의약개입_확률시뮬레이션_보고서.md", 
     ["익산시_보건의료_내쉬균형_및_한의약개입_확률시뮬레이션_보고서.html"]),
    ("익산시_한의약_방문진료_돌봄_진료비_시뮬레이션_보고서.md", 
     ["익산시_한의약_방문진료_돌봄_진료비_시뮬레이션_보고서.html"])
]

def render_md_to_html(md_filename, html_filenames):
    md_path = os.path.join(BASE_DIR, md_filename)
    if not os.path.exists(md_path):
        print(f"Skipping missing MD: {md_filename}")
        return
        
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
        
    # extract title from first h1
    first_line = md_text.strip().split('\n')[0]
    title = first_line.replace('#', '').strip()
    
    html_content = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])
    full_html = HTML_TEMPLATE.format(title=title, content=html_content)
    
    for html_fn in html_filenames:
        html_path = os.path.join(BASE_DIR, html_fn)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        print(f"Rendered HTML: {html_fn}")

if __name__ == '__main__':
    for md_file, html_files in FILES_MAP:
        render_md_to_html(md_file, html_files)
    print("\nAll regional HTML reports successfully rendered and synchronized!")

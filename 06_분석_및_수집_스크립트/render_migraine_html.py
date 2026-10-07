# -*- coding: utf-8 -*-
"""
Convert 편두통_한의약_의료서비스_현황_및_확대방안_보고서.md to rich, standalone HTML with Mermaid.js support.
"""

import re
import html

def markdown_to_html(md_text):
    # Escape raw HTML within code blocks or handle tables, headings, lists, bold, italics, mermaid
    lines = md_text.split('\n')
    html_lines = []
    
    in_code = False
    code_lang = ""
    code_buffer = []
    
    in_table = False
    table_buffer = []
    
    in_list = False
    
    def flush_table(buf):
        if not buf:
            return ""
        out = ['<div class="table-wrapper"><table>']
        header_done = False
        for r_idx, row in enumerate(buf):
            # Clean cells
            cells = [c.strip() for c in row.strip().strip('|').split('|')]
            if r_idx == 1 and all(set(c).issubset({'-', ':', ' '}) for c in cells):
                header_done = True
                continue
            if not header_done and r_idx == 0:
                out.append('<thead><tr>' + ''.join(f'<th>{parse_inline(c)}</th>' for c in cells) + '</tr></thead><tbody>')
            else:
                out.append('<tr>' + ''.join(f'<td>{parse_inline(c)}</td>' for c in cells) + '</tr>')
        if not header_done:
            out.append('</tbody>')
        else:
            out.append('</tbody>')
        out.append('</table></div>')
        return '\n'.join(out)

    def parse_inline(text):
        # bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # inline code
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return text

    for line in lines:
        stripped = line.strip()
        
        # Check code fence
        if stripped.startswith('```'):
            if in_code:
                in_code = False
                if code_lang == 'mermaid':
                    html_lines.append(f'<div class="mermaid">\n{"\n".join(code_buffer)}\n</div>')
                else:
                    escaped_code = html.escape('\n'.join(code_buffer))
                    html_lines.append(f'<pre><code class="language-{code_lang}">{escaped_code}</code></pre>')
                code_buffer = []
                code_lang = ""
            else:
                in_code = True
                code_lang = stripped[3:].strip()
                code_buffer = []
            continue
            
        if in_code:
            code_buffer.append(line)
            continue
            
        # Table
        if stripped.startswith('|') and stripped.endswith('|'):
            table_buffer.append(stripped)
            continue
        else:
            if table_buffer:
                html_lines.append(flush_table(table_buffer))
                table_buffer = []

        # Blockquote
        if stripped.startswith('>'):
            content = stripped.lstrip('> ').strip()
            html_lines.append(f'<blockquote><p>{parse_inline(content)}</p></blockquote>')
            continue

        # Horizontal Rule
        if stripped in ('---', '***', '___'):
            html_lines.append('<hr/>')
            continue

        # Headings
        if stripped.startswith('# '):
            html_lines.append(f'<h1>{parse_inline(stripped[2:])}</h1>')
            continue
        if stripped.startswith('## '):
            html_lines.append(f'<h2>{parse_inline(stripped[3:])}</h2>')
            continue
        if stripped.startswith('### '):
            html_lines.append(f'<h3>{parse_inline(stripped[4:])}</h3>')
            continue
        if stripped.startswith('#### '):
            html_lines.append(f'<h4>{parse_inline(stripped[5:])}</h4>')
            continue

        # Lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            html_lines.append(f'<ul><li>{parse_inline(stripped[2:])}</li></ul>')
            continue
        if re.match(r'^\d+\.\s', stripped):
            item = re.sub(r'^\d+\.\s', '', stripped)
            html_lines.append(f'<ol><li>{parse_inline(item)}</li></ol>')
            continue

        # Normal paragraph
        if stripped:
            html_lines.append(f'<p>{parse_inline(stripped)}</p>')
        else:
            html_lines.append('')

    if table_buffer:
        html_lines.append(flush_table(table_buffer))

    body_html = '\n'.join(html_lines)
    
    # Merge consecutive <ul> and <ol>
    body_html = body_html.replace('</ul>\n<ul>', '')
    body_html = body_html.replace('</ol>\n<ol>', '')

    template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>편두통 한의약 의료서비스 현황 및 급여·비급여 확대방안 종합 마스터 보고서</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    }});
  </script>
  <style>
    :root {{
      --primary: #1e3a8a;
      --primary-light: #3b82f6;
      --secondary: #0d9488;
      --bg: #f8fafc;
      --surface: #ffffff;
      --text: #1e293b;
      --text-muted: #64748b;
      --border: #e2e8f0;
      --accent: #d97706;
      --success: #16a34a;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Segoe UI", Roboto, "Noto Sans KR", sans-serif;
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.75;
      padding: 2rem 1rem;
      margin: 0;
    }}
    .container {{
      max-width: 1080px;
      margin: 0 auto;
      background: var(--surface);
      padding: 3rem 3.5rem;
      border-radius: 16px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
      border: 1px solid var(--border);
    }}
    h1 {{
      color: var(--primary);
      font-size: 2.2rem;
      border-bottom: 3px solid var(--primary-light);
      padding-bottom: 0.8rem;
      margin-top: 2rem;
      line-height: 1.3;
    }}
    h2 {{
      color: #1e40af;
      font-size: 1.6rem;
      border-bottom: 1.5px solid var(--border);
      padding-bottom: 0.5rem;
      margin-top: 2.5rem;
    }}
    h3 {{
      color: #0f766e;
      font-size: 1.25rem;
      margin-top: 1.8rem;
    }}
    h4 {{
      color: #334155;
      font-size: 1.05rem;
      margin-top: 1.2rem;
    }}
    p {{
      margin: 0.9rem 0;
      word-break: keep-all;
    }}
    strong {{
      color: #0f172a;
      font-weight: 600;
    }}
    hr {{
      border: none;
      height: 1px;
      background: var(--border);
      margin: 2.5rem 0;
    }}
    blockquote {{
      margin: 1.5rem 0;
      padding: 1rem 1.5rem;
      background: #f1f5f9;
      border-left: 4px solid var(--primary-light);
      border-radius: 0 8px 8px 0;
      color: #334155;
    }}
    blockquote p {{
      margin: 0.3rem 0;
    }}
    .table-wrapper {{
      overflow-x: auto;
      margin: 1.5rem 0;
      border-radius: 8px;
      border: 1px solid var(--border);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
      text-align: left;
    }}
    th {{
      background: #f1f5f9;
      color: #1e293b;
      font-weight: 600;
      padding: 0.75rem 1rem;
      border-bottom: 2px solid var(--border);
    }}
    td {{
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    tr:nth-child(even) td {{
      background: #fafafa;
    }}
    tr:hover td {{
      background: #f8fafc;
    }}
    .mermaid {{
      background: #ffffff;
      padding: 1.5rem;
      margin: 1.5rem 0;
      border-radius: 12px;
      border: 1px solid var(--border);
      display: flex;
      justify-content: center;
    }}
    code {{
      background: #f1f5f9;
      color: #e11d48;
      padding: 0.2rem 0.4rem;
      border-radius: 4px;
      font-size: 0.88em;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }}
    pre {{
      background: #0f172a;
      color: #f8fafc;
      padding: 1.2rem;
      border-radius: 8px;
      overflow-x: auto;
    }}
    pre code {{
      background: transparent;
      color: inherit;
      padding: 0;
    }}
    ul, ol {{
      padding-left: 1.8rem;
      margin: 0.8rem 0;
    }}
    li {{
      margin: 0.35rem 0;
    }}
    @media (max-width: 768px) {{
      .container {{
        padding: 1.5rem;
      }}
      h1 {{
        font-size: 1.7rem;
      }}
      h2 {{
        font-size: 1.35rem;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    {body_html}
  </div>
</body>
</html>
"""
    return template

def main():
    md_file = r"D:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\편두통_한의약_의료서비스_현황_및_확대방안_보고서.md"
    with open(md_file, "r", encoding="utf-8") as f:
        md_text = f.read()

    html_text = markdown_to_html(md_text)

    out_file_1 = r"D:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\편두통_한의약_의료서비스_현황_및_확대방안_보고서.html"
    out_file_2 = r"D:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\편두통_한의약_의료서비스_현황_및_확대방안_보고서.html"

    for of in [out_file_1, out_file_2]:
        with open(of, "w", encoding="utf-8") as f:
            f.write(html_text)

    print("HTML reports successfully rendered to:", out_file_1)

if __name__ == "__main__":
    main()

import fitz
import re
import pandas as pd

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\curriculum.pdf")

courses = []

for pno in range(16, 26):
    page = doc[pno]
    blocks = page.get_text("blocks")
    # Sort blocks by y0, x0
    # Let's inspect block texts
    full_text = page.get_text("text")
    lines = [l.strip() for l in full_text.splitlines() if l.strip()]
    
    # Let's find patterns where a 6-digit number appears (course code)
    for idx, l in enumerate(lines):
        if re.match(r'^\d{6}$', l):
            code = l
            # Look backwards for classification (교필, 전필, 전선, etc.)
            classification = ""
            for b in range(max(0, idx-5), idx):
                if lines[b] in ["교필", "전필", "전선", "일선", "교선"]:
                    classification = lines[b]
                elif lines[b] in ["교", "전"] and b+1 < idx and lines[b+1] in ["필", "선"]:
                    classification = lines[b] + lines[b+1]
            
            # Look forward for name, credit, theory, lab, eng name
            # Usually: Name (1 or 2 lines), Credit (int), Theory (int), Lab (int), Eng name
            name_parts = []
            f_idx = idx + 1
            while f_idx < len(lines) and not re.match(r'^\d+$', lines[f_idx]):
                name_parts.append(lines[f_idx])
                f_idx += 1
            name = "".join(name_parts)
            
            credit = lines[f_idx] if f_idx < len(lines) else ""
            theory = lines[f_idx+1] if f_idx+1 < len(lines) else ""
            lab = lines[f_idx+2] if f_idx+2 < len(lines) else ""
            
            # eng name
            eng_idx = f_idx + 3
            eng_parts = []
            while eng_idx < len(lines) and not re.match(r'^\d{6}$', lines[eng_idx]) and lines[eng_idx] not in ["교필", "전필", "전선", "교선", "교", "전", "예1", "예2", "본1", "본2", "본3", "본4", "1", "2"]:
                if "2024" in lines[eng_idx] or "교육과정" in lines[eng_idx] or "시간" in lines[eng_idx] or "구분" in lines[eng_idx]:
                    break
                eng_parts.append(lines[eng_idx])
                eng_idx += 1
            eng_name = " ".join(eng_parts)
            
            courses.append({
                "page": pno + 1,
                "code": code,
                "classification": classification,
                "name": name,
                "credit": credit,
                "theory": theory,
                "lab": lab,
                "eng_name": eng_name
            })

df = pd.DataFrame(courses)
print(f"Extracted {len(df)} courses")
print(df.to_string())
df.to_excel(r"d:\행정\한의학 교육과 의료 통합\01_교육과정_혁신로드맵\분석자료\wonkwang_curriculum_extracted.xlsx", index=False)

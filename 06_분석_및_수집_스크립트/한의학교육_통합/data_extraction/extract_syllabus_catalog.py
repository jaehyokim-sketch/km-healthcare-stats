import fitz
import re
import json
import pandas as pd

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\curriculum.pdf")

syllabus_courses = []

# Each syllabus usually starts with a heading or table: 교과목명, 학수번호, 학년/학기, 학점/시수, 담당교수, 교육목표 등
for pno in range(26, len(doc)):
    text = doc[pno].get_text("text")
    if "수업계획서" in text or "교과목명" in text or "교과목 해설서" in text or "학수번호" in text:
        # Extract course info
        # Let's search for patterns
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        
        course_name = ""
        course_code = ""
        grade_sem = ""
        credits_hours = ""
        course_type = ""
        
        for i, l in enumerate(lines):
            if "교과목명" in l and i+1 < len(lines):
                course_name = lines[i+1]
            elif "학수번호" in l and i+1 < len(lines):
                course_code = lines[i+1]
            elif "이수구분" in l and i+1 < len(lines):
                course_type = lines[i+1]
            elif "학점/시수" in l and i+1 < len(lines):
                credits_hours = lines[i+1]
            elif "개설학년/학기" in l and i+1 < len(lines):
                grade_sem = lines[i+1]
                
        if course_name or course_code:
            syllabus_courses.append({
                "page": pno + 1,
                "name": course_name,
                "code": course_code,
                "type": course_type,
                "grade_sem": grade_sem,
                "credits_hours": credits_hours,
                "sample_text": text[:300]
            })

print(f"Found {len(syllabus_courses)} syllabus pages.")
with open(r"d:\행정\한의학 교육과 의료 통합\_archive\intermediate_outputs\syllabus_catalog.json", "w", encoding="utf-8") as f:
    json.dump(syllabus_courses, f, ensure_ascii=False, indent=2)

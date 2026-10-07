# -*- coding: utf-8 -*-
import os
import shutil

base_dir = r"g:\내 드라이브\한의 의료서비스 통계"

src_html = os.path.join(base_dir, "한의사_재택의료_방문진료_참여확대_종합분석_및_정책제언_보고서.html")
dst_html = os.path.join(base_dir, "policy_report.html")

if os.path.exists(src_html):
    shutil.copyfile(src_html, dst_html)
    print(f"Copied {src_html} -> {dst_html}")
else:
    print(f"Source file not found: {src_html}")

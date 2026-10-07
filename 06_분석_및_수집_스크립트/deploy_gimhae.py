# -*- coding: utf-8 -*-
import os
import sys
import json
import base64
import urllib.request
import urllib.error

def upload_via_github_api():
    base_dir = r"g:\내 드라이브\한의 의료서비스 통계"
    username = "jaehyokim-sketch"
    repo_name = "km-healthcare-stats"

    # 업로드 대상 파일 목록 (로컬경로, 원격파일명, 바이너리 여부)
    files = [
        (os.path.join(base_dir, "gimhae_gyeongnam.html"), "gimhae_gyeongnam.html", False),
        (os.path.join(base_dir, "gimhae_gyeongnam_report.md"), "gimhae_gyeongnam_report.md", False),
        (os.path.join(base_dir, "gimhae_gyeongnam_simulation_chart.png"), "gimhae_gyeongnam_simulation_chart.png", True),
        (os.path.join(base_dir, "gimhae_gyeongnam_full_simulation.json"), "gimhae_gyeongnam_full_simulation.json", False),
        (os.path.join(base_dir, "index.html"), "index.html", False),
        (os.path.join(base_dir, "경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html"), "경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html", False),
        (os.path.join(base_dir, "경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md"), "경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md", False)
    ]

    print("[INFO] GitHub API를 통해 리포지토리에 파일 직접 업로드를 시도합니다...")
    
    # 깃허브 토큰 환경변수 또는 커맨드라인에서 확인
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    
    # git credential 도구를 통해 토큰 획득 시도
    if not token:
        try:
            import subprocess
            proc = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n", capture_output=True, text=True)
            for line in proc.stdout.splitlines():
                if line.startswith("password="):
                    token = line.split("=", 1)[1].strip()
                    break
        except Exception as e:
            print(f"[WARN] Git credential helper 조회 실패: {e}")

    if not token:
        print("[ERROR] GitHub Personal Access Token을 찾을 수 없습니다.")
        return False

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Gimhae-Deployer",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    success_count = 0
    for local_path, remote_path, is_binary in files:
        if not os.path.exists(local_path):
            print(f"[SKIP] 로컬 파일이 없음: {local_path}")
            continue

        if is_binary:
            with open(local_path, "rb") as f:
                b64_content = base64.b64encode(f.read()).decode("utf-8")
        else:
            with open(local_path, "r", encoding="utf-8") as f:
                b64_content = base64.b64encode(f.read().encode("utf-8")).decode("utf-8")

        url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{urllib.parse.quote(remote_path)}"
        
        # SHA 확인 (기존 파일 존재하는지)
        sha = None
        try:
            req_get = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req_get) as res:
                info = json.loads(res.read().decode("utf-8"))
                sha = info.get("sha")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                print(f"[WARN] SHA 조회 HTTP {e.code}: {remote_path}")

        payload = {
            "message": f"Deploy {remote_path} via API",
            "content": b64_content
        }
        if sha:
            payload["sha"] = sha

        data_bytes = json.dumps(payload).encode("utf-8")
        req_put = urllib.request.Request(url, data=data_bytes, headers=headers, method="PUT")

        try:
            with urllib.request.urlopen(req_put) as res:
                if res.status in [200, 201]:
                    print(f"[OK] 업로드 성공: {remote_path}")
                    success_count += 1
                else:
                    print(f"[FAIL] HTTP {res.status}: {remote_path}")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8")
            print(f"[ERROR] HTTP {e.code} ({remote_path}): {err_msg}")

    print(f"\n[SUMMARY] 총 {len(files)}개 중 {success_count}개 파일 업로드 완료!")
    return success_count > 0

if __name__ == '__main__':
    upload_via_github_api()

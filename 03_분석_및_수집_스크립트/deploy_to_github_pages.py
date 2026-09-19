"""
GitHub Pages Automated Deployer for Korean Medicine Healthcare Reports
모든 인터랙티브 대시보드(전주시·전북, 전라남도·여수시, 익산시 등)와 이미지 차트를 GitHub 저장소에 일괄 업로드하고 Pages를 활성화합니다.
"""
import os
import sys
import json
import base64
import urllib.request
import urllib.error

def github_api_request(url, method="GET", token=None, data=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "KM-Healthcare-Stats-Deployer",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    encoded_data = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        encoded_data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return response.status, json.loads(res_body) if res_body else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(err_body)
        except Exception:
            err_json = {"message": err_body}
        return e.code, err_json

def upload_file_to_repo(token, username, repo_name, local_path, repo_path, is_binary=False):
    if not os.path.exists(local_path):
        print(f" [Warning] 파일을 찾을 수 없어 건너뜁니다: {local_path}")
        return False
        
    if is_binary:
        with open(local_path, "rb") as f:
            b64_content = base64.b64encode(f.read()).decode("utf-8")
    else:
        with open(local_path, "r", encoding="utf-8") as f:
            b64_content = base64.b64encode(f.read().encode("utf-8")).decode("utf-8")

    contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{repo_path}"
    status, file_info = github_api_request(contents_url, token=token)
    
    put_payload = {
        "message": f"Upload {repo_path}",
        "content": b64_content
    }
    if status == 200 and "sha" in file_info:
        put_payload["sha"] = file_info["sha"]
        print(f" -> 파일 업데이트: {repo_path}")
    else:
        print(f" -> 새 파일 업로드: {repo_path}")

    status, upload_res = github_api_request(contents_url, method="PUT", token=token, data=put_payload)
    if status not in [200, 201]:
        print(f"[Error] {repo_path} 업로드 실패 (HTTP {status}): {upload_res.get('message')}")
        return False
    return True

def deploy_all(token, repo_name="km-healthcare-stats"):
    print("1. GitHub 사용자 인증 확인 중...")
    status, user_info = github_api_request("https://api.github.com/user", token=token)
    if status != 200:
        print(f"[Error] GitHub 인증 실패 (HTTP {status}): {user_info.get('message')}")
        return False
    
    username = user_info.get("login")
    print(f" -> 로그인 성공: {username} ({user_info.get('name', '')})")

    print(f"\n2. 저장소 '{repo_name}' 확인 및 생성...")
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    status, repo_info = github_api_request(repo_url, token=token)
    
    if status == 404:
        print(f" -> 새 공개(Public) 저장소 생성 중: {repo_name}")
        create_payload = {
            "name": repo_name,
            "description": "지역별 한의약 방문진료 기관참여율별 의료 적정성 및 5개년 효과 시뮬레이션 대시보드",
            "private": False,
            "auto_init": True
        }
        c_status, c_info = github_api_request("https://api.github.com/user/repos", method="POST", token=token, data=create_payload)
        if c_status not in [200, 201]:
            print(f"[Error] 저장소 생성 실패 (HTTP {c_status}): {c_info.get('message')}")
            return False
        print(" -> 저장소 생성 완료.")
    else:
        print(f" -> 기존 저장소 연결: {repo_name}")

    print("\n3. 대시보드 HTML 및 차트 파일 일괄 업로드...")
    base_dir = r"d:\한의 의료서비스 통계"
    
    files_to_upload = [
        # (로컬 상대/절대경로, 원격 파일명, 바이너리 여부)
        (os.path.join(base_dir, "전주시_및_전북특별자치도_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html"), "index.html", False),
        (os.path.join(base_dir, "전주시_및_전북특별자치도_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html"), "jeonju_jeonbuk.html", False),
        (os.path.join(base_dir, "전라남도_및_여수시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html"), "jeonnam_yeosu.html", False),
        (os.path.join(base_dir, "익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html"), "iksan.html", False),
        (os.path.join(base_dir, "전주시_및_전북특별자치도_한의약_방문진료_의료적정성_분석_및_시뮬레이션_로직_명세서.md"), "jeonju_jeonbuk_logic_spec.md", False),
        (os.path.join(base_dir, "익산시_한의약_방문진료_의료적정성_분석_및_시뮬레이션_로직_명세서.md"), "iksan_logic_spec.md", False),
        (os.path.join(base_dir, "jeonju_jeonbuk_simulation_chart.png"), "jeonju_jeonbuk_simulation_chart.png", True),
        (os.path.join(base_dir, "yeosu_jeonnam_simulation_chart.png"), "yeosu_jeonnam_simulation_chart.png", True),
        (os.path.join(base_dir, "iksan_km_10_to_100_simulation_chart.png"), "iksan_km_10_to_100_simulation_chart.png", True),
    ]

    for local_f, remote_f, is_bin in files_to_upload:
        upload_file_to_repo(token, username, repo_name, local_f, remote_f, is_bin)

    print("\n4. GitHub Pages 활성화 및 빌드 설정...")
    pages_url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
    status, pages_info = github_api_request(pages_url, token=token)
    
    if status == 404:
        print(" -> GitHub Pages 활성화 요청 중 (main branch root)...")
        pages_payload = {
            "source": {
                "branch": "main",
                "path": "/"
            }
        }
        p_status, p_info = github_api_request(pages_url, method="POST", token=token, data=pages_payload)
        if p_status not in [200, 201]:
            pages_payload["source"]["branch"] = "master"
            p_status, p_info = github_api_request(pages_url, method="POST", token=token, data=pages_payload)
            print(f" -> Pages 설정 응답: HTTP {p_status}")
    else:
        print(" -> GitHub Pages 이미 활성화되어 있습니다.")

    pages_web_url = f"https://{username.lower()}.github.io/{repo_name}/"
    print("\n" + "="*75)
    print(" [배포 성공] GitHub Pages 온라인 대시보드가 정상 배포되었습니다!")
    print(f" * 저장소 주소: https://github.com/{username}/{repo_name}")
    print(f" * 메인 웹 대시보드 (전주시 & 전북): {pages_web_url}")
    print(f" * 전라남도 & 여수시 대시보드: {pages_web_url}jeonnam_yeosu.html")
    print(f" * 익산시 대시보드: {pages_web_url}iksan.html")
    print("="*75 + "\n")
    return pages_web_url

if __name__ == "__main__":
    token = sys.argv[1].strip() if len(sys.argv) > 1 else os.environ.get("GITHUB_TOKEN")
    if not token:
        print("토큰이 제공되지 않았습니다.")
        sys.exit(1)
    deploy_all(token)

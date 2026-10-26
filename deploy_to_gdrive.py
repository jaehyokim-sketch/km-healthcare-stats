"""
deploy_to_gdrive.py - Deploy/Sync km-healthcare-stats artifacts from Local to Google Drive.

Usage:
    python deploy_to_gdrive.py [--dry-run] [--prune]
"""
import atexit, os, sys, shutil, argparse

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LOCAL_REPO = r"C:\workspace\km-healthcare-stats"
DEFAULT_DEST = r"G:\내 드라이브\한의 의료서비스 통계"

def resolve_gdrive_dest():
    if os.path.exists(DEFAULT_DEST):
        return DEFAULT_DEST
    for letter in ['G', 'H', 'D', 'E', 'F']:
        alt = DEFAULT_DEST.replace('G:', f'{letter}:').replace('D:', f'{letter}:')
        if os.path.exists(alt):
            return alt
    return DEFAULT_DEST

GDRIVE_DEST = resolve_gdrive_dest()

IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
    ".idea",
    ".vscode",
    "04_CLI_대화세션_아카이브"
}

IGNORE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".lock",
    ".swp",
    ".bak"
}

# Google Drive 정본 원칙(2026-10-26): 최상위 지침 파일(CLAUDE.md·AGENTS.md·GEMINI.md, .claude/·.agents/)은
# Drive 배포 폴더 쪽이 정본이고 로컬은 미러다(acupoint_anatomy/scripts/sync_claude_skill.py). 배포·prune하지 않는다.
RULE_FILES = {"CLAUDE.md", "AGENTS.md", "GEMINI.md"}
RULE_DIRS = {".claude", ".agents"}


def is_rule_path(rel_path):
    parts = rel_path.replace("\\", "/").split("/")
    return parts[0] in RULE_DIRS or (len(parts) == 1 and parts[0] in RULE_FILES)


# Google Drive 정본 원칙(2026-10-26): Drive 쪽 파일이 로컬보다 새로우면(다른 PC나 Drive에서 고친 파일)
# 덮어쓰지 않고 목록만 알린다. 로컬 판으로 바꾸려면 Drive 파일을 확인한 뒤 로컬 파일을 다시 저장하고 배포한다.
NEWER_ON_DRIVE = []


def _report_newer_on_drive():
    if NEWER_ON_DRIVE:
        print(f"[주의] Drive 쪽이 더 새로운 파일 {len(NEWER_ON_DRIVE)}개는 덮어쓰지 않았습니다:")
        for p in NEWER_ON_DRIVE[:30]:
            print(f"  [DRIVE NEWER] {p}")


atexit.register(_report_newer_on_drive)


def _same_content(src_file, dest_file, limit=50 * 1024 * 1024):
    """내용이 같으면(줄바꿈 CRLF/LF 차이만 있어도) True. 같으면 로컬 수정 시각을 Drive에 맞춰 다음 비교를 빠르게 한다."""
    try:
        if max(os.path.getsize(src_file), os.path.getsize(dest_file)) > limit:
            return False
        with open(src_file, "rb") as a, open(dest_file, "rb") as b:
            sa, sb = a.read(), b.read()
        if sa != sb and sa.replace(b"\r\n", b"\n") != sb.replace(b"\r\n", b"\n"):
            return False
        os.utime(src_file, (os.path.getatime(src_file), os.path.getmtime(dest_file)))
        return True
    except OSError:
        return False


def sync_to_gdrive(dry_run=False, prune=False):
    mode_str = "[DRY RUN]" if dry_run else "[LIVE DEPLOY]"
    print("=" * 60)
    print("  km-healthcare-stats Local -> Google Drive Sync Deployment")
    print(f"  Source : {LOCAL_REPO}")
    print(f"  Target : {GDRIVE_DEST}")
    print(f"  Mode   : {mode_str}")
    if prune:
        print("  Prune  : [ENABLED] (Deleted local files/folders will be removed from GDrive)")
    print("=" * 60)

    if not os.path.exists(LOCAL_REPO):
        print(f"Error: Local repo does not exist at {LOCAL_REPO}")
        return False
    if not os.path.exists(GDRIVE_DEST):
        print(f"Target directory does not exist, creating: {GDRIVE_DEST}")
        if not dry_run:
            os.makedirs(GDRIVE_DEST, exist_ok=True)

    copied = 0
    skipped = 0

    for root, dirs, files in os.walk(LOCAL_REPO):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not (root == LOCAL_REPO and d in RULE_DIRS)]

        rel_dir = os.path.relpath(root, LOCAL_REPO)
        target_dir = os.path.join(GDRIVE_DEST, rel_dir) if rel_dir != "." else GDRIVE_DEST

        if not os.path.exists(target_dir) and not dry_run:
            os.makedirs(target_dir, exist_ok=True)

        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in IGNORE_EXTENSIONS or f.startswith("~$") or (f.startswith(".") and f not in [".gitignore", ".nojekyll"]):
                continue

            src_file = os.path.join(root, f)
            dest_file = os.path.join(target_dir, f)
            if is_rule_path(os.path.relpath(src_file, LOCAL_REPO)):
                continue

            need_copy = False
            if not os.path.exists(dest_file):
                need_copy = True
            else:
                try:
                    src_stat = os.stat(src_file)
                    dst_stat = os.stat(dest_file)
                    if dst_stat.st_mtime > src_stat.st_mtime + 2.0 and src_stat.st_size != dst_stat.st_size or dst_stat.st_mtime > src_stat.st_mtime + 2.0 and open(src_file, 'rb').read() != open(dest_file, 'rb').read():
                        NEWER_ON_DRIVE.append(os.path.relpath(src_file, LOCAL_REPO))
                    elif (src_stat.st_size != dst_stat.st_size or abs(src_stat.st_mtime - dst_stat.st_mtime) > 1.0) and not _same_content(src_file, dest_file):
                        need_copy = True
                except Exception:
                    need_copy = True

            if need_copy:
                copied += 1
                rel_path = os.path.relpath(src_file, LOCAL_REPO)
                if dry_run:
                    print(f"  [COPY] {rel_path}")
                else:
                    try:
                        shutil.copy2(src_file, dest_file)
                    except Exception as e:
                        print(f"  [ERROR] {rel_path}: {e}")
            else:
                skipped += 1

    pruned_files = 0
    pruned_dirs = 0

    if prune:
        print("\nChecking for files to prune in Google Drive...")
        for root, dirs, files in os.walk(GDRIVE_DEST, topdown=False):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            rel_dir = os.path.relpath(root, GDRIVE_DEST)
            local_dir = os.path.join(LOCAL_REPO, rel_dir) if rel_dir != "." else LOCAL_REPO

            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in IGNORE_EXTENSIONS or f.startswith("~$") or f.endswith(".gdoc") or f.endswith(".gsheet"):
                    continue

                dest_file = os.path.join(root, f)
                src_file = os.path.join(local_dir, f)
                if is_rule_path(os.path.relpath(dest_file, GDRIVE_DEST)):
                    continue

                if not os.path.exists(src_file):
                    pruned_files += 1
                    rel_path = os.path.relpath(dest_file, GDRIVE_DEST)
                    if dry_run:
                        print(f"  [PRUNE FILE] {rel_path}")
                    else:
                        try:
                            os.remove(dest_file)
                            print(f"  [DELETED FILE] {rel_path}")
                        except Exception as e:
                            print(f"  [ERROR] Failed to delete file {rel_path}: {e}")

        for root, dirs, files in os.walk(GDRIVE_DEST, topdown=False):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            rel_dir = os.path.relpath(root, GDRIVE_DEST)
            if rel_dir == "." or is_rule_path(rel_dir):
                continue
            local_dir = os.path.join(LOCAL_REPO, rel_dir)

            is_empty = False
            try:
                is_empty = (len(os.listdir(root)) == 0)
            except Exception:
                pass

            if is_empty and not os.path.exists(local_dir):
                pruned_dirs += 1
                if dry_run:
                    print(f"  [PRUNE DIR] {rel_dir}")
                else:
                    try:
                        os.rmdir(root)
                        print(f"  [DELETED DIR] {rel_dir}")
                    except Exception as e:
                        print(f"  [ERROR] Failed to delete dir {rel_dir}: {e}")

    print("-" * 60)
    print("Deployment Summary:")
    print(f"  Copied/Updated : {copied} files")
    print(f"  Up-to-date     : {skipped} files")
    if prune:
        print(f"  Pruned/Removed : {pruned_files} files, {pruned_dirs} directories")
    print("Google Drive is synchronized with local workspace.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync local repo to Google Drive")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without copying/deleting")
    parser.add_argument("--prune", action="store_true", help="Remove files/dirs from Google Drive that do not exist locally")
    args = parser.parse_args()
    sync_to_gdrive(dry_run=args.dry_run, prune=args.prune)

"""Đăng công cụ thu lên GitHub Pages, ở nhánh gh-pages của kho này.

    python tools/thu-net/dang-trang.py [địa chỉ kho]

Mã chạy được từ bất kỳ thư mục nào. Mã tạo một kho git tạm, lấy nhánh gh-pages hiện có nếu đã có, đóng gói
tools/thu-net/index.html bằng dong-goi.py vào đó, thêm tệp .nojekyll, rồi commit và đẩy lên nhánh gh-pages.
Nhánh gh-pages chỉ chứa trang đã đóng gói, không chứa mã nguồn hay tài liệu của đề tài. Mã không đẩy đè:
mỗi lần đăng thêm một commit lên nhánh, và không làm gì khi trang không đổi.

Địa chỉ kho mặc định là origin của kho này. Lần đầu, cần chọn nhánh gh-pages làm nguồn của Pages trong phần
cài đặt của kho, mã sẽ in đường dẫn tới trang cài đặt đó.
"""
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BRANCH = "gh-pages"


def git(args, cwd, capture=False):
    if not capture:
        # Không in phần -c tên=giá trị, để màn hình chỉ hiện lệnh chính.
        shown = [a for i, a in enumerate(args) if a != "-c" and (i == 0 or args[i - 1] != "-c")]
        print("$ git " + " ".join(shown), flush=True)
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=capture, text=True)
    if r.returncode != 0:
        if capture:
            sys.stderr.write(r.stderr)
        raise SystemExit("Lệnh git thất bại: git " + " ".join(args))
    return r.stdout.strip() if capture else ""


def remove_tree(path):
    # Git đặt các tệp trong .git ở chế độ chỉ đọc, nên trên Windows phải bỏ cờ này trước khi xóa.
    def fix(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=fix)
    else:
        shutil.rmtree(path, onerror=fix)


def main(argv):
    url = argv[0] if argv else git(["remote", "get-url", "origin"], REPO, capture=True)
    page = open(os.path.join(HERE, "index.html"), encoding="utf8").read()
    m = re.search(r"const TOOL_VERSION = '([^']+)'", page)
    version = m.group(1) if m else "không rõ"
    # Commit trong kho tạm mang đúng tên và email của kho chính.
    who = []
    for key in ("user.name", "user.email"):
        r = subprocess.run(["git", "config", key], cwd=REPO, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            who += ["-c", "%s=%s" % (key, r.stdout.strip())]
    tmp = tempfile.mkdtemp(prefix="thu-net-site-")
    try:
        git(["init", "-q"], tmp)
        git(["remote", "add", "origin", url], tmp)
        if git(["ls-remote", "--heads", "origin", BRANCH], tmp, capture=True):
            git(["fetch", "-q", "--depth", "1", "origin", BRANCH], tmp)
            git(["checkout", "-q", "-b", BRANCH, "FETCH_HEAD"], tmp)
        else:
            git(["checkout", "-q", "-b", BRANCH], tmp)
        r = subprocess.run([sys.executable, os.path.join(HERE, "dong-goi.py"), tmp])
        if r.returncode != 0:
            raise SystemExit("Đóng gói thất bại.")
        open(os.path.join(tmp, ".nojekyll"), "w").close()
        git(["-c", "core.autocrlf=false", "add", "index.html", ".nojekyll"], tmp)
        if not git(["status", "--porcelain"], tmp, capture=True):
            print("Trang trên nhánh %s đã là bản %s, không có gì để đăng." % (BRANCH, version))
        else:
            git(who + ["commit", "-q", "-m", "Trang công cụ thu, bản %s" % version], tmp)
            git(["push", "origin", BRANCH], tmp)
            print("Đã đăng bản %s lên nhánh %s." % (version, BRANCH), flush=True)
    finally:
        remove_tree(tmp)
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if m:
        owner, repo = m.group(1), m.group(2)
        print("\nNếu đây là lần đầu, mở https://github.com/%s/%s/settings/pages, chọn Branch là %s và thư mục / (root), rồi bấm Save." % (owner, repo, BRANCH))
        print("Sau một đến hai phút, trang ở https://%s.github.io/%s/" % (owner.lower(), repo))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

from __future__ import annotations

import shutil
import sys
import urllib.request
from pathlib import Path

YTDLP_EXE_URL = (
    "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
)


def download_file(url: str, target: Path) -> None:
    print(f"[다운로드] {url}")
    with urllib.request.urlopen(url) as response, target.open("wb") as output:
        shutil.copyfileobj(response, output)
    print(f"[완료] {target}")


def main() -> int:
    if not sys.platform.startswith("win"):
        print("이 스크립트는 Windows(yt-dlp.exe) 기준으로 작성되었습니다.")
        return 1

    project_root = Path(__file__).resolve().parents[1]
    bin_dir = project_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    target = bin_dir / "yt-dlp.exe"
    try:
        download_file(YTDLP_EXE_URL, target)
    except Exception as exc:
        print(f"[오류] yt-dlp 다운로드 실패: {exc}")
        return 1
    print("[완료] yt-dlp 바이너리 준비 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

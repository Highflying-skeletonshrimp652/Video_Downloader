from __future__ import annotations

import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

FFMPEG_ZIP_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def download_file(url: str, target: Path) -> None:
    print(f"[다운로드] {url}")
    with urllib.request.urlopen(url) as response, target.open("wb") as output:
        shutil.copyfileobj(response, output)
    print(f"[완료] {target}")


def extract_ffmpeg(zip_path: Path, bin_dir: Path) -> None:
    extracted = 0
    targets = {"ffmpeg.exe"}
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            filename = Path(member).name.lower()
            if filename in targets:
                destination = bin_dir / Path(member).name
                with archive.open(member) as src, destination.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                print(f"[추출] {destination}")
                extracted += 1

    if extracted == 0 or not (bin_dir / "ffmpeg.exe").exists():
        raise RuntimeError("ffmpeg.exe 추출에 실패했습니다.")


def main() -> int:
    if not sys.platform.startswith("win"):
        print("이 스크립트는 Windows(ffmpeg.exe) 기준으로 작성되었습니다.")
        return 1

    project_root = Path(__file__).resolve().parents[1]
    bin_dir = project_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    zip_path = bin_dir / "ffmpeg-release-essentials.zip"
    try:
        download_file(FFMPEG_ZIP_URL, zip_path)
        extract_ffmpeg(zip_path, bin_dir)
    except Exception as exc:
        print(f"[오류] ffmpeg 다운로드/추출 실패: {exc}")
        return 1
    finally:
        if zip_path.exists():
            zip_path.unlink()
    print("[완료] ffmpeg 바이너리 준비 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

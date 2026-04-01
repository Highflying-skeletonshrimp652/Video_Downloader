from __future__ import annotations

import json
import re
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

ARIA2_LATEST_RELEASE_API = "https://api.github.com/repos/aria2/aria2/releases/latest"
ARIA2_ZIP_FALLBACK_URL = (
    "https://github.com/aria2/aria2/releases/download/release-1.37.0/"
    "aria2-1.37.0-win-64bit-build1.zip"
)
ASSET_PATTERN = re.compile(r"aria2-.*-win-64bit-build1\.zip$", re.IGNORECASE)


def download_file(url: str, target: Path) -> None:
    print(f"[다운로드] {url}")
    with urllib.request.urlopen(url) as response, target.open("wb") as output:
        shutil.copyfileobj(response, output)
    print(f"[완료] {target}")


def extract_aria2c(zip_path: Path, bin_dir: Path) -> None:
    extracted = 0
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.namelist():
            if Path(member).name.lower() != "aria2c.exe":
                continue
            destination = bin_dir / "aria2c.exe"
            with archive.open(member) as src, destination.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            print(f"[추출] {destination}")
            extracted += 1

    if extracted == 0 or not (bin_dir / "aria2c.exe").exists():
        raise RuntimeError("aria2c.exe 추출에 실패했습니다.")


def discover_latest_asset_url() -> str | None:
    try:
        request = urllib.request.Request(
            ARIA2_LATEST_RELEASE_API,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "VideoDownloaderBuilder/1.0"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
        assets = payload.get("assets", []) if isinstance(payload, dict) else []
        for asset in assets:
            if not isinstance(asset, dict):
                continue
            name = str(asset.get("name", ""))
            if ASSET_PATTERN.search(name):
                url = str(asset.get("browser_download_url", ""))
                if url:
                    return url
    except Exception:
        return None
    return None


def main() -> int:
    if not sys.platform.startswith("win"):
        print("이 스크립트는 Windows(aria2c.exe) 기준으로 작성되었습니다.")
        return 1

    project_root = Path(__file__).resolve().parents[1]
    bin_dir = project_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    zip_path = bin_dir / "aria2-release.zip"
    download_candidates: list[str] = []
    latest_asset_url = discover_latest_asset_url()
    if latest_asset_url:
        download_candidates.append(latest_asset_url)
    if ARIA2_ZIP_FALLBACK_URL not in download_candidates:
        download_candidates.append(ARIA2_ZIP_FALLBACK_URL)

    try:
        last_error: Exception | None = None
        downloaded = False
        for url in download_candidates:
            try:
                download_file(url, zip_path)
                downloaded = True
                break
            except Exception as exc:
                print(f"[경고] 다운로드 실패: {url} ({exc})")
                last_error = exc
        if not downloaded:
            raise RuntimeError(f"aria2c 다운로드 실패: {last_error}")

        extract_aria2c(zip_path, bin_dir)
    except Exception as exc:
        print(f"[오류] aria2c 다운로드/추출 실패: {exc}")
        return 1
    finally:
        if zip_path.exists():
            zip_path.unlink()

    print("[완료] aria2c 바이너리 준비 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

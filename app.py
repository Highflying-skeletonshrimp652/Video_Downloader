from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import traceback
import html
import urllib.request
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from PySide6.QtCore import QTimer, Qt, QThread, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from platform_policy import evaluate_url

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


MODE_VIDEO = "비디오 + 오디오"
MODE_AUDIO_ONLY = "오디오만"

VIDEO_QUALITY_OPTIONS = [
    "자동 (최고 화질)",
    "2160p 이하 (4K)",
    "1440p 이하 (2K)",
    "1080p 이하",
    "720p 이하",
    "480p 이하",
    "360p 이하",
]
VIDEO_SELECTOR_MAP = {
    "자동 (최고 화질)": "bestvideo*",
    "2160p 이하 (4K)": "bestvideo*[height<=2160]",
    "1440p 이하 (2K)": "bestvideo*[height<=1440]",
    "1080p 이하": "bestvideo*[height<=1080]",
    "720p 이하": "bestvideo*[height<=720]",
    "480p 이하": "bestvideo*[height<=480]",
    "360p 이하": "bestvideo*[height<=360]",
}

AUDIO_QUALITY_OPTIONS = [
    "자동 (최고 음질)",
    "192kbps 이하",
    "128kbps 이하",
    "96kbps 이하",
    "64kbps 이하",
]
AUDIO_SELECTOR_MAP = {
    "자동 (최고 음질)": "bestaudio",
    "192kbps 이하": "bestaudio[abr<=192]",
    "128kbps 이하": "bestaudio[abr<=128]",
    "96kbps 이하": "bestaudio[abr<=96]",
    "64kbps 이하": "bestaudio[abr<=64]",
}

AUDIO_FORMAT_OPTIONS = ["원본 유지", "mp3", "m4a", "wav"]
AUDIO_CODEC_MAP = {"mp3": "mp3", "m4a": "m4a", "wav": "wav"}

APP_NAME = "Video Downloader"
APP_DIR_NAME = "VideoDownloader"
APP_WINDOW_WIDTH = 1040
APP_WINDOW_HEIGHT = 760

BUY_ME_A_COFFEE_URL = "https://www.buymeacoffee.com/aminora"

HISTORY_STATUS_PENDING = "진행 중"
HISTORY_STATUS_SUCCESS = "성공"
HISTORY_STATUS_FAILED = "실패"

LEGAL_NOTICE_TEXT = (
    "제1조 (목적)\n\n"
    "본 도구(이하 \"소프트웨어\")는 사용자가 합법적으로 접근 및 이용 권한을 보유한 콘텐츠를 "
    "개인적·적법한 범위 내에서 저장할 수 있도록 지원하기 위해 제공됩니다.\n\n"
    "본 소프트웨어는 저작권 침해, 약관 위반 또는 기술적 보호조치 우회를 목적으로 설계되지 않았으며, "
    "그러한 행위를 지원하지 않습니다.\n\n"
    "제2조 (이용자의 준수 의무)\n\n"
    "사용자는 콘텐츠에 대한 다운로드 및 저장 권한을 스스로 확인할 책임이 있습니다.\n"
    "사용자는 거주 국가의 저작권법, 관련 법령 및 해당 서비스의 이용약관을 준수하여야 합니다.\n"
    "저작권자 또는 권리자로부터 명시적 허락을 받지 않은 콘텐츠의 다운로드는 금지됩니다.\n"
    "다운로드한 콘텐츠의 판매, 공유, 재배포, 공개 업로드 또는 상업적 이용은 금지됩니다.\n\n"
    "제3조 (지원 범위 및 제한)\n\n"
    "본 소프트웨어는 DRM(디지털 권리 관리) 또는 기타 기술적 보호조치가 적용된 콘텐츠를 지원하지 않습니다.\n"
    "DRM 또는 보호조치가 감지되는 경우 다운로드는 자동으로 차단됩니다.\n"
    "로그인 세션, 쿠키, 인증 토큰 등을 자동으로 수집하거나 우회하는 기능은 제공하지 않습니다.\n"
    "본 소프트웨어는 특정 플랫폼 전용 도구가 아니며, 내부 정책에 따라 허용된 도메인(allowlist) 범위 내에서만 동작합니다.\n\n"
    "제4조 (책임의 한계)\n\n"
    "본 소프트웨어는 중립적 기술 도구로 제공됩니다.\n"
    "사용자의 위법 또는 약관 위반 행위로 인해 발생하는 모든 법적 책임은 해당 사용자에게 귀속됩니다.\n"
    "개발자는 사용자의 콘텐츠 이용 방식에 대해 사전 통제하거나 개별적으로 검증하지 않습니다.\n"
    "단, 관련 법령에 의해 제한되는 경우를 제외하고, 개발자는 사용자의 위법 행위로 인한 손해에 대해 책임을 부담하지 않습니다.\n\n"
    "제5조 (금지 행위)\n\n"
    "다음 행위는 엄격히 금지됩니다:\n"
    "- DRM 또는 기술적 보호조치 우회 시도\n"
    "- 유료 구독 콘텐츠의 무단 저장\n"
    "- 접근 통제 장치(로그인·인증 등) 우회\n"
    "- 대량 자동화 다운로드로 서비스 운영에 영향을 주는 행위\n"
    "- 다운로드 콘텐츠의 재배포 또는 상업적 이용\n\n"
    "제6조 (정책 변경 및 준거법)\n\n"
    "본 고지는 관련 법령 및 운영 정책에 따라 변경될 수 있습니다.\n"
    "본 소프트웨어의 이용과 관련된 분쟁은 적용 가능한 관할 법령에 따릅니다."
)

APP_STYLESHEET = """
QMainWindow {
    background: #EEF4FF;
}
QTabWidget::pane {
    border: 1px solid #D6E2F4;
    border-radius: 16px;
    background: #FFFFFF;
}
QTabBar::tab {
    background: #DBEAFE;
    color: #1E3A8A;
    border: 1px solid #BFDBFE;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
    padding: 13px 20px;
    margin-right: 4px;
    min-height: 24px;
    font-weight: 600;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    border-bottom-color: #FFFFFF;
}
QGroupBox {
    border: 1px solid #DDE7F5;
    border-radius: 14px;
    margin-top: 14px;
    padding: 14px;
    background: #FFFFFF;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #1E3A8A;
}
QLineEdit, QComboBox, QTextEdit {
    border: 1px solid #C8D8F0;
    border-radius: 12px;
    padding: 8px 10px;
    background: #FCFDFF;
    selection-background-color: #60A5FA;
}
QComboBox {
    padding-right: 36px;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid #C8D8F0;
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
    background: #EEF4FF;
}
QComboBox::down-arrow {
    __COMBO_ARROW_RULE__
    width: 12px;
    height: 12px;
}
QComboBox::down-arrow:on {
    top: 1px;
}
QLineEdit#urlInput {
    border: 2px solid #2563EB;
    border-radius: 16px;
    padding: 18px 20px;
    background: #FFFFFF;
    font-size: 18px;
    font-weight: 600;
}
QLineEdit#urlInput:focus {
    border: 2px solid #1D4ED8;
    background: #F8FBFF;
}
QPushButton {
    background: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
}
QPushButton:hover {
    background: #1D4ED8;
}
QPushButton:pressed {
    background: #1E40AF;
}
QPushButton:disabled {
    background: #9AB7F1;
    color: #E5ECFB;
}
QPushButton#donateCornerButton {
    background: #FFDD00;
    color: #000000;
    border: 1px solid #000000;
    border-radius: 12px;
    padding: 7px 16px;
    font-family: "Cookie", "Segoe UI";
    font-size: 16px;
    font-weight: 700;
}
QPushButton#donateCornerButton:hover {
    background: #FFE95C;
}
QPushButton#donateCornerButton:pressed {
    background: #E6C300;
}
QCheckBox {
    color: #0F172A;
}
QFrame#historyCard {
    border: 1px solid #D8E5F8;
    border-radius: 14px;
    background: #FFFFFF;
}
QFrame#historyCard:hover {
    border-color: #93C5FD;
    background: #F8FBFF;
}
QLabel#historyTitle {
    color: #0F172A;
    font-size: 24px;
    font-weight: 700;
}
QLabel#historyMeta {
    color: #334155;
    font-size: 20px;
}
QLabel#historyUrl {
    color: #1D4ED8;
    font-size: 20px;
}
QPushButton#historyCardButton {
    padding: 6px 10px;
    border-radius: 10px;
    font-size: 20px;
}
"""


def build_app_stylesheet(app_dir: Path) -> str:
    arrow_file = find_asset_file(app_dir, "combobox_arrow.svg")
    if arrow_file is None:
        arrow_rule = "image: none;"
    else:
        arrow_path = str(arrow_file).replace("\\", "/")
        arrow_rule = f'image: url("{arrow_path}");'
    return APP_STYLESHEET.replace("__COMBO_ARROW_RULE__", arrow_rule)


def resolve_app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resolve_user_data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return base / APP_DIR_NAME


def resolve_default_download_dir() -> Path:
    downloads = Path.home() / "Downloads"
    if downloads.exists():
        return downloads / APP_DIR_NAME
    return resolve_user_data_dir() / "downloads"


def get_runtime_search_roots(app_dir: Path) -> list[Path]:
    roots: list[Path] = [app_dir, app_dir / "_internal"]
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        roots.insert(0, Path(meipass))
    return roots


def find_ffmpeg_executable(app_dir: Path) -> Path | None:
    names = ["ffmpeg.exe", "ffmpeg"] if sys.platform.startswith("win") else ["ffmpeg"]
    for root in get_runtime_search_roots(app_dir):
        for name in names:
            candidate = root / "bin" / name
            if candidate.exists():
                return candidate.resolve()
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def find_ytdlp_executable(app_dir: Path) -> Path | None:
    names = ["yt-dlp.exe", "yt-dlp"] if sys.platform.startswith("win") else ["yt-dlp"]
    for root in get_runtime_search_roots(app_dir):
        for name in names:
            candidate = root / "bin" / name
            if candidate.exists():
                return candidate.resolve()
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def find_aria2c_executable(app_dir: Path) -> Path | None:
    names = ["aria2c.exe", "aria2c"] if sys.platform.startswith("win") else ["aria2c"]
    for root in get_runtime_search_roots(app_dir):
        for name in names:
            candidate = root / "bin" / name
            if candidate.exists():
                return candidate.resolve()
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def find_asset_file(app_dir: Path, name: str) -> Path | None:
    for root in get_runtime_search_roots(app_dir):
        candidate = root / "assets" / name
        if candidate.exists():
            return candidate.resolve()
    candidate = app_dir / "assets" / name
    if candidate.exists():
        return candidate.resolve()
    return None


def get_subprocess_no_window_kwargs() -> dict[str, Any]:
    if not sys.platform.startswith("win"):
        return {}

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    return {
        "startupinfo": startupinfo,
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
    }


def fetch_video_metadata_for_url(url: str, ytdlp_path: Path | None) -> dict[str, Any]:
    if yt_dlp is not None:
        try:
            opts = {
                "skip_download": True,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "ignoreconfig": True,
                "cookiefile": None,
                "cookiesfrombrowser": None,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
            if isinstance(info, dict) and info.get("entries"):
                entries = info.get("entries") or []
                first = entries[0] if entries else {}
                return first if isinstance(first, dict) else {}
            return info if isinstance(info, dict) else {}
        except Exception:
            pass

    if ytdlp_path is None:
        return {}

    command = [
        str(ytdlp_path),
        "--ignore-config",
        "--skip-download",
        "--dump-single-json",
        "--no-playlist",
        "--no-warnings",
        url,
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
            **get_subprocess_no_window_kwargs(),
        )
        if result.returncode != 0:
            return {}
        for line in reversed(result.stdout.splitlines()):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                payload = json.loads(line)
                if isinstance(payload, dict):
                    return payload
                return {}
    except Exception:
        return {}
    return {}


def download_thumbnail_to_file(thumbnail_url: str, target: Path) -> str:
    if not thumbnail_url:
        return ""
    try:
        request = urllib.request.Request(
            thumbnail_url,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            data = response.read()
        if not data:
            return ""
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return str(target)
    except Exception:
        return ""


def create_fallback_header_logo(width: int = 56, height: int = 56) -> QPixmap:
    size = min(width, height)
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0, QColor("#4FC3F7"))
    gradient.setColorAt(1, QColor("#1D4ED8"))
    painter.setBrush(gradient)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, size, size, size * 0.22, size * 0.22)

    play_path = QPainterPath()
    play_path.moveTo(size * 0.38, size * 0.28)
    play_path.lineTo(size * 0.74, size * 0.5)
    play_path.lineTo(size * 0.38, size * 0.72)
    play_path.closeSubpath()

    painter.setBrush(QColor("#FFFFFF"))
    painter.drawPath(play_path)
    painter.end()
    return pixmap


def load_pixmap_with_fallback(
    app_dir: Path,
    asset_name: str,
    width: int,
    height: int,
    fallback_factory,
) -> QPixmap:
    asset_path = find_asset_file(app_dir, asset_name)
    if asset_path is not None:
        icon = QIcon(str(asset_path))
        pixmap = icon.pixmap(width, height)
        if not pixmap.isNull():
            return pixmap
    return fallback_factory(width, height) if fallback_factory else QPixmap()


def load_app_icon(app_dir: Path) -> QIcon:
    for asset_name in ("app_icon.ico", "header_icon.svg"):
        asset_path = find_asset_file(app_dir, asset_name)
        if asset_path is None:
            continue
        icon = QIcon(str(asset_path))
        if not icon.isNull():
            return icon

    fallback = create_fallback_header_logo(64, 64)
    return QIcon(fallback)


def create_fallback_thumbnail(width: int = 168, height: int = 94) -> QPixmap:
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#EAF2FF"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QColor("#C8D8F2"))
    painter.setBrush(QColor("#EAF2FF"))
    painter.drawRoundedRect(0, 0, width - 1, height - 1, 12, 12)

    icon = create_fallback_header_logo(34, 34)
    icon_x = (width - icon.width()) // 2
    icon_y = (height - icon.height()) // 2 - 8
    painter.drawPixmap(icon_x, icon_y, icon)

    painter.setPen(QColor("#3B82F6"))
    painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
    painter.drawText(0, height - 24, width, 20, Qt.AlignCenter, "No Thumbnail")
    painter.end()
    return pixmap


def format_duration(duration_seconds: int | None) -> str:
    if not duration_seconds or duration_seconds < 0:
        return "-"
    hours, rem = divmod(int(duration_seconds), 3600)
    minutes, seconds = divmod(rem, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def install_safe_exception_handler(log_dir: Path) -> None:
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    error_log = log_dir / "error.log"

    def _handler(exc_type, exc_value, exc_traceback) -> None:
        try:
            with error_log.open("a", encoding="utf-8") as handle:
                handle.write("\n===== Unhandled Exception =====\n")
                traceback.print_exception(exc_type, exc_value, exc_traceback, file=handle)
        except Exception:
            pass
        QMessageBox.critical(
            None,
            "오류",
            f"예기치 못한 오류가 발생했습니다.\n자세한 내용은 로그를 확인하세요:\n{error_log}",
        )

    sys.excepthook = _handler


@dataclass
class AppSettings:
    save_path: str
    download_mode: str
    default_video_quality: str
    default_audio_quality: str
    default_audio_format: str

    @classmethod
    def create_default(cls) -> "AppSettings":
        return cls(
            save_path=str(resolve_default_download_dir()),
            download_mode=MODE_VIDEO,
            default_video_quality=VIDEO_QUALITY_OPTIONS[0],
            default_audio_quality=AUDIO_QUALITY_OPTIONS[0],
            default_audio_format=AUDIO_FORMAT_OPTIONS[0],
        )


class SettingsStore:
    def __init__(self, user_data_dir: Path, legacy_file_path: Path | None = None):
        self.user_data_dir = user_data_dir
        self.legacy_file_path = legacy_file_path
        try:
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            fallback_dir = Path.home() / f".{APP_DIR_NAME.lower()}"
            fallback_dir.mkdir(parents=True, exist_ok=True)
            self.user_data_dir = fallback_dir
        self.file_path = self.user_data_dir / "settings.json"

    def load(self) -> AppSettings:
        default = AppSettings.create_default()
        source_file = self.file_path
        if not source_file.exists() and self.legacy_file_path and self.legacy_file_path.exists():
            source_file = self.legacy_file_path

        if not source_file.exists():
            return default

        try:
            data = json.loads(source_file.read_text(encoding="utf-8"))
        except Exception:
            return default

        save_path = str(data.get("save_path", default.save_path))
        download_mode = data.get("download_mode", default.download_mode)
        video = data.get("default_video_quality", default.default_video_quality)
        audio = data.get("default_audio_quality", default.default_audio_quality)
        audio_format = data.get("default_audio_format", default.default_audio_format)

        if download_mode not in (MODE_VIDEO, MODE_AUDIO_ONLY):
            download_mode = default.download_mode
        if video not in VIDEO_QUALITY_OPTIONS:
            video = default.default_video_quality
        if audio not in AUDIO_QUALITY_OPTIONS:
            audio = default.default_audio_quality
        if audio_format not in AUDIO_FORMAT_OPTIONS:
            audio_format = default.default_audio_format

        return AppSettings(
            save_path=save_path,
            download_mode=download_mode,
            default_video_quality=video,
            default_audio_quality=audio,
            default_audio_format=audio_format,
        )

    def save(self, settings: AppSettings) -> None:
        self.file_path.write_text(
            json.dumps(asdict(settings), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


@dataclass
class DownloadHistoryRecord:
    record_id: str
    url: str
    title: str
    thumbnail_path: str
    duration_seconds: int | None
    requested_at: str
    status: str
    output_path: str = ""


class HistoryStore:
    def __init__(self, user_data_dir: Path):
        self.user_data_dir = user_data_dir
        self.file_path = self.user_data_dir / "history.json"
        self.thumbnail_dir = self.user_data_dir / "history_thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[DownloadHistoryRecord]:
        if not self.file_path.exists():
            return []
        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except Exception:
            return []
        if not isinstance(raw, list):
            return []

        records: list[DownloadHistoryRecord] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            duration = item.get("duration_seconds")
            if not isinstance(duration, int):
                duration = None
            records.append(
                DownloadHistoryRecord(
                    record_id=str(item.get("record_id", "")) or uuid.uuid4().hex,
                    url=str(item.get("url", "")),
                    title=str(item.get("title", "")) or "제목 정보 없음",
                    thumbnail_path=str(item.get("thumbnail_path", "")),
                    duration_seconds=duration,
                    requested_at=str(item.get("requested_at", "")),
                    status=str(item.get("status", "")) or HISTORY_STATUS_PENDING,
                    output_path=str(item.get("output_path", "")),
                )
            )
        return records

    def save(self, records: list[DownloadHistoryRecord]) -> None:
        payload = [asdict(record) for record in records]
        self.file_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def make_thumbnail_path(self, record_id: str, extension: str = ".jpg") -> Path:
        ext = extension if extension.startswith(".") else f".{extension}"
        return self.thumbnail_dir / f"{record_id}{ext}"


class QtYdlLogger:
    def __init__(self, callback):
        self.callback = callback

    def debug(self, msg: str) -> None:
        if msg and (
            "[download]" in msg
            or "[Merger]" in msg
            or "[ExtractAudio]" in msg
            or "[ffmpeg]" in msg
        ):
            self.callback(msg)

    def warning(self, msg: str) -> None:
        if msg:
            self.callback(f"[경고] {msg}")

    def error(self, msg: str) -> None:
        if msg:
            self.callback(f"[오류] {msg}")


class DownloadWorker(QThread):
    progress = Signal(float, str)
    log = Signal(str)
    success = Signal(str)
    failed = Signal(str)

    def __init__(
        self,
        url: str,
        ydl_opts: dict,
        output_path: str,
        ytdlp_path: Path | None,
        aria2c_path: Path | None,
    ):
        super().__init__()
        self.url = url
        self.ydl_opts = ydl_opts
        self.output_path = output_path
        self.ytdlp_path = ytdlp_path
        self.aria2c_path = aria2c_path

    def _emit_progress(self, data: dict) -> None:
        status = data.get("status")
        if status == "downloading":
            percent = self._get_percent(data)
            speed = data.get("_speed_str") or "-"
            eta = data.get("_eta_str") or "-"
            filename = Path(data.get("filename", "")).name
            message = f"{percent:.1f}% | 속도: {speed} | ETA: {eta}"
            if filename:
                message += f" | 파일: {filename}"
            self.progress.emit(max(0.0, min(percent, 100.0)), message)
        elif status == "finished":
            self.progress.emit(100.0, "다운로드 완료, 후처리 중...")

    @staticmethod
    def _get_percent(data: dict) -> float:
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        downloaded = data.get("downloaded_bytes")
        if total and downloaded is not None:
            return (float(downloaded) / float(total)) * 100.0

        raw_percent = data.get("_percent_str", "")
        matched = re.search(r"(\d+(?:\.\d+)?)%", raw_percent)
        if matched:
            return float(matched.group(1))
        return 0.0

    def run(self) -> None:
        if self.ytdlp_path:
            self._run_with_cli()
            return

        if yt_dlp is None:
            self.failed.emit("yt-dlp를 찾지 못했습니다. bin/yt-dlp.exe를 포함하세요.")
            return

        try:
            options = dict(self.ydl_opts)
            options["logger"] = QtYdlLogger(self.log.emit)
            options["progress_hooks"] = [self._emit_progress]
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([self.url])
            self.success.emit(self.output_path)
        except Exception as exc:
            self.failed.emit(str(exc))

    def _run_with_cli(self) -> None:
        process: subprocess.Popen | None = None
        try:
            command = [
                str(self.ytdlp_path),
                "--ignore-config",
                "--no-playlist",
                "--newline",
                "--progress",
                "--no-warnings",
                "-f",
                str(self.ydl_opts["format"]),
                "-o",
                str(self.ydl_opts["outtmpl"]),
            ]
            if self.ydl_opts.get("windowsfilenames"):
                command.append("--windows-filenames")
            if self.ydl_opts.get("continuedl"):
                command.append("--continue")
            if self.ydl_opts.get("retries") is not None:
                command.extend(["--retries", str(self.ydl_opts["retries"])])
            if self.ydl_opts.get("extractor_retries") is not None:
                command.extend(
                    ["--extractor-retries", str(self.ydl_opts["extractor_retries"])]
                )
            if self.ydl_opts.get("fragment_retries") is not None:
                command.extend(
                    ["--fragment-retries", str(self.ydl_opts["fragment_retries"])]
                )
            if self.ydl_opts.get("concurrent_fragment_downloads") is not None:
                command.extend(
                    [
                        "--concurrent-fragments",
                        str(self.ydl_opts["concurrent_fragment_downloads"]),
                    ]
                )
            if self.ydl_opts.get("socket_timeout") is not None:
                command.extend(["--socket-timeout", str(self.ydl_opts["socket_timeout"])])
            if self.ydl_opts.get("check_formats") is False:
                command.append("--no-check-formats")
            if self.aria2c_path is not None:
                command.extend(
                    [
                        "--downloader",
                        str(self.aria2c_path),
                        "--downloader-args",
                        "aria2c:-x16 -s16 -k1M --summary-interval=0 --console-log-level=warn",
                    ]
                )
            if self.ydl_opts.get("merge_output_format"):
                command.extend(
                    ["--merge-output-format", str(self.ydl_opts["merge_output_format"])]
                )
            if self.ydl_opts.get("ffmpeg_location"):
                command.extend(
                    ["--ffmpeg-location", str(self.ydl_opts["ffmpeg_location"])]
                )

            postprocessors = self.ydl_opts.get("postprocessors") or []
            for processor in postprocessors:
                if processor.get("key") == "FFmpegExtractAudio":
                    command.extend(
                        [
                            "-x",
                            "--audio-format",
                            str(processor.get("preferredcodec", "mp3")),
                            "--audio-quality",
                            str(processor.get("preferredquality", "0")),
                        ]
                    )
                    break

            command.append(self.url)
            self.log.emit("[정보] yt-dlp CLI 모드로 다운로드를 시작합니다.")
            if self.aria2c_path is not None:
                self.log.emit("[정보] 빠른 모드 적용: aria2c 외부 다운로더 + 병렬 조각 다운로드 + 포맷 점검 비활성화")
            else:
                self.log.emit("[정보] 빠른 모드 적용: 병렬 조각 다운로드 + 포맷 점검 비활성화")

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                **get_subprocess_no_window_kwargs(),
            )

            if process.stdout is None:
                raise RuntimeError("yt-dlp 출력 스트림을 읽을 수 없습니다.")

            last_line = ""
            for raw_line in process.stdout:
                line = raw_line.strip()
                if not line:
                    continue
                last_line = line
                self.log.emit(line)

                lowered = line.lower()
                if "drm" in lowered and any(
                    keyword in lowered
                    for keyword in ("protected", "unsupported", "not supported", "license")
                ):
                    process.kill()
                    try:
                        process.wait(timeout=2)
                    except Exception:
                        pass
                    raise RuntimeError("DRM 보호 신호가 감지되어 다운로드를 차단했습니다.")

                matched = re.search(r"(\d+(?:\.\d+)?)%", line)
                if matched:
                    percent = float(matched.group(1))
                    self.progress.emit(max(0.0, min(percent, 100.0)), line)

            return_code = process.wait()
            if return_code != 0:
                raise RuntimeError(last_line or f"yt-dlp 실행 실패 (코드 {return_code})")

            self.progress.emit(100.0, "다운로드 완료")
            self.success.emit(self.output_path)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            if process is not None and process.stdout is not None:
                try:
                    process.stdout.close()
                except Exception:
                    pass


class MetadataFetchWorker(QThread):
    resolved = Signal(str, object, str)
    failed = Signal(str, str)

    def __init__(
        self,
        record_id: str,
        url: str,
        ytdlp_path: Path | None,
        thumbnail_dir: Path,
    ):
        super().__init__()
        self.record_id = record_id
        self.url = url
        self.ytdlp_path = ytdlp_path
        self.thumbnail_dir = thumbnail_dir

    def run(self) -> None:
        try:
            metadata = fetch_video_metadata_for_url(self.url, self.ytdlp_path)
            if not isinstance(metadata, dict):
                metadata = {}

            thumbnail_path = ""
            thumb_url = str(metadata.get("thumbnail", "")).strip()
            if thumb_url:
                ext = Path(QUrl(thumb_url).path()).suffix.lower()
                if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                    ext = ".jpg"
                target = self.thumbnail_dir / f"{self.record_id}{ext}"
                thumbnail_path = download_thumbnail_to_file(thumb_url, target)

            self.resolved.emit(self.record_id, metadata, thumbnail_path)
        except Exception as exc:
            self.failed.emit(self.record_id, str(exc))


class LegalConsentDialog(QDialog):
    def __init__(self, app_icon: QIcon | None = None) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - 법적 고지 동의")
        if app_icon is not None and not app_icon.isNull():
            self.setWindowIcon(app_icon)
        self.resize(1020, 820)
        self.setModal(True)
        self.setStyleSheet(
            """
QDialog {
    background: #F5F9FF;
}
QTextEdit#legalNoticeView {
    border: 1px solid #C7D8F3;
    border-radius: 12px;
    background: #FFFFFF;
    padding: 8px;
}
QCheckBox#legalAgreeCheck {
    color: #0F172A;
    font-size: 18px;
    font-weight: 600;
}
QPushButton#legalDeclineBtn {
    background: #E2E8F0;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
    min-width: 150px;
    min-height: 42px;
}
QPushButton#legalDeclineBtn:hover {
    background: #CBD5E1;
}
QPushButton#legalDeclineBtn:pressed {
    background: #94A3B8;
    color: #0F172A;
}
QPushButton#legalAcceptBtn {
    background: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 10px 14px;
    font-weight: 700;
    min-width: 150px;
    min-height: 42px;
}
QPushButton#legalAcceptBtn:hover {
    background: #1D4ED8;
}
QPushButton#legalAcceptBtn:pressed {
    background: #1E40AF;
}
QPushButton#legalAcceptBtn:disabled {
    background: #9AB7F1;
    color: #E5ECFB;
}
"""
        )
        self._notice_fully_read = False

        layout = QVBoxLayout(self)

        title = QLabel("아래 내용을 읽고 동의해야 프로그램을 사용할 수 있습니다.")
        title_font = QFont("Segoe UI", 18, QFont.Bold)
        title.setFont(title_font)
        title.setWordWrap(True)
        layout.addWidget(title)

        subtitle = QLabel("미동의 시 프로그램 사용이 불가하며 즉시 종료됩니다.")
        subtitle.setFont(QFont("Segoe UI", 18))
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.notice_view = QTextEdit()
        self.notice_view.setReadOnly(True)
        self.notice_view.setObjectName("legalNoticeView")
        self.notice_view.setHtml(self._build_notice_html(LEGAL_NOTICE_TEXT))
        self.notice_view.verticalScrollBar().valueChanged.connect(self._on_notice_scroll)
        layout.addWidget(self.notice_view)

        self.scroll_hint_label = QLabel("안내문을 끝까지 스크롤하면 동의 체크박스가 표시됩니다.")
        self.scroll_hint_label.setStyleSheet("color:#1E3A8A; font-size:16px; font-weight:600;")
        self.scroll_hint_label.setWordWrap(True)
        layout.addWidget(self.scroll_hint_label)

        self.agree_checkbox = QCheckBox("위 내용을 확인했고, 모든 조건에 동의합니다.")
        self.agree_checkbox.setObjectName("legalAgreeCheck")
        self.agree_checkbox.setVisible(False)
        self.agree_checkbox.stateChanged.connect(self._update_buttons)
        layout.addWidget(self.agree_checkbox)

        button_row = QHBoxLayout()
        self.btn_decline = QPushButton("미동의 (종료)")
        self.btn_decline.setObjectName("legalDeclineBtn")
        self.btn_decline.clicked.connect(self.reject)
        self.btn_accept = QPushButton("동의하고 시작")
        self.btn_accept.setObjectName("legalAcceptBtn")
        self.btn_accept.setEnabled(False)
        self.btn_accept.clicked.connect(self._accept_if_checked)
        button_row.addStretch(1)
        button_row.addWidget(self.btn_decline)
        button_row.addWidget(self.btn_accept)
        layout.addLayout(button_row)
        QTimer.singleShot(0, self._initialize_scroll_gate)

    def _update_buttons(self) -> None:
        self.btn_accept.setEnabled(self.agree_checkbox.isChecked())

    def _accept_if_checked(self) -> None:
        if self.agree_checkbox.isChecked():
            self.accept()

    def _initialize_scroll_gate(self) -> None:
        self._on_notice_scroll(self.notice_view.verticalScrollBar().value())

    def _on_notice_scroll(self, value: int) -> None:
        if self._notice_fully_read:
            return
        bar = self.notice_view.verticalScrollBar()
        if bar.maximum() <= 0 or value >= bar.maximum():
            self._notice_fully_read = True
            self.scroll_hint_label.setVisible(False)
            self.agree_checkbox.setVisible(True)

    @staticmethod
    def _build_notice_html(raw_text: str) -> str:
        heading_pattern = re.compile(r"^(제\d+조\s*\(.*\))$")
        parts = [
            "<html><body style='font-family:\"Segoe UI\"; font-size:18px; line-height:1.66; color:#0F172A;'>"
        ]
        for raw_line in raw_text.splitlines():
            line = raw_line.strip()
            if not line:
                parts.append("<div style='height:8px;'></div>")
                continue

            if heading_pattern.match(line):
                parts.append(
                    "<hr style='border:none; border-top:1px solid #D8E4F6; margin:12px 0 8px 0;'>"
                )
                parts.append(
                    f"<div style='font-size:18px; font-weight:700; color:#1E3A8A;'>{html.escape(line)}</div>"
                )
                continue

            if line.startswith("- "):
                parts.append(f"<div style='margin-left:8px;'>• {html.escape(line[2:])}</div>")
                continue

            parts.append(f"<div>{html.escape(line)}</div>")

        parts.append("</body></html>")
        return "".join(parts)


class HistoryCard(QFrame):
    selected = Signal(str)
    delete_requested = Signal(str)
    open_url_requested = Signal(str)

    def __init__(self, record: DownloadHistoryRecord):
        super().__init__()
        self.record = record
        self.setObjectName("historyCard")
        self.setCursor(Qt.PointingHandCursor)

        row = QHBoxLayout(self)
        row.setContentsMargins(12, 12, 12, 12)
        row.setSpacing(12)

        thumb_label = QLabel()
        thumb_label.setFixedSize(168, 94)
        thumb_label.setScaledContents(True)
        thumb = QPixmap(record.thumbnail_path) if record.thumbnail_path else QPixmap()
        if thumb.isNull():
            thumb = create_fallback_thumbnail(168, 94)
        else:
            thumb = thumb.scaled(168, 94, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        thumb_label.setPixmap(thumb)
        row.addWidget(thumb_label)

        content_col = QVBoxLayout()
        content_col.setSpacing(4)

        title = QLabel(record.title)
        title.setObjectName("historyTitle")
        title.setWordWrap(True)
        content_col.addWidget(title)

        url = QLabel(record.url)
        url.setObjectName("historyUrl")
        url.setWordWrap(True)
        content_col.addWidget(url)

        meta = QLabel(
            f"상태: {record.status}  |  길이: {format_duration(record.duration_seconds)}  |  요청: {record.requested_at}"
        )
        meta.setObjectName("historyMeta")
        meta.setWordWrap(True)
        content_col.addWidget(meta)

        btn_open = QPushButton("URL 열기")
        btn_open.setObjectName("historyCardButton")
        btn_open.clicked.connect(lambda: self.open_url_requested.emit(self.record.url))

        btn_delete = QPushButton("삭제")
        btn_delete.setObjectName("historyCardButton")
        btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.record.record_id))
        row.addLayout(content_col, 1)

        action_col = QVBoxLayout()
        action_col.setSpacing(10)
        action_col.addWidget(btn_open)
        action_col.addWidget(btn_delete)
        action_col.addStretch(1)
        row.addLayout(action_col)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.selected.emit(self.record.record_id)
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self, app_icon: QIcon | None = None) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(APP_WINDOW_WIDTH, APP_WINDOW_HEIGHT)
        self.setMinimumWidth(APP_WINDOW_WIDTH)
        self.setMaximumWidth(APP_WINDOW_WIDTH)

        self.app_dir = resolve_app_dir()
        self.user_data_dir = resolve_user_data_dir()
        self.setStyleSheet(build_app_stylesheet(self.app_dir))
        self.app_icon = app_icon if app_icon is not None else load_app_icon(self.app_dir)
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        self.settings_store = SettingsStore(
            self.user_data_dir,
            legacy_file_path=self.app_dir / "settings.json",
        )
        self.settings = self.settings_store.load()
        self._ensure_safe_startup_paths()
        self.history_store = HistoryStore(self.user_data_dir)
        self.history_records = self.history_store.load()
        self.active_history_record_id: str | None = None

        self.ytdlp_path = find_ytdlp_executable(self.app_dir)
        self.ytdlp_available = self.ytdlp_path is not None or yt_dlp is not None
        self.aria2c_path = find_aria2c_executable(self.app_dir)
        self.aria2c_available = self.aria2c_path is not None
        self.ffmpeg_path = find_ffmpeg_executable(self.app_dir)
        self.ffmpeg_available = self.ffmpeg_path is not None
        self.download_worker: DownloadWorker | None = None
        self.metadata_workers: list[MetadataFetchWorker] = []

        self._init_ui()
        self._load_settings_to_form()

    def _init_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        self.tabs = QTabWidget()
        self.tab_download = QWidget()
        self.tab_settings = QWidget()
        self.tab_history = QWidget()
        self.tabs.addTab(self.tab_download, "다운로드")
        self.tabs.addTab(self.tab_settings, "설정")
        self.tabs.addTab(self.tab_history, "기록")

        self.btn_donate_corner = QPushButton("☕ Buy me a coffee")
        self.btn_donate_corner.setObjectName("donateCornerButton")
        self.btn_donate_corner.setCursor(Qt.PointingHandCursor)
        self.btn_donate_corner.setFixedHeight(40)
        self.btn_donate_corner.clicked.connect(self.open_buy_me_a_coffee)
        donate_corner_wrap = QWidget()
        donate_corner_layout = QHBoxLayout(donate_corner_wrap)
        donate_corner_layout.setContentsMargins(0, 6, 8, 8)
        donate_corner_layout.addWidget(self.btn_donate_corner)
        self.tabs.setCornerWidget(donate_corner_wrap, Qt.TopRightCorner)

        root_layout.addWidget(self.tabs)
        self.setCentralWidget(root)

        self._build_download_tab()
        self._build_settings_tab()
        self._build_history_tab()
        self._render_history_records()

    def _build_download_tab(self) -> None:
        layout = QVBoxLayout(self.tab_download)
        layout.setContentsMargins(14, 18, 14, 12)
        layout.setSpacing(10)

        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("URL 입력")
        self.url_input.setMinimumHeight(72)
        url_row.addWidget(self.url_input)
        layout.addLayout(url_row)

        button_row = QHBoxLayout()
        self.btn_download = QPushButton("다운로드 시작")
        self.btn_download.clicked.connect(self.start_download)
        self.btn_open_folder = QPushButton("저장 폴더 열기")
        self.btn_open_folder.clicked.connect(self.open_download_folder)
        button_row.addWidget(self.btn_download)
        button_row.addWidget(self.btn_open_folder)
        layout.addLayout(button_row)

        self.status_label = QLabel("대기 중")
        layout.addWidget(self.status_label)

        log_group = QGroupBox("로그")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.document().setMaximumBlockCount(1500)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)

    def _build_settings_tab(self) -> None:
        layout = QVBoxLayout(self.tab_settings)
        layout.setContentsMargins(14, 18, 14, 12)

        form_group = QGroupBox("기본 설정")
        form_layout = QFormLayout(form_group)

        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.btn_browse = QPushButton("경로 선택")
        self.btn_browse.clicked.connect(self.choose_download_dir)
        path_row.addWidget(self.path_input)
        path_row.addWidget(self.btn_browse)

        self.default_video_combo = QComboBox()
        self.default_video_combo.addItems(VIDEO_QUALITY_OPTIONS)
        self.default_audio_combo = QComboBox()
        self.default_audio_combo.addItems(AUDIO_QUALITY_OPTIONS)
        self.default_audio_format_combo = QComboBox()
        self.default_audio_format_combo.addItems(AUDIO_FORMAT_OPTIONS)
        self.default_mode_combo = QComboBox()
        self.default_mode_combo.addItems([MODE_VIDEO, MODE_AUDIO_ONLY])

        form_layout.addRow("저장 경로", path_row)
        form_layout.addRow("다운로드 모드", self.default_mode_combo)
        form_layout.addRow("기본 화질", self.default_video_combo)
        form_layout.addRow("기본 오디오 품질", self.default_audio_combo)
        form_layout.addRow("기본 오디오 포맷", self.default_audio_format_combo)

        self.btn_save_settings = QPushButton("설정 저장")
        self.btn_save_settings.clicked.connect(self.save_settings)
        form_layout.addRow(self.btn_save_settings)

        layout.addWidget(form_group)
        layout.addStretch(1)

    def _build_history_tab(self) -> None:
        layout = QVBoxLayout(self.tab_history)
        layout.setContentsMargins(14, 18, 14, 12)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        self.history_summary_label = QLabel("기록 0건")
        summary_font = QFont("Segoe UI", 18, QFont.Bold)
        self.history_summary_label.setFont(summary_font)
        top_row.addWidget(self.history_summary_label)
        top_row.addStretch(1)

        self.btn_clear_history = QPushButton("전체 삭제")
        self.btn_clear_history.clicked.connect(self.clear_history_records)
        top_row.addWidget(self.btn_clear_history)
        layout.addLayout(top_row)

        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setFrameShape(QFrame.NoFrame)

        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        self.history_layout.setSpacing(10)
        self.history_scroll.setWidget(self.history_content)
        layout.addWidget(self.history_scroll)

    def _clear_history_layout_widgets(self) -> None:
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render_history_records(self) -> None:
        self._clear_history_layout_widgets()

        total = len(self.history_records)
        self.history_summary_label.setText(f"기록 {total}건")
        self.btn_clear_history.setEnabled(total > 0)

        if total == 0:
            empty_label = QLabel("다운로드 기록이 없습니다.")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color:#64748B; padding:28px;")
            self.history_layout.addWidget(empty_label)
            self.history_layout.addStretch(1)
            return

        for record in self.history_records:
            card = HistoryCard(record)
            card.selected.connect(self._on_history_card_selected)
            card.open_url_requested.connect(self._open_external_url)
            card.delete_requested.connect(self.delete_history_record)
            self.history_layout.addWidget(card)
        self.history_layout.addStretch(1)

    def _save_history_records(self) -> None:
        try:
            self.history_store.save(self.history_records)
        except Exception as exc:
            self.log_text.append(f"[경고] 기록 저장 실패: {exc}")

    def _find_record_by_id(self, record_id: str) -> DownloadHistoryRecord | None:
        for record in self.history_records:
            if record.record_id == record_id:
                return record
        return None

    def _download_thumbnail(self, thumbnail_url: str, record_id: str) -> str:
        if not thumbnail_url:
            return ""
        ext = Path(QUrl(thumbnail_url).path()).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        target = self.history_store.make_thumbnail_path(record_id, ext)
        try:
            request = urllib.request.Request(
                thumbnail_url,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(request, timeout=8) as response:
                data = response.read()
            if not data:
                return ""
            target.write_bytes(data)
            return str(target)
        except Exception:
            return ""

    def _fetch_video_metadata(self, url: str) -> dict[str, Any]:
        return fetch_video_metadata_for_url(url, self.ytdlp_path)

    def _append_history_record(self, url: str, metadata: dict[str, Any]) -> str:
        record_id = uuid.uuid4().hex
        duration = metadata.get("duration") if metadata else None
        if not isinstance(duration, int):
            duration = None

        title = str(metadata.get("title", "")).strip() if metadata else ""
        if not title:
            title = "제목 정보 없음"

        record = DownloadHistoryRecord(
            record_id=record_id,
            url=url,
            title=title,
            thumbnail_path="",
            duration_seconds=duration,
            requested_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status=HISTORY_STATUS_PENDING,
        )
        self.history_records.insert(0, record)
        self.history_records = self.history_records[:300]
        self._save_history_records()
        self._render_history_records()
        return record_id

    def _update_history_record(
        self,
        record_id: str | None,
        status: str,
        output_path: str = "",
    ) -> None:
        if not record_id:
            return
        record = self._find_record_by_id(record_id)
        if record is None:
            return
        record.status = status
        if output_path:
            record.output_path = output_path
        self._save_history_records()
        self._render_history_records()

    def _apply_history_metadata(
        self,
        record_id: str,
        metadata: dict[str, Any],
        thumbnail_path: str,
    ) -> None:
        record = self._find_record_by_id(record_id)
        if record is None:
            return

        title = str(metadata.get("title", "")).strip() if metadata else ""
        if title:
            record.title = title

        duration = metadata.get("duration") if metadata else None
        if isinstance(duration, int):
            record.duration_seconds = duration

        if thumbnail_path:
            record.thumbnail_path = thumbnail_path

        self._save_history_records()
        self._render_history_records()

    def _start_metadata_fetch(self, record_id: str, url: str) -> None:
        worker = MetadataFetchWorker(
            record_id=record_id,
            url=url,
            ytdlp_path=self.ytdlp_path,
            thumbnail_dir=self.history_store.thumbnail_dir,
        )
        worker.resolved.connect(self._on_metadata_fetch_resolved)
        worker.failed.connect(self._on_metadata_fetch_failed)
        worker.finished.connect(lambda w=worker: self._on_metadata_worker_finished(w))
        self.metadata_workers.append(worker)
        worker.start()

    def _on_metadata_fetch_resolved(
        self,
        record_id: str,
        metadata: dict[str, Any],
        thumbnail_path: str,
    ) -> None:
        self._apply_history_metadata(record_id, metadata, thumbnail_path)

    def _on_metadata_fetch_failed(self, record_id: str, error_msg: str) -> None:
        self.log_text.append(f"[경고] 메타데이터 확인 실패(record={record_id}): {error_msg}")

    def _on_metadata_worker_finished(self, worker: MetadataFetchWorker) -> None:
        if worker in self.metadata_workers:
            self.metadata_workers.remove(worker)
        worker.deleteLater()

    def _on_history_card_selected(self, record_id: str) -> None:
        record = self._find_record_by_id(record_id)
        if record is None:
            return
        self.tabs.setCurrentWidget(self.tab_download)
        self.url_input.setText(record.url)
        self.url_input.setFocus()
        self.url_input.selectAll()
        self.status_label.setText("기록 URL이 입력되었습니다.")

    def _open_external_url(self, url: str) -> None:
        if not url:
            return
        QDesktopServices.openUrl(QUrl(url))

    def delete_history_record(self, record_id: str) -> None:
        index_to_remove = -1
        record_to_remove: DownloadHistoryRecord | None = None
        for index, record in enumerate(self.history_records):
            if record.record_id == record_id:
                index_to_remove = index
                record_to_remove = record
                break
        if index_to_remove < 0:
            return

        if record_to_remove and record_to_remove.thumbnail_path:
            thumb_file = Path(record_to_remove.thumbnail_path)
            if thumb_file.exists():
                try:
                    thumb_file.unlink()
                except Exception:
                    pass

        self.history_records.pop(index_to_remove)
        self._save_history_records()
        self._render_history_records()

    def clear_history_records(self) -> None:
        if not self.history_records:
            return
        answer = QMessageBox.question(
            self,
            "기록 삭제",
            "모든 다운로드 기록을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        for record in self.history_records:
            if record.thumbnail_path:
                thumb_file = Path(record.thumbnail_path)
                if thumb_file.exists():
                    try:
                        thumb_file.unlink()
                    except Exception:
                        pass

        self.history_records = []
        self._save_history_records()
        self._render_history_records()

    def _ensure_safe_startup_paths(self) -> None:
        default_download = resolve_default_download_dir()
        save_path_obj = Path(self.settings.save_path)
        try:
            self._ensure_download_dir(save_path_obj)
            return
        except Exception:
            pass

        try:
            self._ensure_download_dir(default_download)
            self.settings.save_path = str(default_download)
            try:
                self.settings_store.save(self.settings)
            except Exception:
                pass
        except Exception as exc:
            raise RuntimeError(
                "기본 저장 경로를 준비하지 못했습니다. 권한을 확인해 주세요."
            ) from exc

    def _load_settings_to_form(self) -> None:
        self.path_input.setText(self.settings.save_path)
        self.default_mode_combo.setCurrentText(self.settings.download_mode)
        self.default_video_combo.setCurrentText(self.settings.default_video_quality)
        self.default_audio_combo.setCurrentText(self.settings.default_audio_quality)
        self.default_audio_format_combo.setCurrentText(self.settings.default_audio_format)

    @staticmethod
    def _ensure_download_dir(path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def choose_download_dir(self) -> None:
        current = self.path_input.text().strip() or str(resolve_default_download_dir())
        selected = QFileDialog.getExistingDirectory(self, "저장 경로 선택", current)
        if selected:
            self.path_input.setText(selected)

    def open_download_folder(self) -> None:
        target = Path(self.settings.save_path)
        self._ensure_download_dir(target)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))

    def open_buy_me_a_coffee(self) -> None:
        QDesktopServices.openUrl(QUrl(BUY_ME_A_COFFEE_URL))

    def save_settings(self) -> None:
        save_path = self.path_input.text().strip() or str(resolve_default_download_dir())
        path_obj = Path(save_path)
        try:
            self._ensure_download_dir(path_obj)
        except Exception as exc:
            QMessageBox.critical(self, "오류", f"저장 경로를 생성할 수 없습니다.\n{exc}")
            return

        self.settings = AppSettings(
            save_path=str(path_obj),
            download_mode=self.default_mode_combo.currentText(),
            default_video_quality=self.default_video_combo.currentText(),
            default_audio_quality=self.default_audio_combo.currentText(),
            default_audio_format=self.default_audio_format_combo.currentText(),
        )
        try:
            self.settings_store.save(self.settings)
        except Exception as exc:
            QMessageBox.critical(self, "오류", f"설정을 저장하지 못했습니다.\n{exc}")
            return

        QMessageBox.information(self, "완료", "설정이 저장되었습니다.")

    def _build_ydl_options(self, output_dir: Path) -> dict:
        mode = self.settings.download_mode
        video_quality = self.settings.default_video_quality
        audio_quality = self.settings.default_audio_quality
        audio_format = self.settings.default_audio_format

        options = {
            "format": "best",
            "outtmpl": str(output_dir / "%(title).200B [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "retries": 10,
            "extractor_retries": 3,
            "fragment_retries": 10,
            "concurrent_fragment_downloads": 10,
            "socket_timeout": 20,
            "check_formats": False,
            "continuedl": True,
            "windowsfilenames": True,
            "ignoreconfig": True,
            "cookiefile": None,
            "cookiesfrombrowser": None,
        }

        if mode == MODE_VIDEO:
            if self.ffmpeg_available:
                video_selector = VIDEO_SELECTOR_MAP[video_quality]
                audio_selector = AUDIO_SELECTOR_MAP[audio_quality]
                options["format"] = f"{video_selector}+{audio_selector}/{video_selector}/best"
                options["merge_output_format"] = "mp4"
            else:
                options["format"] = "best"
                self.log_text.append(
                    "[알림] ffmpeg 미설치로 best 단일 스트림으로 다운로드됩니다."
                )
        else:
            audio_selector = AUDIO_SELECTOR_MAP[audio_quality]
            options["format"] = f"{audio_selector}/bestaudio/best"
            if audio_format != "원본 유지":
                if not self.ffmpeg_available:
                    raise RuntimeError(
                        "오디오 변환(mp3/m4a/wav)을 위해 ffmpeg가 필요합니다."
                    )
                options["postprocessors"] = [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": AUDIO_CODEC_MAP[audio_format],
                        "preferredquality": "0",
                    }
                ]

        if self.ffmpeg_available and self.ffmpeg_path is not None:
            options["ffmpeg_location"] = str(self.ffmpeg_path.parent)

        return options

    def start_download(self) -> None:
        if not self.ytdlp_available:
            QMessageBox.critical(
                self,
                "오류",
                "yt-dlp를 찾지 못했습니다. 배포 시 bin/yt-dlp.exe를 포함하세요.",
            )
            return

        url = self.url_input.text().strip()
        if not re.match(r"^https?://", url):
            QMessageBox.warning(self, "입력 오류", "올바른 영상 링크(URL)를 입력하세요.")
            return

        self.log_text.append("[정보] URL 형식 검증 완료")
        self.status_label.setText("정책 검사 중...")
        url_policy = evaluate_url(url)
        if not url_policy.allowed:
            self.log_text.append(f"[정책] 차단됨 | 도메인: {url_policy.host or '-'} | 사유: {url_policy.reason}")
            QMessageBox.warning(
                self,
                "정책 차단",
                f"도메인: {url_policy.host or '-'}\n사유: {url_policy.reason}",
            )
            return
        self.log_text.append(f"[정보] 정책 검사 통과 | 도메인: {url_policy.host}")

        if self.download_worker and self.download_worker.isRunning():
            return

        self.active_history_record_id = self._append_history_record(url, {})
        if self.active_history_record_id:
            self._start_metadata_fetch(self.active_history_record_id, url)
            self.log_text.append("[정보] 메타데이터는 백그라운드에서 확인합니다.")

        output_dir = Path(self.settings.save_path)
        self.status_label.setText("옵션 계산 중...")
        try:
            self._ensure_download_dir(output_dir)
            ydl_opts = self._build_ydl_options(output_dir)
            self.log_text.append("[정보] 포맷/후처리 옵션 계산 완료")
        except Exception as exc:
            self.log_text.append("[오류] 옵션 계산 실패")
            self._update_history_record(self.active_history_record_id, HISTORY_STATUS_FAILED)
            self.active_history_record_id = None
            QMessageBox.critical(self, "오류", str(exc))
            return

        self.status_label.setText("다운로드 준비 완료")
        self.log_text.append(f"[정보] 다운로드 시작: {url}")
        self.log_text.append(
            f"[정보] 적용 옵션 | 모드: {self.settings.download_mode} | 화질: {self.settings.default_video_quality} | 오디오: {self.settings.default_audio_quality} | 포맷: {self.settings.default_audio_format}"
        )
        self.log_text.append("[정보] 스트림 수집 및 다운로드 시작")
        if self.aria2c_available:
            self.log_text.append("[정보] aria2c 외부 다운로더 사용")
        else:
            self.log_text.append("[알림] aria2c 미탑재: yt-dlp 기본 다운로더로 진행")

        self.btn_download.setEnabled(False)

        self.download_worker = DownloadWorker(
            url,
            ydl_opts,
            str(output_dir),
            self.ytdlp_path,
            self.aria2c_path,
        )
        self.download_worker.progress.connect(self._on_download_progress)
        self.download_worker.log.connect(self._on_download_log)
        self.download_worker.success.connect(self._on_download_success)
        self.download_worker.failed.connect(self._on_download_failed)
        self.download_worker.finished.connect(self._on_download_finished)
        self.download_worker.start()

    def _on_download_log(self, line: str) -> None:
        self.log_text.append(line)
        lowered = line.lower()
        if "[download]" in lowered and "destination" in lowered:
            self.status_label.setText("대상 파일 준비 완료")
        elif "[download]" in lowered and "resum" in lowered:
            self.status_label.setText("이어서 다운로드")
        elif "[download]" in lowered and "100%" in lowered:
            self.status_label.setText("다운로드 100% 완료, 후처리 시작")
            self.log_text.append("[정보] 다운로드 완료, 후처리 시작")
        elif "[merger]" in lowered:
            self.status_label.setText("비디오/오디오 병합 중...")
        elif "[extractaudio]" in lowered:
            self.status_label.setText("오디오 변환 중...")
        elif "[ffmpeg]" in lowered:
            self.status_label.setText("ffmpeg 후처리 실행 중...")

    def _on_download_progress(self, percent: float, message: str) -> None:
        self.status_label.setText(message)

    def _on_download_success(self, output_path: str) -> None:
        self.status_label.setText("다운로드 완료")
        self.log_text.append("[정보] 후처리 완료")
        self.log_text.append(f"[완료] 저장 위치: {output_path}")
        self._update_history_record(
            self.active_history_record_id,
            HISTORY_STATUS_SUCCESS,
            output_path=output_path,
        )
        QMessageBox.information(self, "완료", f"다운로드가 완료되었습니다.\n저장 위치: {output_path}")

    def _on_download_failed(self, error_msg: str) -> None:
        self.status_label.setText("다운로드 실패")
        self.log_text.append(f"[오류] 다운로드 실패: {error_msg}")
        self.log_text.append("[오류] 다운로드/후처리 실패")
        self._update_history_record(self.active_history_record_id, HISTORY_STATUS_FAILED)
        if "DRM" in error_msg.upper():
            QMessageBox.warning(
                self,
                "정책 차단",
                "DRM 보호 신호가 감지되어 다운로드가 차단되었습니다.\n"
                "합법적 공개 콘텐츠만 사용해 주세요.",
            )
            return
        QMessageBox.critical(self, "오류", f"다운로드에 실패했습니다.\n{error_msg}")

    def _on_download_finished(self) -> None:
        self.btn_download.setEnabled(True)
        self.active_history_record_id = None
        if self.download_worker is not None:
            self.download_worker.deleteLater()
            self.download_worker = None


def main() -> int:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app_dir = resolve_app_dir()
    user_data_dir = resolve_user_data_dir()
    install_safe_exception_handler(user_data_dir)
    app_icon = load_app_icon(app_dir)
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    consent_dialog = LegalConsentDialog(app_icon)
    if consent_dialog.exec() != QDialog.Accepted:
        return 0

    try:
        window = MainWindow(app_icon)
    except Exception as exc:
        QMessageBox.critical(None, "오류", f"프로그램 초기화 실패:\n{exc}")
        return 1

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

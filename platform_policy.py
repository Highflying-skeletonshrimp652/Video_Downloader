from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

POLICY_ALLOW = "allow"
POLICY_BLOCK_OTT = "block_ott"


@dataclass(frozen=True)
class PlatformRule:
    name: str
    domains: tuple[str, ...]
    policy: str


ALLOWLIST_RULES: tuple[PlatformRule, ...] = (
    PlatformRule("YouTube", ("youtube.com", "youtu.be"), POLICY_ALLOW),
    PlatformRule("Vimeo", ("vimeo.com",), POLICY_ALLOW),
    PlatformRule("Dailymotion", ("dailymotion.com", "dai.ly"), POLICY_ALLOW),
    PlatformRule("Facebook Watch", ("facebook.com", "fb.watch"), POLICY_ALLOW),
    PlatformRule("Instagram", ("instagram.com",), POLICY_ALLOW),
    PlatformRule("X (Twitter)", ("x.com", "twitter.com"), POLICY_ALLOW),
    PlatformRule("TikTok", ("tiktok.com", "vm.tiktok.com"), POLICY_ALLOW),
    PlatformRule("Twitch", ("twitch.tv",), POLICY_ALLOW),
    PlatformRule("Kick", ("kick.com",), POLICY_ALLOW),
    PlatformRule("Trovo", ("trovo.live",), POLICY_ALLOW),
    PlatformRule("Rumble", ("rumble.com",), POLICY_ALLOW),
    PlatformRule("Bilibili", ("bilibili.com", "b23.tv"), POLICY_ALLOW),
    PlatformRule("Youku", ("youku.com",), POLICY_ALLOW),
    PlatformRule("iQIYI", ("iq.com", "iqiyi.com"), POLICY_ALLOW),
    PlatformRule("Tencent Video", ("v.qq.com", "qq.com"), POLICY_ALLOW),
    PlatformRule("Niconico", ("nicovideo.jp", "nico.ms"), POLICY_ALLOW),
    PlatformRule("VK Video", ("vk.com", "vkvideo.ru"), POLICY_ALLOW),
    PlatformRule("Rutube", ("rutube.ru",), POLICY_ALLOW),
    PlatformRule("Odysee", ("odysee.com",), POLICY_ALLOW),
    PlatformRule("DTube", ("d.tube", "dtube.network"), POLICY_ALLOW),
    PlatformRule("PeerTube", ("peertube.tv",), POLICY_ALLOW),
    PlatformRule("BitChute", ("bitchute.com",), POLICY_ALLOW),
    PlatformRule("TED", ("ted.com",), POLICY_ALLOW),
    PlatformRule("Coursera", ("coursera.org",), POLICY_ALLOW),
    PlatformRule("Udemy", ("udemy.com",), POLICY_ALLOW),
    PlatformRule("LinkedIn", ("linkedin.com",), POLICY_ALLOW),
    PlatformRule("Snapchat", ("snapchat.com",), POLICY_ALLOW),
    PlatformRule("Triller", ("triller.co", "triller.tv"), POLICY_ALLOW),
    PlatformRule("Tubi", ("tubitv.com",), POLICY_ALLOW),
    PlatformRule("Pluto TV", ("pluto.tv",), POLICY_ALLOW),
    PlatformRule("Crackle", ("crackle.com", "sonycrackle.com"), POLICY_ALLOW),
    PlatformRule("AfreecaTV", ("afreecatv.com",), POLICY_ALLOW),
    PlatformRule("Chzzk", ("chzzk.naver.com",), POLICY_ALLOW),
    PlatformRule("Naver TV", ("tv.naver.com",), POLICY_ALLOW),
    PlatformRule("KakaoTV", ("tv.kakao.com",), POLICY_ALLOW),
    PlatformRule("Douyin", ("douyin.com",), POLICY_ALLOW),
    PlatformRule("AcFun", ("acfun.cn",), POLICY_ALLOW),
    PlatformRule("Mango TV", ("mgtv.com", "mangotv.com"), POLICY_ALLOW),
    PlatformRule("QQ Video", ("v.qq.com", "qq.com"), POLICY_ALLOW),
    PlatformRule("BBC iPlayer", ("bbc.co.uk", "bbc.com"), POLICY_ALLOW),
    PlatformRule("ITVX", ("itv.com",), POLICY_ALLOW),
    PlatformRule("All 4", ("channel4.com",), POLICY_ALLOW),
    PlatformRule("My5", ("channel5.com",), POLICY_ALLOW),
    PlatformRule("ARD Mediathek", ("ardmediathek.de", "ard.de"), POLICY_ALLOW),
    PlatformRule("ZDF Mediathek", ("zdf.de",), POLICY_ALLOW),
    PlatformRule("France.tv", ("france.tv",), POLICY_ALLOW),
    PlatformRule("NHK World", ("nhk.or.jp", "nhk.jp"), POLICY_ALLOW),
    PlatformRule("Al Jazeera", ("aljazeera.com",), POLICY_ALLOW),
    PlatformRule("Bloomberg", ("bloomberg.com",), POLICY_ALLOW),
    PlatformRule("CNN", ("cnn.com",), POLICY_ALLOW),
    PlatformRule("Fox Nation", ("foxnation.com",), POLICY_ALLOW),
    PlatformRule("Viu", ("viu.com",), POLICY_ALLOW),
    PlatformRule("iflix", ("iflix.com",), POLICY_ALLOW),
    PlatformRule("Hoichoi", ("hoichoi.tv",), POLICY_ALLOW),
    PlatformRule("AltBalaji", ("altbalaji.com",), POLICY_ALLOW),
    PlatformRule("Eros Now", ("erosnow.com",), POLICY_ALLOW),
    PlatformRule("FilmRise", ("filmrise.com",), POLICY_ALLOW),
    PlatformRule("Hayu", ("hayu.com",), POLICY_ALLOW),
    PlatformRule("MagellanTV", ("magellantv.com",), POLICY_ALLOW),
    PlatformRule("Bongo", ("bongobd.com",), POLICY_ALLOW),
    PlatformRule("Stageit", ("stageit.com",), POLICY_ALLOW),
)

BLOCKED_OTT_RULES: tuple[PlatformRule, ...] = (
    PlatformRule("Netflix", ("netflix.com",), POLICY_BLOCK_OTT),
    PlatformRule("Hulu", ("hulu.com",), POLICY_BLOCK_OTT),
    PlatformRule("Amazon Prime Video", ("primevideo.com", "amazon.com"), POLICY_BLOCK_OTT),
    PlatformRule("Disney+", ("disneyplus.com",), POLICY_BLOCK_OTT),
    PlatformRule("Apple TV+", ("tv.apple.com", "apple.com"), POLICY_BLOCK_OTT),
    PlatformRule("HBO Max / Max", ("max.com", "hbomax.com"), POLICY_BLOCK_OTT),
    PlatformRule("Paramount+", ("paramountplus.com",), POLICY_BLOCK_OTT),
    PlatformRule("Peacock", ("peacocktv.com",), POLICY_BLOCK_OTT),
    PlatformRule("Crunchyroll", ("crunchyroll.com",), POLICY_BLOCK_OTT),
    PlatformRule("Rakuten TV", ("rakuten.tv",), POLICY_BLOCK_OTT),
    PlatformRule("Zee5", ("zee5.com",), POLICY_BLOCK_OTT),
    PlatformRule("Hotstar", ("hotstar.com",), POLICY_BLOCK_OTT),
    PlatformRule("Viki", ("viki.com",), POLICY_BLOCK_OTT),
    PlatformRule("WeTV", ("wetv.vip",), POLICY_BLOCK_OTT),
    PlatformRule("MX Player", ("mxplayer.in",), POLICY_BLOCK_OTT),
    PlatformRule("SonyLIV", ("sonyliv.com",), POLICY_BLOCK_OTT),
    PlatformRule("Discovery+", ("discoveryplus.com",), POLICY_BLOCK_OTT),
    PlatformRule("ESPN+", ("espn.com",), POLICY_BLOCK_OTT),
    PlatformRule("Shudder", ("shudder.com",), POLICY_BLOCK_OTT),
    PlatformRule("Gaia", ("gaia.com",), POLICY_BLOCK_OTT),
    PlatformRule("Nebula", ("nebula.tv",), POLICY_BLOCK_OTT),
    PlatformRule("CuriosityStream", ("curiositystream.com",), POLICY_BLOCK_OTT),
    PlatformRule("Kanopy", ("kanopy.com",), POLICY_BLOCK_OTT),
    PlatformRule("Plex", ("plex.tv",), POLICY_BLOCK_OTT),
    PlatformRule("Redbox", ("redbox.com",), POLICY_BLOCK_OTT),
    PlatformRule("Vudu", ("vudu.com", "fandango.com"), POLICY_BLOCK_OTT),
    PlatformRule("FuboTV", ("fubo.tv",), POLICY_BLOCK_OTT),
    PlatformRule("Sling TV", ("sling.com",), POLICY_BLOCK_OTT),
    PlatformRule("YouTube TV", ("tv.youtube.com",), POLICY_BLOCK_OTT),
)

ALL_RULES: tuple[PlatformRule, ...] = ALLOWLIST_RULES + BLOCKED_OTT_RULES

ALLOWED_EXTRACTOR_TOKENS: tuple[str, ...] = (
    "youtube",
    "vimeo",
    "dailymotion",
    "facebook",
    "instagram",
    "twitter",
    "tiktok",
    "twitch",
    "kick",
    "trovo",
    "rumble",
    "bilibili",
    "youku",
    "iqiyi",
    "tencent",
    "qq",
    "niconico",
    "vk",
    "rutube",
    "odysee",
    "dtube",
    "peertube",
    "bitchute",
    "ted",
    "coursera",
    "udemy",
    "linkedin",
    "snapchat",
    "triller",
    "tubi",
    "pluto",
    "crackle",
    "afreecatv",
    "chzzk",
    "naver",
    "kakao",
    "douyin",
    "acfun",
    "mangotv",
    "bbc",
    "itv",
    "channel4",
    "my5",
    "ardmediathek",
    "zdf",
    "francetv",
    "nhk",
    "aljazeera",
    "bloomberg",
    "cnn",
    "foxnation",
    "viu",
    "iflix",
    "hoichoi",
    "altbalaji",
    "erosnow",
    "filmrise",
    "hayu",
    "magellantv",
    "bongo",
    "stageit",
)

BLOCKED_EXTRACTOR_TOKENS: tuple[str, ...] = (
    "netflix",
    "hulu",
    "primevideo",
    "disneyplus",
    "appletv",
    "hbomax",
    "paramountplus",
    "peacock",
    "crunchyroll",
    "rakutentv",
    "zee5",
    "hotstar",
    "viki",
    "wetv",
    "mxplayer",
    "sonyliv",
    "discoveryplus",
    "espnplus",
    "shudder",
    "gaia",
    "nebula",
    "curiositystream",
    "kanopy",
    "plex",
    "redbox",
    "vudu",
    "fubo",
    "sling",
    "youtubetv",
)


@dataclass(frozen=True)
class UrlPolicyResult:
    allowed: bool
    host: str
    platform_name: str
    reason: str


def _normalize_host(host: str) -> str:
    value = host.strip().lower().rstrip(".")
    if value.startswith("www."):
        value = value[4:]
    return value


def get_host(url: str) -> str:
    parsed = urlparse(url)
    return _normalize_host(parsed.hostname or "")


def _host_matches(host: str, domain: str) -> bool:
    normalized_domain = _normalize_host(domain)
    return host == normalized_domain or host.endswith(f".{normalized_domain}")


def find_domain_rule(host: str) -> PlatformRule | None:
    if not host:
        return None
    normalized = _normalize_host(host)
    matches: list[tuple[int, int, PlatformRule]] = []
    for rule in ALL_RULES:
        for domain in rule.domains:
            if _host_matches(normalized, domain):
                normalized_domain = _normalize_host(domain)
                blocked_priority = 1 if rule.policy == POLICY_BLOCK_OTT else 0
                matches.append((len(normalized_domain), blocked_priority, rule))
                break

    if not matches:
        return None

    matches.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return matches[0][2]


def evaluate_url(url: str) -> UrlPolicyResult:
    host = get_host(url)
    if not host:
        return UrlPolicyResult(
            allowed=False,
            host="",
            platform_name="-",
            reason="URL에서 도메인을 확인할 수 없습니다.",
        )

    rule = find_domain_rule(host)
    if rule and rule.policy == POLICY_BLOCK_OTT:
        return UrlPolicyResult(
            allowed=False,
            host=host,
            platform_name=rule.name,
            reason="유료 OTT/DRM 가능성이 높은 도메인은 정책상 차단됩니다.",
        )

    return UrlPolicyResult(
        allowed=True,
        host=host,
        platform_name=rule.name if rule else "미분류",
        reason="통과",
    )


def evaluate_extractor_allowlist(extractor: str) -> tuple[bool, str]:
    value = (extractor or "").strip().lower()
    if not value:
        return False, "플랫폼 추출자 정보를 확인할 수 없습니다."

    if any(token in value for token in BLOCKED_EXTRACTOR_TOKENS):
        return False, "유료 OTT/DRM 가능성이 높은 플랫폼은 정책상 차단됩니다."

    if any(token in value for token in ALLOWED_EXTRACTOR_TOKENS):
        return True, "통과"

    return False, "allowlist에 등록된 플랫폼만 허용됩니다."


def detect_drm_signals(info: dict) -> bool:
    if not isinstance(info, dict):
        return False

    for key in ("has_drm", "is_drm"):
        if info.get(key):
            return True

    for key in ("drm_family", "drm_families", "license_url"):
        value = info.get(key)
        if isinstance(value, str) and value.strip():
            return True

    formats = info.get("formats")
    if isinstance(formats, list):
        for fmt in formats:
            if not isinstance(fmt, dict):
                continue
            if fmt.get("has_drm") or fmt.get("is_drm") or fmt.get("drm_family"):
                return True

            hint_parts = [
                str(fmt.get("format_note", "")),
                str(fmt.get("manifest_url", "")),
                str(fmt.get("url", "")),
                str(fmt.get("protocol", "")),
            ]
            hint = " ".join(hint_parts).lower()
            if any(keyword in hint for keyword in ("drm", "widevine", "playready", "fairplay")):
                return True

    return False


def build_policy_overview_text() -> str:
    return (
        "[플랫폼 정책 안내]\n"
        "- 허용/차단 도메인 목록은 내부 정책으로만 관리되며 UI에 명시하지 않습니다.\n"
        "- 특정 서비스명을 나열하지 않는 중립 정책을 적용합니다.\n\n"
        "[정책]\n"
        "- DRM 감지 시 차단\n"
        "- 유료 OTT 도메인 차단\n"
        "- 로그인 세션 자동 추출 금지\n"
        "- 특정 플랫폼 전용 다운로더 아님\n"
        "- allowlist 기반 구조"
    )

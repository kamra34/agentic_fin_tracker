"""Tiny dependency-free User-Agent parser for the admin session view.

Good enough to show "Chrome on Windows" style labels in login history; not a full
UA database. Stores the raw UA alongside, so we can always re-parse later if needed.
"""


def parse_device(ua: str) -> str:
    if not ua:
        return "Unknown device"
    u = ua.lower()

    # Operating system
    if "windows" in u:
        os_name = "Windows"
    elif "iphone" in u:
        os_name = "iPhone"
    elif "ipad" in u:
        os_name = "iPad"
    elif "mac os" in u or "macintosh" in u:
        os_name = "macOS"
    elif "android" in u:
        os_name = "Android"
    elif "linux" in u:
        os_name = "Linux"
    else:
        os_name = "Unknown OS"

    # Browser (order matters: Edge/Opera spoof Chrome, Chrome spoofs Safari)
    if "edg/" in u or "edga/" in u or "edgios/" in u:
        browser = "Edge"
    elif "opr/" in u or "opera" in u:
        browser = "Opera"
    elif "chrome" in u and "chromium" not in u:
        browser = "Chrome"
    elif "firefox" in u or "fxios" in u:
        browser = "Firefox"
    elif "safari" in u and "chrome" not in u:
        browser = "Safari"
    else:
        browser = "Unknown browser"

    return f"{browser} on {os_name}"

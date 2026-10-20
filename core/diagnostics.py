"""Optional page captures for diagnosing scheduled runs."""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


def capture_page(page, username, stage, logger, detail=""):
    """Capture without changing task behavior or exporting browser credentials."""
    if os.getenv("DOUYIN_CAPTURE_PAGES") != "1":
        return
    try:
        directory = Path("logs")
        directory.mkdir(exist_ok=True)
        account = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(username)).strip("_") or "account"
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        prefix = directory / f"{timestamp}_{account}_{stage}"
        metadata = {
            "stage": stage,
            "url": page.url,
            "detail": str(detail),
        }
        Path(str(prefix) + ".json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        page.screenshot(path=str(prefix) + ".png", full_page=True, timeout=10000)
        logger.info("页面截图已保存: %s.png", prefix)
    except Exception as exc:
        logger.warning("页面截图保存失败: %s", exc)

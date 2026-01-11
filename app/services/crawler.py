import os
import uuid
import logging
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.services.detector import DeepfakeDetector
from app import db
from app.models import Violation

# Optional dependency
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

logger = logging.getLogger(__name__)


class InvestigationCrawler:
    def __init__(self, upload_folder):
        self.detector = DeepfakeDetector()
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def _is_youtube_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc in {
            "www.youtube.com",
            "youtube.com",
            "m.youtube.com",
            "youtu.be",
        }

    def _download_image(self, image_url: str) -> bytes | None:
        try:
            response = requests.get(image_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return None

            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image"):
                return None

            if len(response.content) < 5_000:
                return None

            return response.content

        except requests.RequestException as e:
            logger.warning(f"Image download failed: {image_url} ({e})")
            return None

    def _analyze_image(self, image_url, source_url, contact_info="Unknown"):
        img_data = self._download_image(image_url)
        if not img_data:
            return None

        parsed = urlparse(image_url)
        ext = os.path.splitext(parsed.path)[1] or ".jpg"

        temp_filename = f"scan_{uuid.uuid4()}{ext}"
        temp_path = os.path.join(self.upload_folder, temp_filename)

        try:
            with open(temp_path, "wb") as f:
                f.write(img_data)

            probability = self.detector.detect_deepfake(temp_path)

            if probability > 0.5:
                violation = Violation(
                    target_url=source_url,
                    image_url=image_url,
                    ai_probability=probability,
                    contact_info=contact_info,
                )
                db.session.add(violation)

                return {
                    "image_url": image_url,
                    "probability": probability,
                    "status": "DETECTED",
                }

        except Exception as e:
            logger.error(f"Detection failed for {image_url}: {e}")
            db.session.rollback()

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return None

    def scan_youtube(self, target_url):
        if not YT_DLP_AVAILABLE:
            return {"error": "yt-dlp library not installed"}

        results = []

        try:
            with yt_dlp.YoutubeDL(
                {"quiet": True, "skip_download": True, "no_warnings": True}
            ) as ydl:
                info = ydl.extract_info(target_url, download=False)

            thumbnails = info.get("thumbnails") or []
            if not thumbnails and info.get("thumbnail"):
                thumbnails = [{"url": info["thumbnail"]}]

            for thumb in reversed(thumbnails):
                url = thumb.get("url")
                if not url:
                    continue

                result = self._analyze_image(
                    url,
                    target_url,
                    contact_info=f"YouTube Channel: {info.get('uploader_url', 'Unknown')}",
                )
                if result:
                    results.append(result)
                    break

            db.session.commit()
            return results

        except Exception as e:
            logger.error(f"YouTube scan error: {e}")
            db.session.rollback()
            return {"error": str(e)}

    def scan_url(self, target_url):
        if self._is_youtube_url(target_url):
            return self.scan_youtube(target_url)

        results = []

        try:
            response = requests.get(target_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return {"error": "Failed to fetch target URL"}

            soup = BeautifulSoup(response.text, "html.parser")
            images = soup.find_all("img")

            contact_info = "Unknown"
            mailto = soup.select_one("a[href^=mailto]")
            if mailto:
                contact_info = mailto["href"].replace("mailto:", "")

            scanned = 0
            for img in images:
                if scanned >= 10:
                    break

                src = img.get("src")
                if not src:
                    continue

                full_url = urljoin(target_url, src)

                if any(k in full_url.lower() for k in ["logo", "icon", "pixel", "tracker"]):
                    continue

                result = self._analyze_image(full_url, target_url, contact_info)
                if result:
                    results.append(result)

                scanned += 1

            db.session.commit()
            return results

        except Exception as e:
            logger.error(f"Crawling error: {e}")
            db.session.rollback()
            return {"error": str(e)}

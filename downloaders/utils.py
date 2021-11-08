import glob
import logging
import os

import requests
from bs4 import BeautifulSoup

from exceptions.solanum_exceptions import NotAbleToDownloadException

LOGGER = logging.getLogger(__name__)
TIMEOUT_SEG = 7


def tidy_up_url(url: str) -> str:
    if url.startswith("//"):
        # If no protocol was supplied, add https
        url = "https:" + url

    if '?' in url:
        url = url[:url.rfind('?')]

    if url.endswith("/"):
        url = url[:-1]
    return url


def prepare_download_folder(folder):
    if not os.path.exists(folder):
        LOGGER.debug("Creating folder %s" % folder)
        os.makedirs(folder)


def url_contains_extension(url: str) -> bool:
    return tidy_up_url(url)[url.rfind(".") + 1:] in ["jpeg", "png", "jpg", "gif", "bmp"]


def extract_image_url_from_dom(image_location_url: str, dom_selector) -> str:

    html_source = requests.get(image_location_url, timeout=TIMEOUT_SEG).text

    soup = BeautifulSoup(html_source, "lxml")

    matches = soup.select(dom_selector)

    if not matches:
        raise NotAbleToDownloadException(f"Couldn't process {image_location_url}")

    for m in matches:
        image_url = tidy_up_url(m['href'])
        return image_url


def image_already_exists(folder: str, image) -> bool:

    # The filename pattern is as follows:
    # "%s_%s_%s_%s_%s" % (self.section, self.species, self.sample_id, self.source, self.row_idx)
    filename_pattern = "*%s*%s*%s*"

    pattern_to_search = filename_pattern % (image.sample_id, image.source, image.row_idx)
    pattern_to_search = os.path.join(folder, image.section, pattern_to_search)
    LOGGER.debug("Pattern to search: %s" % pattern_to_search)

    return len(glob.glob(pattern_to_search)) > 0


def is_url_pointing_to_image_bytes(location_url: str) -> tuple:
    response = requests.head(location_url,
                             allow_redirects=True,
                             timeout=TIMEOUT_SEG)

    if not response.ok:
        raise NotAbleToDownloadException(f"{location_url} returned a {response.status_code} HTTP Code!")

    # Let's determine the MIME type of the link, more info:
    #  https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
    mime_type, mime_subtype = response.headers["Content-Type"].split("/")

    if mime_type.lower() == "image":
        return True, mime_subtype
    else:
        return False, None

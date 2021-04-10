import logging
import os
from argparse import Namespace

import requests
import pandas as pd

from downloaders import utils
from exceptions.solanum_exceptions import NotAbleToDownloadException

LOGGER = logging.getLogger(__name__)


class Downloader:

    def __init__(self, args: Namespace):

        self.args = args
        self.failed_images = pd.DataFrame(columns=["id", "species", "url", "section", "source"])

    def download(self):

        # Read all CSVs into Pandas Dataframes
        LOGGER.info("Reading CSVs...")
        dataframes = []

        for csv in self.args.csvs:
            df = pd.read_csv(csv)
            dataframes.append(df)

        samples_to_download = pd.concat(dataframes)

        # 1. Filter out duplicated URLs so as to try them only once
        samples_to_download.drop_duplicates(subset=["url"],
                                            keep="first",
                                            inplace=True)

        # 2. Create parent download folder
        utils.prepare_download_folder(self.args.folder)

        # 3. Download images
        self._download_images(samples_to_download, self.args.folder)

        LOGGER.info("The downloader is done!")

    def _download_images(self, images: pd.DataFrame, folder: str):
        #    1. If they end with an extension, download them directly
        #    1. If not, download the html and parse the img#src attribute
        # 4. If there's a failure
        #    1. Log it
        #    1. Add it to a pandas DF for reporting (which should also be persisted to disk eventually)
        # 5. Should detect if the image already exists on disk and if it does, skip it.
        #    1. Use the filename to detect duplicates.
        #    1. This will only work if there is 1 and only 1 picture per ID.
        #    1. These should only be logged

        for index, row in images.iterrows():

            image = Image(index, row)

            if not self.args.should_overwrite and utils.image_already_exists(folder, image):
                LOGGER.info(f"Skipping image {image.filename} as we already have its images!")
                continue

            LOGGER.info('Downloading %s...' % image.location_url)

            try:
                image_folder = os.path.join(folder, image.section)
                utils.prepare_download_folder(image_folder)

                with requests.get(image.url) as response:
                    if response.ok:

                        full_filename = os.path.join(image_folder, image.filename)

                        LOGGER.info('Saving %s...' % full_filename)

                        with open(full_filename, 'wb') as fo:
                            for chunk in response.iter_content(4096):
                                fo.write(chunk)

                    else:
                        self.failed_images.append(row)
                        LOGGER.error("Failed to download, we got an HTTP %i error for %s" % (response.status_code,
                                                                                             image.url))

            except requests.exceptions.ConnectionError as ex:
                LOGGER.error(ex)
                continue
            except Exception as exception:
                LOGGER.error("Failed to download %s!" % image.url)
                LOGGER.error(ex)
                self.failed_images.append(row)
                continue

        if not self.failed_images.empty:
            LOGGER.info(f"Saving report of failed images to {folder}...")
            self.failed_images.to_csv(f"{folder}/failed_images.csv")


class Image:

    def __init__(self, row_idx: int, row: pd.Series):
        self.row_idx = row_idx
        self.sample_id = row["id"]
        self.species = row["species"]
        self.location_url = row["url"]
        self.section = row["section"]
        self.source = row["source"]

        # This will be lazily calculated later
        self._url = None

        # Pattern should have the following format:
        # <section>_<species>_<id>_<source>_<idx>.jpg|png|gif
        self.filename = "%s_%s_%s_%s_%s" % (self.section, self.species, self.sample_id, self.source, self.row_idx)

    @property
    def url(self):
        """
        The direct URL to the bytes of the image. This is lazily calculated.
        """
        if self._url:
            return self._url

        if utils.url_contains_extension(self.location_url):
            self._url = self.location_url
            image_extension = self._url[self._url.rfind(".") + 1:]

        else:
            # Check first if the URL is without extension but is still pointing to the bytes of an image, we'll use
            #  the Content-Type in a HEAD HTTP request to retrieve this information
            is_url_pointing_to_image_bytes, image_extension = utils.is_url_pointing_to_image_bytes(self.location_url)
            self._url = self.location_url

            # As a last resort, let's try to parse the DOM to see if we can find the image
            if not is_url_pointing_to_image_bytes:
                LOGGER.debug(f"{self.location_url} doesn't point to an image, attempting to extract it from the DOM!")
                self._url = utils.extract_image_url_from_dom(self.location_url,
                                                             "img[src]")
                image_extension = self._url[self._url.rfind(".") + 1:]

        # We tried our best but we were not able to find a suitable image URL, so let's abort the downloading
        #  of this image
        if not self._url:
            raise NotAbleToDownloadException(f"Couldn't find an image link in {self.location_url}")

        self.filename = "%s.%s" % (self.filename, image_extension)

        return self._url

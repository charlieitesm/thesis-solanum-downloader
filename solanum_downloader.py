#!/usr/bin/python3

import logging
import sys
from argparse import ArgumentParser

from downloaders.downloader import Downloader

LOGGER = logging.getLogger(__name__)
VERSION = "0.0.1"


def main():
    args = parse_args()
    configure_logging(args.is_debug)

    downloader = Downloader(args)

    downloader.download()


def configure_logging(is_debug=False):
    log_format = "%(asctime)s [%(name)s] [%(levelname)s] %(message)s"

    file_handler = logging.FileHandler('solanum_downloader.log')

    console_handler = logging.StreamHandler(sys.stdout)
    err_handler = logging.StreamHandler(sys.stderr)

    logging.basicConfig(format=log_format,
                        level=logging.DEBUG if is_debug else logging.INFO,
                        handlers=[console_handler, file_handler, err_handler])

    LOGGER.info("******* Solanum Downloader *******")
    LOGGER.debug("Ready to DEBUG!")


def parse_args():
    """Parse args with argparse
    :returns: args
    """
    parser = ArgumentParser(description=f"Solanum Downloader {VERSION} - Potatos and tomatos!")

    parser.add_argument('--destination', '-d',
                        dest='folder',
                        default='solanum_output',
                        help="Defines a download folder.")

    parser.add_argument("--overwrite", "-o",
                        dest="should_overwrite",
                        action="store_true",
                        help="Specifies if files should be overwritten if they were already downloaded.")

    parser.add_argument("--debug",
                        dest="is_debug",
                        action="store_true",
                        help="Activates debug mode.")

    parser.add_argument('csvs',
                        nargs='+',
                        metavar="CSVs",
                        help="List CSV file locations that contain the URLs to download.")

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    main()


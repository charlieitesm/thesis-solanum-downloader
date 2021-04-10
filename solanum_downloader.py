#!/usr/bin/python3

from argparse import ArgumentParser
import logging
import sys

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
    logging.basicConfig(format=log_format,
                        filename='solanum_downloader.log',
                        level=logging.DEBUG if is_debug else logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.DEBUG)

    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

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


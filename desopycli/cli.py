#!/bin/env python
# -*- coding: utf-8 -*-
"""
DesoPy Cli

Usage:
    deso [options] post <CONTENT> [<ATTACHMENT_PATH>]
    deso [options] repost <POSTHEX>
    deso [options] quote <POSTHEX> <CONTENT>
    deso [options] following
    deso [options] notifications
    deso [options] shell
    deso [options] activity
    deso --version

Options:
    -h --help   Show this screen.
    --version   Show version.
    -A --account=<account>   `account` name to substitute in `pass` path [default: asyncmind]
    -S --seedhex-pass-path-template=<seedhexpathtemplate>  Pass path for seedhex [default: crypto/deso/{account}/seedhex]
    -K --key-pass-path-template=<keypathtemplate>  Pass path for deso public key [default: crypto/deso/{account}/key]


"""
from desopycli import DesoCli, __VERSION__
import logging
import logging.config

from docopt import docopt
from pprint import pprint

log_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file_handler": {
            "level": "DEBUG",
            "filename": "desopycli.log",
            "class": "logging.FileHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": ["file_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
logging.config.dictConfig(log_dict)

logger = logging.getLogger(__name__)


def main():
    opts = docopt(__doc__)
    logger.debug(opts)
    deso = DesoCli(
        opts["--key-pass-path-template"].format(account=opts["--account"]),
        opts["--seedhex-pass-path-template"].format(account=opts["--account"]),
    )
    if opts["post"] is True:
        deso.post(opts["<CONTENT>"], opts["<ATTACHMENT_PATH>"])
    if opts["repost"] is True:
        deso.repost(opts["<POSTHEX>"])
    if opts["quote"] is True:
        deso.quote(opts["<CONTENT>"], opts["<POSTHEX>"])
    elif opts["following"] is True:
        deso.following()
    elif opts["notifications"] is True:
        deso.notifications()
    elif opts["shell"] is True:
        deso.shell()
    elif opts["activity"] is True:
        deso.activity()
    elif opts["--version"]:
        print(__VERSION__)

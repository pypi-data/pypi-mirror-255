import logging
import os
import json
import time
from datetime import datetime

from .constants import *


def setup_logger():
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s"  # %(filename)s %(funcName)s():
    DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
    LOG_SUFFIX = time.strftime("%Y%m%d")
    LOG_FILE = os.path.join(PATH.LOG_PATH, f"{LOG_SUFFIX}.log")
    logging.addLevelName(25, "HTTP")
    logging.addLevelName(26, "RESPONSE")

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )
    logger = logging.getLogger(__name__)

    def http(self, message, *args, **kws):
        if self.isEnabledFor(25):
            self._log(25, message, args, **kws)

    def response(self, message, *args, **kws):
        if self.isEnabledFor(26):
            self._log(26, message, args, **kws)

    logging.Logger.http = http
    logging.Logger.response = response

    return logger


def get_time():
    return datetime.now().strftime("%H:%M:%S")


def algnprint(input_dict):
    max_key_length = max(len(key) for key in input_dict.keys()) + 1
    for key, value in input_dict.items():
        key += ":"
        formatted_key = f"{key:{max_key_length}}"
        print(f"{formatted_key} {value}")


def jprint(dict):
    print(json.dumps(dict, indent=4, ensure_ascii=False))


def jlog(dict):
    return json.dumps(dict, indent=4, ensure_ascii=False)


def jsave(dict, dir=None):
    with open(dir, "w+") as f:
        json.dump(dict, f, indent=4, ensure_ascii=False)
    print(f"jsave to {dir}")


def lprint(list, with_index=True):
    max_index_width = len(str(len(list) - 1))
    for index, item in enumerate(list):
        if with_index:
            index_str = str(index).rjust(max_index_width)
            print(f"{index_str} {item}")
        else:
            print(item)

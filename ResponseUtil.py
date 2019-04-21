# !/usr/bin/env python
# coding=utf-8
import functools
import json
import logging


def debug(enable=False, expect=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            if enable:
                return True, expect
            else:
                return func(*args, **kw)
        return wrapper
    return decorator


def success(response):
    if response:
        result = str(response, encoding='utf-8')
        logging.info("Get Response : %s" % result)
        obj = json.loads(result)
        if obj:
            if "Code" in obj:
                code = obj["Code"]
                if code:
                    logging.error("Remote Request Error Code : %s" % code)
                else:
                    # code equals None means success.
                    return True
            # code not exists means success.
            return True
        else:
            logging.error("Get JSON of None.")
    else:
        logging.error("Get Response of None.")
    return False
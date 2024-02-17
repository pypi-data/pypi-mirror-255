import os
import re


def isNone(x):
    return True if type(x) == type(None) else False

def isFile(fn):
    return True if os.path.isfile(fn) else False

def validate(apikey):
    try:
        return re.match(
            '^([0-9a-fA-F]{8})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{4})-([0-9a-fA-F]{12})$',
            apikey)
    except:
        return False

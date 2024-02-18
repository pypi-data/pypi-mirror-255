import os
import yaml

import string
from datetime import timedelta
from dateutil.parser import parse
from dateutil.tz import gettz

from glom import glom, assign

# import jmespath


# ------------------------------------------------
# File and config helpers
# ------------------------------------------------
def expandpath(path):
    if path:
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        path = os.path.abspath(path)
        while path[-1] == "/":
            path = path[:-1]
    return path


def load_config(env):
    """Merge config files"""
    cfg = env.__dict__
    for path in reversed(env.config_files):
        try:
            data = yaml.load(open(path, "rt"), Loader=yaml.Loader)
            # merge(cfg, data, inplace=True) # use any deep merge library or ...
            cfg.update(data)

        except FileNotFoundError:
            pass

    env.folders = {expandpath(p): None for p in env.folders}


def save_config(env):
    os.makedirs(os.path.dirname(env.config_file), exist_ok=True)
    yaml.dump(env.__dict__, open(env.config_file, "wt"))


# --------------------------------------------------
#  Convert Base
# --------------------------------------------------

# CHAR_LOOKUP = list(string.digits + string.ascii_letters)

#  avoid use of numbers (so can be used as regular attribute names with ".")
CHAR_LOOKUP = list(string.ascii_letters)
INV_LOOKUP = {c: i for i, c in enumerate(CHAR_LOOKUP)}


def convert_base(number, base, padding=-1, lookup=CHAR_LOOKUP):
    """Coding a number into a string in base 'base'

    results will be padded with '0' until minimal 'padding'
    length is reached.

    lookup is the char map available for coding.
    """
    if base < 2 or base > len(lookup):
        raise RuntimeError(f"base: {base} > coding map length: {len(lookup)}")
    mods = []
    while number > 0:
        mods.append(lookup[number % base])
        number //= base

    while len(mods) < padding:
        mods.append(lookup[0])

    mods.reverse()
    return ''.join(mods)


def from_base(key, base, inv_lookup=INV_LOOKUP):
    """Convert a coded number in base 'base' to an integer."""
    number = 0
    keys = list(key)
    keys.reverse()
    w = 1
    for c in keys:
        number += INV_LOOKUP[c] * w
        w *= base
    return number


# def new_uid(base=50):
# number = uuid.uuid1()
# return convert_base(number.int, base)
SEED = 12345


def new_uid(base=50):
    global SEED
    SEED += 1
    return convert_base(SEED, base)


# from xml.sax.saxutils import escape
# ------------------------------------------------
# jinja2 filters
# ------------------------------------------------
def escape(text: str):
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text


def fmt(value, fmt=">40"):
    fmt = "{:" + fmt + "}"
    try:
        value = fmt.format(value)
    except:
        pass
    return value


# ------------------------------------------------
# glom extensions
# ------------------------------------------------
def setdefault(obj, path, val, missing=dict):
    current = glom(obj, path, default=None)
    if current is None:
        assign(obj, path, val, missing=missing)
        return val
    return current


# ------------------------------------------------
# Converter functions
# ------------------------------------------------
def I(x):
    return x


def INT(x):
    if x is None:
        return 0
    return int(x)


def FLOAT(x):
    if x is None:
        return 0.0
    return float(x)


def BOOL(x):
    if x is None:
        return False
    if isinstance(x, str):
        return x.lower() in ("true", "yes", "1")

    return bool(x)


TZINFOS = {"UTC": gettz(" Etc/UTC")}


def DATE(x):
    if x is None:
        return None

    return parse(x, tzinfos=TZINFOS)


def DURATION(x):  # TODO
    return timedelta(days=float(x))


def TEXT(x):
    return x.text


def STRIP(x):
    return x.strip()


# ------------------------------------------------
# console
# ------------------------------------------------

GREEN = "\033[32;1;4m"
RESET = "\033[0m"


last_sepatator = 40


def banner(
    header,
    lines=None,
    spec=None,
    sort_by=None,
    sort_reverse=True,
    output=print,
    color=GREEN,
):
    global last_sepatator
    lines = lines or []
    # compute keys spaces
    m = 1 + max([len(k) for k in lines] or [0])
    if isinstance(lines, dict):
        if sort_by:
            idx = 0 if sort_by.lower().startswith("keys") else 1
            lines = dict(
                sorted(
                    lines.items(),
                    key=lambda item: item[idx],
                    reverse=sort_reverse,
                )
            )
        _lines = []
        for k, v in lines.items():
            if spec:
                try:
                    v = glom(v, spec)
                except:
                    v = getattr(v, spec)

            line = f"{k.ljust(m)}: {v}"
            _lines.append(line)
        lines = _lines

    if lines:
        m = max([len(l) for l in lines])
        last_sepatator = m
    elif last_sepatator:
        m = last_sepatator
    else:
        m = max([40, len(header)]) - len(header) + 1

    # m = max([len(l) for l in lines] or [40, len(header)]) - len(header) + 1
    output(f"{color}{header}{' ' * m}{RESET}")
    for line in lines:
        output(line)

"""Main module."""

# library modules
import asyncio
import os
import pickle
import re
import time


import uvloop
# import ryaml
import yaml

# library partial
# from time import sleep


# local imports
from .helpers import expandpath
from .parallel import Parallel, AsyncParallel

# 3rd party libraries
# ---------------------------------------------------------
# helpers
# ---------------------------------------------------------
from agptools.containers import walk, rebuild, deep_chain


def myget(data, keys):
    for key in keys:
        data = data[key]
    return data


def myholder(data: dict, *keys):
    _keys = list(deep_chain(keys))

    for key in _keys[:-1]:
        ## "thread-safe way"
        # while (new := data.get(key)) is None:
        # data.setdefault(key, {})

        # need to to this way because lists doesn't have 'get' method
        if isinstance(data, list):
            data = data[key]  # must exists (can't create items in lists)
        else:
            data = data.setdefault(key, {})

    return data, _keys[-1]


def myassign(data, value, keys):
    data, key = myholder(data, keys)
    data[key] = value


# ---------------------------------------------------------
# storage
# ---------------------------------------------------------
# from .storage import Storage
from .storage import DualStorage as Storage

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)

# subloger = logger(f'{__name__}.subloger')


# =========================================================
# syncmodels
# =========================================================


class COPY:
    pass


class SyncModel:
    MAPPERS = {}
    RESTRUCT_DATA = {}
    RETAG_DATA = {}
    REFERENCE_MATCHES = []
    KINDS_UID = {}
    MODEL = None  # calleable to create a Model instance

    def __init__(
        self,
        config_path=None,
        overwrite=False,
        save_model=True,
        num_threads=None,
        db_url=None,
    ):
        if not config_path:
            config_path = "config.yaml"
        config_path = expandpath(config_path)
        self.root = os.path.dirname(config_path)
        self.stats_path = os.path.join(self.root, "stats.yaml")

        # env_path = os.path.join(self.root, '.env')
        # log.info(f"loading ENV from: {env_path}")
        # load_dotenv(env_path)

        self.cfg = yaml.load(open(config_path, "rt"), Loader=yaml.Loader)

        # runner / threads
        num_threads = num_threads or self.cfg.get("threads", 8)
        #self.runner = Parallel(num_threads=num_threads)
        self.runner = AsyncParallel(num_threads=num_threads)
        self._add_task = self.runner.add_task

        self.model = None

        # storage
        db_url = db_url or self.cfg.get("db_url", "./data")
        self.db = Storage(url=db_url)

        self._save_model = save_model
        self._overwrite = overwrite

    def save_model(self, table="model", data=None):
        if data is None:
            if isinstance(self.model, dict):
                data = self.model
            else:
                data = self.model.dict()

        self.db.set(table, data)

    def load_model(self):
        try:
            self.model = pickle.load(open("model.pickle", "rb"))
            # self.model = yaml.load(open("model.yaml", "r"), Loader=yaml.Loader)
        except Exception as why:
            log.error(f"can't load model from disk: {why}")

    def sync(self):
        for func, args, kwargs in self._bootstrap():
            self._add_task(func, *args, **kwargs)

        uvloop.install()
        asyncio.run(self.runner.run())
        
        print(f"elapsed: {self.runner.elapsed}")
        self._build_items()
        if self._save_model:
            self.save_model()
        return self.model

    def _bootstrap(self):
        raise NotImplementedError()

    def _build_items(self):
        # _model = self.MODEL()
        model = self.model
        for kind, holder in model.__dict__.items():
            holder = getattr(model, kind)
            for uid, data in holder.items():
                item = self.new(kind, data)
                holder[uid] = item
        foo = 1

    def new(self, type_, data):
        data = self.convert_into_references(data)

        klass = self.MAPPERS.get(type_)
        if not klass:
            log.warning(f"missing MAPPERS[{type_}] class!")
            return

        item = klass.pydantic(data)
        return item

    def _clean(self, kind, data):
        for k, v in data.items():
            if isinstance(v, str):
                data[k] = v.strip()
        return data

    def _restruct(self, kind, data, reveal):
        restruct = {}
        info = self.RESTRUCT_DATA.get("default", {})
        info.update(self.RESTRUCT_DATA.get(kind, {}))
        for pattern, (new_path, new_value) in info.items():
            for path, value in reveal.items():
                m = re.match(pattern, path)
                if m:
                    d = m.groupdict()
                    d["value"] = value
                    key = tuple(new_path.format_map(d).split("/"))
                    _value = value if new_value == COPY else new_value.format_map(d)
                    restruct[key] = _value

        restruct = rebuild(restruct, result={})
        data = {**data, **restruct}

        return data

        # expand all tagging info

    def convert_into_references(self, value):
        if self.REFERENCE_MATCHES:
            id_keys = list(
                walk(
                    value,
                    keys_included=self.REFERENCE_MATCHES,
                    include_struct=False,
                )
            )
            for idkey, idval in id_keys:
                # myassign(value, myget(value, idkey), idkey[:-1])
                myassign(value, idval, idkey[:-1])

        return value

    def get_uid(self, kind, item):
        # uid = getattr(item, 'id', None)
        # if uid is None:
        # use render templates
        if kind in self.KINDS_UID:
            uid_key, func, id_key = self.KINDS_UID[kind]
            # uid_key = self.KINDS_UID.get(kind, '{id}')
            if not isinstance(item, dict):
                item = item.dict()
            uid = uid_key.format_map(item)
            # uid = item[uid]
            uid = func(uid)
            item[id_key] = uid
        else:
            uid = item["id"]
        return uid

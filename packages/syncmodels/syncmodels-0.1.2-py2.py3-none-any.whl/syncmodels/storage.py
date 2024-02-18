# ----------------------------------------------------------
# Storage Port
# ----------------------------------------------------------
import os
import pickle
import time
import yaml

from surrealdb import Surreal


from recommender.helpers import expandpath
# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)
class StoragePort:
    PATH_TEMPLATE = "{self.url}/{table}"
    
    def __init__(self, url="./db"):
        url = expandpath(url)
        os.makedirs(url, exist_ok=True)
        self.url = url
        
    def _file(self, table):
        return self.PATH_TEMPLATE.format_map(locals())

    async def get(self, table, query=None, **params):
        raise NotImplementedError
        # return requests.get(f"{self.url}{path}", params=params)

    async def set(self, table, data, merge=True):
        raise NotImplementedError

    async def put(self, table, query=None, **params):
        raise NotImplementedError
        # return requests.get(f"{self.url}{path}", params=params)


class PickleStorage(StoragePort):
    PATH_TEMPLATE = "{self.url}/{table}.pickle"
    def __init__(self, url="./db"):
        super().__init__(url)
        self.cache = {}

    async def get(self, table, query=None, **params):
        data = self.cache.get(table)
        if data is None:
            try:
                data = pickle.load(open(self._file(table), "rb"))
            except Exception as why:
                log.warning(why)
                data = {}
            self.cache[table] = data
        if query:
            raise NotImplementedError

        return data

    async def set(self, table, data, merge=True):
        t0 = time.time()
        if merge:
            data0 = self.get(table)
            #data = {** data0, ** data} # TODO: is faster?
            data0.update(data)
            data = data0
            
        path = f"{self.url}/{table}.pickle"
        pickle.dump(data, open(path, "wb"))
        t1 = time.time()
        self.cache[table] = data
        
        print(f"{self.__class__}.set() : elapsed = {t1-t0} seconds")

    async def put(self, table, query=None, **params):
        raise NotImplementedError
        # return requests.get(f"{self.url}{path}", params=params)


class YamlStorage(StoragePort):
    PATH_TEMPLATE = "{self.url}/{table}.yaml"
    
    def __init__(self, url="./db"):
        super().__init__(url)
        self.cache = {}

    async def get(self, table, query=None, **params):
        data = self.cache.get(table)
        if data is None:
            try:
                data = yaml.load(open(self._file(table)), Loader=yaml.Loader)
            except Exception as why:
                log.warning(why)
                data = {}
            self.cache[table] = data
        if query:
            raise NotImplementedError

        return data

    async def set(self, table, data, merge=True):
        t0 = time.time()
        if merge:
            data0 = self.get(table)
            #data = {** data0, ** data} # TODO: is faster?
            data0.update(data)
            data = data0
            
        path = f"{self.url}/{table}.yaml"
        yaml.dump(data, open(path, "w"), Dumper=yaml.Dumper)
        t1 = time.time()
        print(f"{self.__class__}.set() : elapsed = {t1-t0} seconds")

    async def put(self, table, query=None, **params):
        raise NotImplementedError
        # return requests.get(f"{self.url}{path}", params=params)


class SurrealStorage(StoragePort):
    def __init__(self, url="./db", user="root", password="root", ns="test", db="test"):
        #super().__init__(url) # DO NOT CALL BASE CLASS, will corrupt url
        self.url = url
        self.cache = {}
        self.user = user
        self.password = password
        self.ns = ns
        self.db = db
        self.connection = None
        
    async def _connect(self):
        self.connection = Surreal(self.url)
        
        # TODO: use credentials
        await self.connection.connect()
        await self.connection.signin({"user": self.user, "pass": self.password})
        

    async def get(self, table, query=None, **params):
        data = self.cache.get(table)
        if data is None:
            if not self.connection:
                await self._connect()
            try:
                data = yaml.load(open(self._file(table)), Loader=yaml.Loader)
            except Exception as why:
                log.warning(why)
                data = {}
            self.cache[table] = data
        if query:
            raise NotImplementedError
    
        return data

    async def set(self, table, data, merge=True):
        t0 = time.time()
        if merge:
            data0 = self.get(table)
            #data = {** data0, ** data} # TODO: is faster?
            data0.update(data)
            data = data0
            
        if not self.connection:
            await self._connect()
            
        await self.connection.use(self.ns, table)                     
        #await self.connection.query(f"USE DB {table.replace('.', '_')};")
        
        for kind, items  in data.items():
            for id_, item in items.items():
                result = await self.connection.create(
                    kind,
                    item, 
                )        
        t1 = time.time()
        print(f"{self.__class__}.set() : elapsed = {t1-t0} seconds")
        
    async def put(self, table, query=None, **params):
        raise NotImplementedError
        # return requests.get(f"{self.url}{path}", params=params)


class DualStorage(PickleStorage):
    """Storage for debugging and see all data in yaml
    Low performance, but is just for testing
    """

    def __init__(self, url="./db", klass=YamlStorage):
        super().__init__(url)
        self.other = klass(url)

    async def get(self, table, query=None, **params):
        other_path = self.other._file(table)
        other_mtime = None
        mine_path = self._file(table)
        try:
            other_mtime = os.stat(other_path).st_mtime
            mine_mtime = os.stat(mine_path).st_mtime
        except Exception:
            mine_mtime = 0
            
        if other_mtime is not None:
            if other_mtime > mine_mtime:
                data = self.other.get(table, query=query, **params)
                await super().set(table, data, merge=False)
            else:
                data =  await super().get(table, query, **params)
        else:
            data = {}
                                
        return data

    async def set(self, table, data, merge=True):
        """
        other.mtime < mine.mtime
        
        otherwise user has modifier `yaml` file and `pickle` will be updated
        """
        await self.other.set(table, data, merge)
        await super().set(table, data, merge)

    async def put(self, table, query=None, **params):
        await super().put(table, query, **params)
        raise NotImplementedError
        # return requests.get(f"{self.url}{path}", params=params)


Storage = PickleStorage

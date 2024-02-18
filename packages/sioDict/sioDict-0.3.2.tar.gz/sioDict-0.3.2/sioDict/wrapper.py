
import abc
from sioDict.base import SioBaseDict, SioBaseList
import orjson

class SioWrapper(SioBaseDict):
    def __init__(
        self, 
        path : str, 
        *args, 
        reset : bool = False,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.loadMethod = self._load
        self.saveMethod = self._save
        self.clearMethod = self._clear
        self.syncFile(path, reset)
        
    @abc.abstractstaticmethod
    def _load(path : str):
        with open(path, 'rb') as f:
            return orjson.loads(f.read())
    
    @abc.abstractstaticmethod
    def _save(d, path : str):
        with open(path, 'wb') as f:
            f.write(orjson.dumps(d))
    
    @abc.abstractstaticmethod
    def _clear(path : str):
        with open(path, 'w') as f:
            f.write("{}")

class SioList(SioBaseList):
    def __init__(self, path : str, *args, reset : bool = False):
        super().__init__(*args)
        self.loadMethod = SioWrapper._load
        self.saveMethod = SioWrapper._save
        self.clearMethod = self._clear
        self.syncFile(path, reset)

    @abc.abstractstaticmethod
    def _clear(path : str):
        with open(path, 'w') as f:
            f.write("[]")

from sioDict.wrapper import SioWrapper

import toml

class TomlSioDict(SioWrapper):
    @staticmethod
    def _save(d, path : str):
        with open(path, 'w') as f:
            toml.dump(d, f)

    @staticmethod
    def _load(path : str):
        with open(path, 'r') as f:
            return toml.load(f)
        
    @staticmethod
    def _clear(path : str):
        with open(path, 'w') as f:
            f.write("")

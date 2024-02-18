# sio-dict
Super Charged Io Dicts

# Installation
```bash
pip install sioDict
```

# Features
- [x] OneLayerDict, OneLayerList are auto savable dict/list that supports depth 1
- [x] SioList, SioDict supports infinite nesting with customizable `_save`, `_load` and `_clear` io methods
- [x] variants contain prebuilt sioDict implementations
- [x] functions like `getDeep, setDeep, setDeepSimple` are utility functions that can be used for any dict

# Example Usage
```py
from sioDict import SioDict, SioList

d = SioDict(
    "test.json",
    {"a" : 1},
    reset=True
)

d["a"] = {
    "b" : 2
}

# expect test.json =>  {"a": {"b": 2}}
```

# License
MIT

# Acknowledgements
- Peter Wendl 
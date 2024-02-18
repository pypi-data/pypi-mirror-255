

import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from sioDict import SioDict

data = SioDict("tests/testdict.json",reset=True)

data["w", "r"] = {}

w = data["w"]

w["r", "k"] = 1
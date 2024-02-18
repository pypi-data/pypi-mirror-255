import os 
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from sioDict.etc import getDeep, setDeep, setDeepSimple

def test_getdeep():
    d = {
        "a": {
            "b": {
                "c": [
                    1, {
                        "d": 2
                    }
                ]
                
            }
        }
    }
    
    res = getDeep(d, "a", "b", "c", 1, "d")
    assert res == 2

def test_setdeep():
    d = {}

    setDeep(d, "a", "b", "c", 1, "d", 2)

    f = {}
    setDeepSimple(f, "a", "b", "c", 1, "d", 2)

    print(d)
    print(f)
    assert d == {'a': {'b': {'c': {1: {'d': 2}}}}}
    assert f == {'a': {'b': {'c': [{}, {'d': 2}]}}}

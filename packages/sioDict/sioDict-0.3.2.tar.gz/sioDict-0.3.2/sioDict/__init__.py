from sioDict.base import SioBaseDict, SioBaseList

from sioDict.wrapper import SioWrapper, SioList
OrjsonSioDict = SioWrapper

class SioDict(SioWrapper):
    pass

from sioDict.simple import OneLayerDict, OneLayerList

from sioDict.etc import getDeep, setDeep, setDeepSimple, setDefault
import typing

class ExtOptions:
    raiseOnError = 0x01
    returnClosest = 0x02

def getDeep(
    d : dict, 
    *keys, 
    default = None,
    options : int = 0
):
    if len(keys) == 0:
        return d
    if len(keys) == 1:
        return d.get(keys[0], default)
    
    for key in keys[:-1]:
        if (
                key not in d and isinstance(d, dict
            )
            or (
                isinstance(d, list) and key >= len(d)
            )
        ):
            if options & ExtOptions.raiseOnError:
                raise KeyError(key)
            elif options & ExtOptions.returnClosest:
                return default
            return default
        d = d[key]
    
    
    if options & ExtOptions.raiseOnError:
        raise KeyError(keys[-1])
    elif options & ExtOptions.returnClosest:
        return default
    
    return d.get(keys[-1], default)

def iterTypeMapping(
    keys : typing.List[str] = None,
    mapping  : typing.Union[
        type, typing.List[typing.Tuple[typing.Type, int]], typing.Dict[str, typing.Type]
    ] = dict
):
    index = 0
    counter = 0
    while True:
        if index > len(keys) - 1:
            break
        
        if isinstance(mapping, type):
            yield mapping, keys[index]
        elif isinstance(mapping, list) and counter < len(mapping):
            # (dict, 3) (list, 2) yield 3 times dict and 2 times list
            for i in range(mapping[counter][1]):
                yield mapping[counter][0], keys[index]
            counter += 1
        elif isinstance(mapping, dict):
            yield mapping[keys[index]], keys[index]
            
        index += 1

def setDeep(
    d : dict, 
    *keysAndValue,
    expandMapping : typing.Union[
        type, typing.List[typing.Tuple[typing.Type, int]], typing.Dict[str, typing.Type]
    ] = dict
):
    if len(keysAndValue) == 0:
        raise KeyError("no keys passed in")
    
    if len(keysAndValue) == 1:
        raise KeyError("only 1 key passed in, missing value")
    
    if len(keysAndValue) == 2:
        d[keysAndValue[0]] = keysAndValue[1]
        return
    
    target = d
    for stype, key in iterTypeMapping(keysAndValue[:-2], expandMapping):
        if key not in target:
            target[key] = stype()
        target = target[key]
    
    target[keysAndValue[-2]] = keysAndValue[-1]

def setDeepSimple(d, *keysAndValue):
    if len(keysAndValue) < 2:
        raise ValueError("At least one key and one value are required")

    # Navigate through the keys, stopping before the last key to set the value
    target = d
    for i, key in enumerate(keysAndValue[:-2]):  # Iterate until the penultimate item
        next_key = keysAndValue[i+1]  # Look ahead to the next key to determine the required type

        if isinstance(key, int):  # Current key is an integer, so we expect a list at this level
            # Ensure the target is a list and is long enough
            while isinstance(target, dict) and key in target and not isinstance(target[key], list):
                target[key] = [target[key]]  # Convert to list if necessary
            if not isinstance(target, list):
                raise TypeError(f"Expected list at key '{key}' but found a dict.")
            while len(target) <= key:
                target.append({})
            target = target[key]
        else:  # Current key is not an integer, we expect a dict at this level
            if key not in target or not isinstance(target[key], (dict, list)):
                # Initialize the correct type based on the next key
                target[key] = [] if isinstance(next_key, int) else {}
            target = target[key]

    # Set the value for the last key
    final_key = keysAndValue[-2]
    if isinstance(final_key, int):  # Final key is an integer, prepare a list if necessary
        # Ensure the target is a list and is long enough
        if not isinstance(target, list):
            target = [target]  # Convert existing value to list
        while len(target) <= final_key:
            target.append(None)
        target[final_key] = keysAndValue[-1]
    else:  # Final key is not an integer, simply set the value in a dict
        target[final_key] = keysAndValue[-1]
    
def setDefault(
    d : dict,
    *keys,
    default,
    expandMapping : typing.Union[
        type, typing.List[typing.Tuple[typing.Type, int]], typing.Dict[str, typing.Type]
    ] = dict,
    useSimple : bool = False
):
    try:
        getDeep(d, *keys, options=ExtOptions.raiseOnError)
    except KeyError:
        if useSimple:
            setDeepSimple(d, *keys, default)
        else:
            setDeep(d, *keys, expandMapping=expandMapping, default=default)

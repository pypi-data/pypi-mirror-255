from __future__ import annotations
from typing import Iterable, TypeVar

T_Key = TypeVar('T_Key')

def topological_sort(source: Iterable[tuple[T_Key,Iterable[T_Key]]]) -> list[T_Key]:
    """
    Perform a topological sort.

    - `source`: list of `(key, [list of dependancies])` pairs
    - returns a list of keys, with dependancies listed first
    """
    #See: https://stackoverflow.com/a/11564323
    pending = [(key, set(deps)) for key, deps in source] # copy deps so we can modify set in-place       
    emitted = []
    result = []

    while pending:
        next_pending = []
        next_emitted = []

        for entry in pending:
            key, deps = entry
            deps.difference_update(emitted) # remove deps we emitted last pass
            if deps: # still has deps? recheck during next pass
                next_pending.append(entry) 
            else: # no more deps? time to emit
                result.append(key)
                emitted.append(key) # <-- not required, but helps preserve original ordering
                next_emitted.append(key) # remember what we emitted for difference_update() in next pass

        if not next_emitted: # all entries have unmet deps, one of two things is wrong...
            raise ValueError("cyclic or missing dependancy detected: %r" % (next_pending,))
        
        pending = next_pending
        emitted = next_emitted

    return result

import pytest
import copy

from src.fca.api_models import Context, IncLattice
from src.fca.base_models import Concept


def  test_integration(random_big_context):
    O, A, I = random_big_context
    total_instances = len(O)
    deletions = 1
    
    ctx = Context(list(O), list(A), copy.deepcopy(I))
    l = IncLattice(ctx)
    for i in range(1, deletions + 1):
        print("deleting", O[total_instances - i], l.ctx.G, l.ctx.M, l.ctx.I)
        l.delete_instance(O[total_instances - i])
        print("after deleting", l.concepts, l.ctx.G, l.ctx.M, l.ctx.I)
    
    for _ in range(deletions):
        O.pop()
        I.pop()
    
    ctx2 = Context(*random_big_context)
    expected_l = ctx2.get_concepts()

    expected_res = [sort_tuple(c.to_tuple()) for c in expected_l]
    res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def sort_tuple(t):
        t[0].sort()
        t[1].sort()
        return t

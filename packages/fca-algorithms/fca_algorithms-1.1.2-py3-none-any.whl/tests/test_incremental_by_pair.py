import pytest
import copy

from .utils import *

from functools import wraps
from time import time

from src.fca.api_models import IncLattice, Context


def test_add_object_with_attribute():
    p = IncLattice()
    p.add_pair('1', 'a')
    assert p.bottom.hr_O() == ['1']
    assert p.bottom.hr_A() == ['a']
    assert p.top.hr_O() == ['1']
    assert p.top.hr_A() == ['a']
    assert p.top.X == p.bottom.X
    assert p.top.Y == p.bottom.Y


def test_add_object_with_attribute_with_two_objects():
    p = IncLattice()
    p.add_pair('1', 'a')
    p.add_pair('2', 'b')
    assert p.bottom.hr_O() == []
    assert p.bottom.hr_A() == ['a', 'b']
    assert p.top.hr_O() == ['1', '2']
    assert p.top.hr_A() == []
    

def test_add_attribute_with_three_objects():
    p = IncLattice()
    p.add_pair('1', 'a')
    p.add_pair('1', 'b')
    p.add_pair('1', 'c')
    p.add_pair('2', 'c')
    p.add_pair('3', 'c')
    p.add_pair('4', 'a')
    expected_res = [
        ((['1'], ['a', 'b', 'c'])),
        ((['1', '2', '3'], ['c'])),
        ((['1', '2', '3', '4'], [])),
        ((['1', '4'], ['a'])),]
    for i, elem in enumerate(p.concepts):
        assert elem.to_tuple() == expected_res[i]


def  test_update_object():
    p = IncLattice()
    p.add_pair('1', 'a')
    p.add_pair('2', 'b')
    p.add_pair('3', 'a')
    p.add_pair('4', 'b')
    p.add_pair('5', 'a')
    p.add_pair('1', 'c')
    p.add_pair('3', 'd')
    p.add_pair('6', 'e')
    p.add_pair('2', 'a')

    ctx = Context(['1', '2', '3', '4', '5', '6'], ['a', 'b', 'c', 'd', 'e',],
                [[1, 0, 1, 0, 0], [1, 1, 0, 0, 0], [1, 0, 0, 1, 0], [0, 1, 0, 0, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 1]])

    l = ctx.get_lattice()
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert res == expected_res
    

def  test_update_object_2():
    # from fca.api_models import IncLattice


    some_G = ["4", "5", "1", "3", "6", "2"]
    some_M = ["a", "b", "c", "d", "e"]
    some_I = [
        [0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 1, 0, 0],
        [1, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0],
    ]
    some_context = Context(some_G, some_M, some_I)

    some_G2 = list(some_G)
    some_M2 = list(some_M)
    some_I2 = copy.deepcopy(some_I)
    some_I2[0][3] = 1
    # some_G2.remove("4")
    # del some_I2[0]
    some_context2 = Context(some_G2, some_M2, some_I2)


    p2 = IncLattice(some_context)
    p2.add_pair("4", "d")
    p = IncLattice()
    p.add_pair('1', 'a')
    p.add_pair('2', 'b')
    p.add_pair('3', 'a')
    p.add_pair('4', 'b')
    p.add_pair('5', 'a')
    p.add_pair('1', 'c')
    p.add_pair('3', 'd')
    p.add_pair('6', 'e')
    p.add_pair('2', 'a')
    p.add_pair("4", "d")
    # p.add_pair('6', 'b')
    # p.add_pair('6', 'd')
    
    # ctx = Context(['1', '2', '3', '4', '5', '6'], ['a', 'b', 'c', 'd', 'e',],
    #             [[1, 0, 1, 0, 0], [1, 1, 0, 0, 0], [1, 0, 0, 1, 0], [0, 1, 0, 1, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 1]])

    # l = ctx.get_concepts()
    # expected_res = [sort_tuple(c.to_tuple()) for c in l]
    # res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    # expected_res.sort()
    # res.sort()
    # assert res == expected_res

    assert sorted(p.ctx.O) == sorted(p2.ctx.O)
    assert sorted(p.ctx.A) == sorted(p2.ctx.A)
    assert sorted(p.ctx.I) == sorted(p2.ctx.I)
    l = p2
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert res == expected_res

    expected_concepts = l.concepts 
    expected_concepts.sort(key=concept_key)
    concepts_result = list(p.concepts)
    concepts_result.sort(key=concept_key)
    children_per_concept_res = [[sort_tuple(t.to_tuple()) for t in sorted(c.children, key=concept_key)] for c in concepts_result]
    children_per_concept_expected = [[sort_tuple(t.to_tuple()) for t in sorted(c.children, key=concept_key)] for c in expected_concepts]
    parents_per_concept_res = [[sort_tuple(t.to_tuple()) for t in sorted(c.parents, key=concept_key)] for c in concepts_result]
    parents_per_concept_expected = [[sort_tuple(t.to_tuple()) for t in sorted(c.parents, key=concept_key)] for c in expected_concepts]
    for i in range(len(concepts_result)):
        assert children_per_concept_res[i] == children_per_concept_expected[i], \
               f"{concepts_result[i]} should have children: {children_per_concept_expected[i]}\n" \
               f"but instead it has {children_per_concept_res[i]}"
        assert parents_per_concept_res[i] == parents_per_concept_expected[i], \
               f"{concepts_result[i]} should have parents: {parents_per_concept_expected[i]}\n" \
               f"but instead it has {parents_per_concept_res[i]}"

    # p.add_intent("4", [1, 3])
    # ctx = Context(['1', '2', '3', '4', '5', '6'], ['a', 'b', 'c', 'd', 'e',],
    #             [[1, 0, 1, 0, 0], [1, 1, 0, 0, 0], [1, 0, 0, 1, 0], [0, 1, 0, 1, 0], [1, 0, 0, 0, 0], [0, 0, 0, 0, 1]])
    # l = ctx.get_concepts()
    # expected_res = [sort_tuple(c.to_tuple()) for c in l]
    # res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    # expected_res.sort()
    # res.sort()
    # assert res == expected_res


def  test_all_complete_context():
    # from fca.api_models import IncLattice
    p = IncLattice()
    p.add_pair('1', 'a')
    p.add_pair('1', 'b')
    p.add_pair('2', 'a')
    p.add_pair('2', 'b')
    
    ctx = Context(['1', '2',], ['a', 'b',],
                [[1, 1,], [1, 1,],])

    l = ctx.get_lattice()
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert res == expected_res


def  test_repeated_row_context():
    # from fca.api_models import IncLattice
    p = IncLattice()
    p.add_pair('1', 'a')
    p.add_pair('1', 'c')
    p.add_pair('2', 'a')
    p.add_pair('2', 'b')
    p.add_pair('2', 'c')
    p.add_pair('3', 'a')
    p.add_pair('3', 'b')
    p.add_pair('3', 'c')

    # ctx = Context(['1', '2', '3',], ['a', 'b', 'c',],
    #             [[1, 0, 1,], [1, 1, 1,], [1, 1, 1]])
    
    ctx = Context(['1', '2', '3'], ['a', 'b', 'c',], [[1, 0, 1,], [1, 1, 1,], [1, 1, 1,]])

    l = ctx.get_lattice()
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert res == expected_res


def test_all_true_row(all_true_row_context):
    # from fca.api_models import IncLattice
    ctx = Context(*all_true_row_context)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()
    def sort_tuple(t):
        t[0].sort()
        t[1].sort()
        return t
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res



def test_diagonal_context(diagonal_context):
    # from fca.api_models import IncLattice
    ctx = Context(*diagonal_context)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()
                
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res

        

def test_4x4_context(bigger_context):
    # from fca.api_models import IncLattice
    ctx = Context(*bigger_context)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def test_4x4_context_2(context_4x4_2):
    # from fca.api_models import IncLattice
    ctx = Context(*context_4x4_2)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res

def test_4x4_context_3(context_4x4_3):
    # from fca.api_models import IncLattice
    ctx = Context(*context_4x4_3)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def test_4x4_context_4(context_4x4_4):
    # from fca.api_models import IncLattice
    ctx = Context(*context_4x4_4)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def test_4x4_context_5(context_4x4_5):
    # from fca.api_models import IncLattice
    ctx = Context(*context_4x4_5)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def test_4x4_context_6(context_4x4_6):
    # from fca.api_models import IncLattice
    ctx = Context(*context_4x4_6)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def test_4x4_context_7(context_4x4_7):
    # from fca.api_models import IncLattice
    ctx = Context(*context_4x4_7)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res

def test_5x5_context_1(context_5x5_1):
    # from fca.api_models import IncLattice
    ctx = Context(*context_5x5_1)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def  test_integration(big_context):
    # from fca.api_models import IncLattice
    ctx = Context(*big_context)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_lattice()
    expected_res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def  test_integration_2(random_big_context):
    # from fca.api_models import IncLattice
    ctx = Context(*random_big_context)

    p = IncLattice()
    for i, g in enumerate(ctx.O):
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                p.add_pair(g, m)
    
    l = ctx.get_concepts()

    expected_res = [sort_tuple(c.to_tuple()) for c in l]
    res = [sort_tuple(c.to_tuple()) for c in p.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res


def  test_delete_instance():
    # from fca.api_models import IncLattice
    ctx = Context(['t1', 't2', 't3'], ['competitive', 'expensive', 'adults', 'kids'], [[1, 1, 1, 0], [0, 1, 1, 1], [0, 0, 0, 1]])
    
    l = IncLattice(ctx)
    l.delete_instance('t3')


    ctx2 = Context(['t1', 't2',], ['competitive', 'expensive', 'adults', 'kids'], [[1, 1, 1, 0], [0, 1, 1, 1]])
    l2 = ctx2.get_lattice()

    expected_res = [sort_tuple(c.to_tuple()) for c in l2.concepts]
    res = [sort_tuple(c.to_tuple()) for c in l.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res



def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result
    return wrap


@timing
def add_pair(p, g, m):
    p.add_pair(g, m)


def sort_tuple(t):
        t[0].sort()
        t[1].sort()
        return t

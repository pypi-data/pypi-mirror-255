import pytest
import random

from src.fca.rca.models import Relation


@pytest.fixture
def create_objects_and_attributes():
    O = ['Tg05', 'Tg05FX', 'Flxtra', 'Hxr']
    A = ['Effect', 'Power', 'Control', 'Short']
    I = [
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0],
        [1, 0, 1, 0],
    ]
    return O, A, I


@pytest.fixture
def create_objects_and_attributes_2():
    O = ['1', '2', '3', '4', '5']
    A = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
    I = [
        [1, 0, 1, 0, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 1, 0, 1],
        [0, 1, 1, 0, 0, 1, 0, 1, 0],
        [0, 1, 0, 0, 1, 0, 1, 0, 0],
    ]
    return O, A, I


@pytest.fixture
def create_relation_between_0_and_1():
    I = [
        # object in index 0 is related with 0 and also with 2 of the other
        # context
        set([0, 2]),
        # object in index 1 is related with 0, 2 and 4 of the other context
        set([0, 2, 4]),
        set([0, 3]),
        set([1, 2]),
    ]
    return Relation(I, [0, 1])


@pytest.fixture
def all_true_row_context():
    I = [
        [False, True, False,],
        [True, True, True,],
        [True, False, True,],
        ]
    O = ['o' + str(i) for i in range(3)]
    A = ['a' + str(i) for i in range(3)]
    return O, A, I


@pytest.fixture
def diagonal_context():
    I = [
        [False, True, True,],
        [True, False, True,],
        [True, True, True,],
        ]
    O = ['o' + str(i) for i in range(3)]
    A = ['a' + str(i) for i in range(3)]
    return O, A, I


@pytest.fixture
def bigger_context():
    O, A, I = (['o0', 'o1', 'o2', 'o3'],
    ['a0', 'a1', 'a2', 'a3'],
    [[True, True, False, True], [True, False, True, False], [False, True, False, False], [False, True, True, True]])
    return O, A, I


@pytest.fixture
def context_4x4_2():
    return (['o0', 'o1', 'o2', 'o3'], ['a0', 'a1', 'a2', 'a3'],
    [[False, True, False, True], [True, True, False, True], [True, True, True, False], [True, False, True, True]])


@pytest.fixture
def big_context():
    I = [
        [False, False, False, False, True,],
        [True, True, False, True, False,],
        [True, False, False, False, True,],
        [False, True, False, True, False,],
        [True, False, True, False, True,],
        ]
    O = ['o' + str(i) for i in range(5)]
    A = ['a' + str(i) for i in range(5)]
    return O, A, I


@pytest.fixture
def context_4x4_3():
    return (['o0', 'o1', 'o2', 'o3'], ['a0', 'a1', 'a2', 'a3'],
    [[False, True, True, False], [False, True, True, False], [True, True, False, True], [True, True, True, False]])


@pytest.fixture
def context_4x4_4():
    return (['o0', 'o1', 'o2', 'o3'], ['a0', 'a1', 'a2', 'a3'],
    [[False, False, True, True], [True, False, True, True], [True, False, False, True], [True, True, True, False]])

@pytest.fixture
def context_4x4_5():
    return (['o0', 'o1', 'o2', 'o3'], ['a0', 'a1', 'a2', 'a3'],
    [[True, False, False, True], [False, True, True, False], [True, False, True, True], [True, False, True, True]])


@pytest.fixture
def context_4x4_6():
    return (['o0', 'o1', 'o2', 'o3'], ['a0', 'a1', 'a2', 'a3'],
    [[False, True, True, True], [False, True, False, True], [True, True, True, True], [False, False, True, True]])


@pytest.fixture
def context_4x4_7():
    return (['o0', 'o1', 'o2', 'o3'], ['a0', 'a1', 'a2', 'a3'],
    [[True, False, False, False], [False, True, True, True], [True, True, False, True], [True, True, False, True]])


@pytest.fixture
def context_5x5_1():
    return (['o0', 'o1', 'o2', 'o3', 'o4'], ['a0', 'a1', 'a2', 'a3', 'a4'],
    [[True, True, False, False, False], [True, False, True, False, True], [True, False, True, True, True], [False, True, True, True, True], [True, True, True, True, False]])


@pytest.fixture
def big_context_2():
    I = [
        [False, False, False, False, True, True, True, False, True, True, True, False, True, True, False, True, False, True, True, True, True, False, False, False, False],
        [True, True, False, True, False, True, False, False, True, True, True, False, True, False, True, False, True, False, False, False, True, False, False, False, False],
        [True, False, False, False, True, True, False, True, True, True, True, False, False, True, False, False, True, False, False, True, False, True, True, True, True],
        [False, True, False, True, False, True, False, False, True, True, True, False, True, True, True, True, False, False, True, False, False, False, False, False, False],
        [True, False, True, False, True, False, True, False, True, True, True, False, False, True, True, False, True, False, True, True, True, True, True, False, False],
        [True, True, True, False, True, False, False, False, True, False, True, True, False, True, False, False, True, True, True, True, False, True, True, False, True],
        [True, False, True, False, False, True, False, False, False, False, False, False, True, True, True, False, True, False, False, False, False, True, False, True, False],
        [True, True, True, False, True, True, True, False, True, True, True, True, True, False, True, True, False, False, False, False, False, True, True, True, True],
        [False, False, True, False, False, False, False, False, False, True, True, True, False, False, True, True, False, True, False, False, True, False, False, True, False],
        [True, True, False, False, True, False, False, True, True, False, False, False, True, True, False, False, True, True, True, False, False, True, False, True, False],
        [False, False, False, True, False, True, True, False, True, True, True, False, True, True, False, True, True, False, True, False, True, True, False, False, True],
        [True, False, True, False, True, True, True, False, False, False, False, False, True, False, True, True, False, False, False, True, False, False, True, False, True],
        [False, True, False, True, False, False, False, False, True, False, False, True, False, True, False, False, False, False, True, False, True, True, False, False, True],
        [False, True, True, True, False, True, True, False, False, True, True, True, False, True, True, False, False, False, False, True, False, True, True, True, False],
        [True, True, True, True, True, False, True, False, False, False, False, True, True, False, True, False, False, False, False, False, True, True, False, True, True],
        [False, False, True, False, True, False, True, True, False, True, True, False, True, False, True, False, False, True, True, False, False, False, False, True, True],
        [True, False, False, False, False, False, False, False, True, False, False, False, False, True, False, True, False, True, True, False, True, False, False, False, False],
        [False, False, False, False, True, True, True, False, False, True, False, False, False, True, False, True, False, False, False, False, True, False, True, False, True],
        [False, True, False, False, True, False, True, False, True, True, False, True, True, True, False, False, False, True, False, False, True, True, True, True, False],
        [False, True, False, False, True, False, True, False, False, False, False, False, True, True, True, True, False, False, True, True, True, False, False, False, True],
        [False, False, True, False, True, True, False, True, True, False, False, False, True, False, True, False, True, False, False, True, True, False, True, True, True],
        [True, True, False, False, False, True, False, False, True, True, True, False, False, True, True, True, False, False, False, True, True, True, False, False, True],
        [True, False, True, True, True, True, True, True, False, True, True, True, True, False, False, True, True, False, False, True, True, False, False, False, True],
        [True, True, True, True, False, True, True, True, False, False, True, True, True, False, False, True, False, True, True, True, False, False, False, False, False],
        [True, True, True, True, False, False, True, False, True, False, False, True, False, False, True, True, False, True, False, True, True, True, True, True, True]]
    O = ['o' + str(i) for i in range(25)]
    A = ['a' + str(i) for i in range(25)]
    return O, A, I


@pytest.fixture
def random_big_context():
    size = 6
    I = []
    for i in range(size):
        I.append([])
        for j in range(size):
            I[i].append(random.choice([True, False]))
    
    for l in I:
        if not any(l):
            l[random.randrange(size)] = True
    
    for j in range(size):
        column = [I[i][j] for i in range(size)]
        if not any(column):
            I[random.randrange(size)][j] = True

    O = ['o' + str(i) for i in range(size)]
    A = ['a' + str(i) for i in range(size)]
    return O, A, I

# -*- coding: utf-8 -*-
"""Base representation of the basic classes of FCA

Ideally, with the exception of :class:`Concept`, these classes are only internal, and it should
not be necessary to use them.
"""


from typing import List


class Context:
    """Base representation of a formal context"""
    def __init__(self, O, A, I: List[List[int]]):
        """
        Args:
            O (List[str]): a list of objects. `len(O) = n`
            A (List[str]): a list of attributes. `len(A) = m`
            I (List[List[int]]): a `n m` incidence matrix, beign `I[i][j] = 1`
                                 if object `i` has the attribute `j`, `0 <= i <= n`, `0 <= j <= m`
        """
        self.O: List = O
        self.A: List = A
        self.I: List = I

    def derivative(self, Y, is_attr: bool = True):
        """
        Args:
            Y (List[int]): A subset indices of `self.A` or `self.O`
            is_attr (bool): Whether `Y \\subseteq A` or `Y \\subseteq O`
        """
        return self._derivative_attr(Y) if is_attr else self._derivative_obj(Y)

    def _derivative_attr(self, Y):
        res = set()
        for attr in Y:
            attr_idx = self.A.index(attr)
            for obj in self.O:
                obj_idx = self.O.index(obj)
                if self.I[obj_idx][attr_idx]:
                    res.add(obj)
        return list(res)

    def _derivative_obj(self, Objs):
        res = set()
        for obj in Objs:
            obj_idx = self.O.index(obj)
            for attr in self.A:
                attr_idx = self.A.index(attr)
                if self.I[obj_idx][attr_idx]:
                    res.add(attr)
        return list(res)

    def __repr__(self):
        return f'O: {self.O},\n' \
               f'A: {self.A},\n' \
               f'I: {self.I}'


class Concept:
    """Base representation of a formal concept"""
    def __init__(self, context: Context, O, A, parents=None, children=None):
        if children is None:
            children = []

        if parents is None:
            parents = []

        self.context = context
        self.O = O
        self.A = A
        # this is not supposed to change, so it's a frozenset
        self._set_O = frozenset(O)
        self.parents = parents
        self.children = children
    

    @property
    def X(self):
        return self.O
    
    @property
    def Y(self):
        return self.A

    def in_extent(self, o: int) -> bool:
        """Whether the object o is in its extent"""
        return o in self._set_O  # O(1) amortised

    def add_child(self, concept):
        self.children.append(concept)
        concept.parents.append(self)
    

    def remove_child(self, concept):
        try:
            self.children.remove(concept)
            concept.parents.remove(self)
        except ValueError:
            # print("error removing link between", self, "and", concept)
            pass


    def __repr__(self):
        obj_str = ("{{ {0} }}".format(', '.join([str(self.context.O[i]) for i in self.O])))
        atr_str = ("{{ {0} }}".format(', '.join([str(self.context.A[i]) for i in self.A])))
        return f'({obj_str}, {atr_str})'

    def to_tuple(self):
        """
        Returns:
            A tuple consisting of `(obj, attr)` where obj and attr are the lists of corresponding strings
        """
        return [self.context.O[i]
                for i in self.O], [self.context.A[i] for i in self.A]

    def hr_O(self):
        """
        Returns:
            The list of the corresponding object strings
        """
        return [self.context.O[i] for i in self.O]

    def hr_A(self):
        """
        Returns:
            The list of the corresponding attribute strings
        """
        return [self.context.A[i] for i in self.A]

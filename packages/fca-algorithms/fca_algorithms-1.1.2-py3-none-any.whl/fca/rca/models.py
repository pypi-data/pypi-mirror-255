"""
Propositionalization (P18N) operators
"""
from abc import ABC, abstractmethod

from ..utils.utils import to_subscript


class Propositionalization(ABC):
    @abstractmethod
    def __call__(self, object, relation, concepts) -> bool:
        return False


class Exists(Propositionalization):
    def __call__(self, obj, relation, concepts) -> bool:
        return self._exists(obj, relation, concepts, 0)

    def _exists(self, obj, relation, concepts, i):
        if i == len(concepts) - 1:
            for o in concepts[i].O:
                if o in relation[obj]:
                    return True
        else:
            for o in concepts[i].O:
                if self._exists(o, relation[obj], concepts, i + 1):
                    return True
        return False

    def __repr__(self):
        return '∃'


class Forall(Propositionalization):
    def __call__(self, obj, relation, concepts) -> bool:
        return self._forall(obj, relation, concepts, 0)

    def _forall(self, obj, relation, concepts, i):
        if i == len(concepts) - 1:
            for o in concepts[i].O:
                if o not in relation[obj]:
                    return False
        else:
            for o in concepts[i].O:
                if not self._forall(o, relation[obj], concepts, i + 1):
                    return False
        return True

    def __repr__(self):
        return '∀'


class Relation(list):
    def __init__(self, array, indexes):
        super().__init__(array)
        self.indexes = indexes

    def context_index_from(self):
        return self.indexes[0]

    def context_indexes_to(self):
        return self.indexes[1:]

    def arity(self):
        return len(self.indexes)

    def __repr__(self):
        return f"R{'₋'.join([to_subscript(i) for i in self.indexes])}"

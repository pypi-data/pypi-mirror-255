# -*- coding: utf-8 -*-
"""Interface with the basic classes to be used in the entire `fca` module."""

import csv

from typing import List, Union, Optional
from collections import deque, UserString
from fca_algorithms_cpp import LatticeCpp, ContextCpp, ConceptCpp

from .base_models import Context as Ctx, Concept
from .get_lattice import FCASolver, Inclose
from .utils.utils import (
    to_subscript,
    insert_ordered,
    insert_ordered_unique,
    is_in,
    remove_if_exists,
)
from .plot.plot import plot_from_hasse
from .border_hasse import calculate_hasse


class RelationalAttribute(UserString):
    def __init__(self, p, relation=None, concepts=None):
        """
        :param p: the p18n operator or a string, in which case the relation and concepts are expected to be None.
                  This is mainly to maintain the idea of string[:2] in which another string is expected as a return.
        :param relation: the relation instance
        :param concepts: a list of tuples (lattice_id, concept_id, concept)
        """
        if isinstance(p, str):
            super().__init__(p)
        else:
            value = f"{p}{relation} : {self._concepts_subscripts(concepts)}"
            self.concepts = concepts
            super().__init__(value)

    def _concepts_subscripts(self, combination):
        return ",".join(
            [
                f"C{to_subscript(lattice_idx)}₋{to_subscript(c_idx)}"
                for lattice_idx, c_idx, _ in combination
            ]
        )


class Context(Ctx):
    """The representation of a formal context"""

    def __init__(self, O, A, I, solver: FCASolver = None):
        """
        Args:
            O (List[str]): list of object names
            A (List[str]): list of attribute names
            I (List[List[int]]) incidence matrix (`1` and `0` or `True` and `False` work)
            solver (FCASolver): the solver that should know how to calculate concepts.
        """
        super().__init__(O, A, I)

        if solver is None:
            solver = NonIncrementalSolver()

        self.solver = solver
        self.iteration = 0

        # for each relation, we know what are the attributes already added
        self._relational_attributes = {}

        # FIXME: The ideal would be to cache the last_lattice
        #        and also calculate them from the point they were already calculated
        #        * is that possible not to repeat calculations?
        #        * if not, can we bound the amount of calculations that ought to be repeated?
        self._last_lattice = None

    @staticmethod
    def from_csv(filename, format_name="one_line_per_attribute"):
        """
        Args:
            filename (str): a string representing the path pointing to the file
            format_name (str): one_line_per_attribute | table
        Returns:
            A :class:`Context`
        """
        from .scripts.import_utils import import_context  # to avoid double dependency

        return import_context(filename, format_name)

    def get_concepts(self):
        """
        Returns:
            A List[:class:`Concept`]
        """
        return self.solver.get_concepts(self)

    def get_lattice(self):
        """
        Returns:
            A :class:`Lattice`"""
        self._last_lattice = self.solver.get_lattice(self)
        return self._last_lattice

    def get_association_rules(self, **kwargs):
        """
        Keyword Args:
            min_support=0.5 (float): a float between 0 and 1
            min_confidence=1 (float): a float between 0 and 1
        Yields:
            association rules with
                - Base Item
                - Appended Item
                - Support
                - Confidence
                - Lift
            see (https://pypi.org/project/apyori/)
        """
        return self.solver.get_association_rules(self, **kwargs)

    def generate_association_rules(self, filename, **kwargs):
        """
        Keyword Args:
            filename (str): a str representing where to save the file. It must be csv
            min_support=0.5 (float): a float between 0 and 1
            min_confidence=1 (float): a float between 0 and 1
        Yields:
            association rules with
                - Base Item
                - Appended Item
                - Support
                - Confidence
                - Lift
            see (https://pypi.org/project/apyori/)
        """
        return self.solver.generate_association_rules(self, filename=filename, **kwargs)

    def graduate(self, relation, p, lattices):
        """
        Applies graduation. Extends the formal context with more attributes
        with the relation `relation`, using the p18n operator, against the lattices `lattices` (a list of lattice, lattice_idx)
        """
        for combination in self._tuple_iterator(lattices, 0):
            key = RelationalAttribute(p, relation, combination)
            if key not in self._relational_attributes:
                self.A.append(key)
                self._relational_attributes[key] = (
                    len(self.A) - 1
                )  # adding the idx of the attribute

            attribute_idx = self._relational_attributes[key]
            have_to_add_column = attribute_idx > len(self.I[0]) - 1
            for o, relations in enumerate(self.I):
                has_attribute = p(
                    o, relation, [concept for _, _, concept in combination]
                )
                if have_to_add_column:
                    relations.append(has_attribute)
                else:
                    relations[attribute_idx] = has_attribute

        self.iteration += 1

    def to_csv(self, filename: str):
        """
        Args
            filename (str): the name of the csv to be created

        Creates a csv with name `csv` with one row `g,m` for each object `g` having an attribute `m`
        """
        if not filename.endswith(".csv"):
            filename = f"{filename}.csv"

        with open(filename, "w") as f:
            writer = csv.writer(f)
            for i, g in enumerate(self.O):
                for j, m in enumerate(self.A):
                    if self.I[i][j]:
                        writer.writerow([g, m])

    def _tuple_iterator(self, lattices, i):
        current_lattice_idx = lattices[i][0]
        current_lattice = lattices[i][1]
        if i == len(lattices) - 1:
            for c_idx, concept in enumerate(current_lattice.concepts):
                yield deque([(current_lattice_idx, c_idx, concept)])
        else:
            for c_idx, concept in enumerate(current_lattice.concepts):
                for combination in self._tuple_iterator(lattices, i + 1):
                    combination.appendleft((current_lattice_idx, c_idx, concept))
                    yield combination


class Lattice:
    """Representation of a lattice with all the concepts and the hasse diagram"""

    def __init__(self, hasse, concepts, from_iteration=None):
        self.hasse = hasse
        self._concepts = concepts
        self.ctx = concepts[-1].context
        self._top = None
        self._bottom = None

        self._inverted_hasse = None
        for c in concepts:
            c.children.clear()
            c.parents.clear()
        for i, c in enumerate(concepts):
            if len(c.O) == len(self.ctx.O):
                self._top = c
            if len(c.A) == len(self.ctx.A):
                self._bottom = c

            for j in self.inverted_hasse[i]:
                c.add_child(self.get_concept(j))

    def isomorph(self, other_lattice):
        """
        This method needs the two lattices to have the concepts ordered in the same way, othetwise it'll fail
        - Complexity: `O(|self.concepts|), \\omega(1)`
        """
        if len(self.concepts) != len(other_lattice.concepts):
            return False

        for i, concept in enumerate(self.concepts):
            if len(concept.O) != len(other_lattice.concepts[i].O) or len(
                concept.A
            ) != len(other_lattice.concepts[i].A):
                return False
        return True

    @property
    def bottom(self) -> Concept:
        return self._bottom

    @property
    def top(self) -> Concept:
        return self._top

    @property
    def inverted_hasse(self):
        """The inverse of the hasse digraph"""
        if self._inverted_hasse is None:
            self._calculate_inverted_hasse()
        return self._inverted_hasse

    @property
    def concepts(self):
        return self._concepts

    def get_concept(self, i):
        return self.concepts[i]

    def plot(self, **kwargs):
        """
        Keyword Args:
            show_plot (bool): Whether to show the plot or not.
            save_plot (str): The path where to save the plot. If None, the plot wont be saved.
            ax (Axes | List[Axes]): to reuse axes from another plot.
            fig (Figure): the figure where to draw the plot.
            print_latex (bool): Whether to print the latex code of the plot in the standard output
            instance is destructed.

        Returns:
            (fig, ax, diameter)
        """
        concept_id = dict()
        for i, c in enumerate(self.concepts):
            concept_id[hash(c)] = i

        return plot_from_hasse(
            [[concept_id[hash(c)] for c in t.children] for t in self.concepts],
            self.concepts,
            amount_of_objects=len(self.ctx.O),
            amount_of_attributes=len(self.ctx.A),
            **kwargs,
        )

    def graph_str_repr(self):
        """String representation of the graph"""
        return self._graph_repr(0)

    def __repr__(self):
        return str(self.concepts)

    def _graph_repr(self, i):
        str_so_far = str(self.concepts[i])
        if len(self.inverted_hasse[i]) > 0:
            str_so_far += "<"
            for j in self.inverted_hasse[i]:
                str_so_far += self._graph_repr(j)
            str_so_far += ">"
        return str_so_far

    def _calculate_inverted_hasse(self):
        inv_hasse = []
        for _ in range(len(self.hasse)):
            inv_hasse.append([])

        for i, neighbours in enumerate(self.hasse):
            for j in neighbours:
                inv_hasse[j].append(i)

        self._inverted_hasse = inv_hasse

    def _set_link(self, concept1, concept2):
        # this also sets concept1 as a parent of concept2
        # O(1)
        # if concept1 != concept2 and concept2 not in concept1.children:
        concept1.add_child(concept2)

    def _remove_link(self, concept1, concept2):
        concept1.remove_child(concept2)

    def _remove_node(self, concept):
        for c in concept.parents:
            c.children.remove(concept)

        for c in concept.children:
            c.parents.remove(concept)

        self.concepts.remove(concept)

    def _get_maximal_E_concept(
        self, extent, generator_concept, common_attributes=None
    ):  # O(nm² log m)
        extent_set = set(extent)
        children_is_maximal = True
        while children_is_maximal:
            children_is_maximal = False
            children = self._get_children(generator_concept)
            for child in children:
                if (
                    common_attributes is not None
                    and len(common_attributes[hash(child)]) == len(extent)
                ) or extent_set.issubset(set(child.O)):
                    generator_concept = child
                    children_is_maximal = True
                    break

        return generator_concept

    def _get_maximal_I_concept(
        self, intent, generator_concept, common_objects=None
    ):  # O(mn² log n)
        intent_set = set(intent)  # O(n)
        parent_is_maximal = True
        while parent_is_maximal:  # O(n) or O(max(|m'|))
            parent_is_maximal = False
            parents = self._get_parents(generator_concept)
            for parent in parents:  # O(m)
                if (
                    common_objects is not None
                    and len(common_objects[hash(parent)]) == len(intent)
                ) or intent_set.issubset(
                    set(parent.A)
                ):  # O(n log n)
                    generator_concept = parent
                    parent_is_maximal = True
                    break

        return generator_concept

    def _get_parents(self, concept):
        return concept.parents

    def _get_children(self, concept):
        return concept.children

    def _get_common_attributes(self, intent):
        common_attributes = []
        for idx in range(len(self._lat)):
            elem = self._lat[idx]
            c = elem[0]
            common_elements = []
            for i in intent:
                if is_in(i, c.A)[0]:
                    common_elements.append(i)

            common_attributes.append(common_elements)

        return common_attributes

    def _get_intent(self, g: str, ignore_attr: str = None):
        g_idx = self._object_idx[g]
        m_idx = self._attribute_idx.get(ignore_attr)
        return [
            j for j in range(len(self.ctx.A)) if j != m_idx and self.ctx.I[g_idx][j]
        ]

    def _get_extent(self, m: str, ignore_obj: str = None):
        m_idx = self._attribute_idx[m]
        g_idx = self._object_idx.get(ignore_obj)
        return [
            i for i in range(len(self.ctx.O)) if i != g_idx and self.ctx.I[i][m_idx]
        ]


class IncLattice:
    """Incremenal Lattice that can receive objects on the fly.

    Its purpose is to be able to receive objects and update only the minimal parts of it
    each update takes `O(|G|²|M||L|)` where L is the Lattice we have so far, and G are the objects so far.
    """

    def __init__(self, ctx_or_attributes: Optional[Union[List[str], Context]] = None):
        """
        Args:
            ctx_or_attributes (List[str] | Context): The list of attributes the Lattice will have or a Context.
        Example:
            .. code-block:: python

                L1 = IncLattice()
                L2 = IncLattice(['a', 'b', 'c'])
                L3 = IncLattice(Context(['1', '2'], ['a', 'b', 'c'], [[1, 0, 0], [0, 1, 1]]))
        """
        if ctx_or_attributes is None:
            self.ctx = ContextCpp([], [], [])
        elif isinstance(ctx_or_attributes, list):
            self.ctx = ContextCpp([], ctx_or_attributes, [])
        else:
            self.ctx = ContextCpp(
                [str(o) for o in ctx_or_attributes.O],
                [str(a) for a in ctx_or_attributes.A],
                [[int(i) for i in row] for row in ctx_or_attributes.I],
            )
        self._lat_cpp = LatticeCpp(self.ctx)

    @staticmethod
    def copy(l):
        new_l = IncLattice()
        new_l._lat_cpp = LatticeCpp.copy(l._lat_cpp)
        new_l.ctx = new_l._lat_cpp.ctx
        return new_l

    @property
    def concepts(self):
        return self._lat_cpp.concepts

    @property
    def hasse(self):
        concept_id = dict()
        for i, c in enumerate(self._lat_cpp.concepts):
            concept_id[c] = i

        return [[concept_id[c] for c in t.children] for t in self._lat_cpp.concepts]

    @property
    def bottom(self):
        return self._lat_cpp.get_bottom()

    @property
    def top(self):
        return self._lat_cpp.get_top()

    def isomorph(self, other_lattice):
        """
        This method needs the two lattices to have the concepts ordered in the same way, othetwise it'll fail
        - Complexity: `O(|self.concepts|), \\omega(1)`
        """
        if len(self.concepts) != len(other_lattice.concepts):
            return False

        for i, concept in enumerate(self.concepts):
            if len(concept.O) != len(other_lattice.concepts[i].O) or len(
                concept.A
            ) != len(other_lattice.concepts[i].A):
                return False
        return True

    def merge_concepts(self, other):
        return self._lat_cpp.merge_concepts(other._lat_cpp).concepts

    def add_intent(self, object_name: str, intent: List[int]):
        """
        Args:
            object_name (str): the name of the object being added.
            intent (List[int]): The list of attribute indices the object has.

        Example:
            .. code-block:: python

                L.add_intent('o1', [1, 3, 6])
        """
        self._lat_cpp.add_intent(object_name, intent)

    def delete_instance(self, object_name: str):
        """
        Args:
            object_name (str): the name of an object to be deleted.

        Example:
            .. code-block:: python

                L.delete_instance('o1')
        """
        self._lat_cpp.delete_instance(object_name)

    def add_attribute(self, attr_name: str):
        return self._lat_cpp.add_attribute(attr_name)

    def add_object(self, object_name: str):
        return self._lat_cpp.add_object(object_name)

    def add_pair(self, object_name: str, attr_name: str):
        """
        Args:
            object_name (str): the name of an object.
            attr_name (str): the name of an attribute corresponding to that object.

        Example:
            .. code-block:: python

                L.add_pair('o1', 'a2')
        """
        self._lat_cpp.add_pair(object_name, attr_name)

    def get_concept(self, i: int) -> ConceptCpp:
        """
        Args:
            i (int): index of the concept to be returned
        Returns:
            :class:`ConceptCpp` in `i`-th position
        """
        return self._lat_cpp.get_concept(i)

    def plot(self, **kwargs):
        """
        Keyword Args:
            show_plot (bool): Whether to show the plot or not.
            save_plot (str): The path where to save the plot. If None, the plot wont be saved.
            ax (Axes | List[Axes]): to reuse axes from another plot.
            fig (Figure): the figure where to draw the plot.
            print_latex (bool): Whether to print the latex code of the plot in the standard output
            instance is destructed.

        Returns:
            (fig, ax, diameter)
        """
        concept_id = dict()
        for i, c in enumerate(self._lat_cpp.concepts):
            concept_id[c] = i

        return plot_from_hasse(
            [[concept_id[c] for c in t.children] for t in self._lat_cpp.concepts],
            [
                Concept(self.ctx, t.X, t.Y, children=t.children, parents=t.parents)
                for t in self._lat_cpp.concepts
            ],
            amount_of_objects=len(self.ctx.G),
            amount_of_attributes=len(self.ctx.M),
            **kwargs,
        )

    def __repr__(self) -> str:
        return self._lat_cpp.__repr__()


class IncrementalSolver(Inclose):
    def get_lattice(self, ctx):
        return IncLattice(ctx)


class NonIncrementalSolver(Inclose):
    def get_lattice(self, ctx: Context):
        hasse, concepts = calculate_hasse(ctx, self.get_concepts(ctx))
        return Lattice(hasse, concepts)


# This is a variable later used for automatically generating the docs
__all__ = (
    "Context",
    "Lattice",
    "IncLattice",
)

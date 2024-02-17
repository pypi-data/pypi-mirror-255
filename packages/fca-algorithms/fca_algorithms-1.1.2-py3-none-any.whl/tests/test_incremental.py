import pytest

from .utils import *
from src.fca.api_models import IncLattice, Context
from src.fca.base_models import Concept


def  test_integration(random_big_context):
    ctx = Context(*random_big_context)

    l = IncLattice(ctx.A)
    for i, g in enumerate(ctx.O):
        intent = []
        for j, m in enumerate(ctx.A):
            if ctx.I[i][j]:
                intent.append(j)
        l.add_intent(g, intent)
    
    expected_concepts = ctx.get_lattice().concepts

    expected_res = [sort_tuple(c.to_tuple()) for c in expected_concepts]
    res = [sort_tuple(Concept(l.ctx, c.X, c.Y).to_tuple()) for c in l.concepts]
    expected_res.sort()
    res.sort()
    assert len(res) == len(expected_res)
    assert res == expected_res

    concepts_result = list(l.concepts)
    concepts_result.sort(key=concept_key)
    expected_concepts.sort(key=concept_key)
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


import pytest
from src.fca.rca.p18n import EXISTS
from src.fca.rca.rca import rca_get_relations, lattice_and_concept_idx
from src.fca.api_models import Context
from src.fca.plot.plot import plot_from_hasse
from src.fca.utils.utils import to_subscript


def test_rca_converges(create_objects_and_attributes,
                       create_objects_and_attributes_2, create_relation_between_0_and_1):
    k_1 = create_objects_and_attributes
    k_2 = create_objects_and_attributes_2
    K = [Context(*k_1), Context(*k_2)]
    R = [create_relation_between_0_and_1]
    lattices = rca_get_relations(K, R, EXISTS)
    assert len(lattices) == 2


def test_rca_creates_the_right_amount_of_attributes(
        create_objects_and_attributes, create_objects_and_attributes_2, create_relation_between_0_and_1):
    k_1 = create_objects_and_attributes
    k_2 = create_objects_and_attributes_2
    K = [Context(*k_1), Context(*k_2)]
    R = [create_relation_between_0_and_1]
    lattices = rca_get_relations(K, R, EXISTS)
    maximum_lattice_concept = len(lattices[1].concepts)
    assert '∃R₀₋₁ : C₁₋₀' in K[0].A
    assert f'∃R₀₋₁ : C₁₋{to_subscript(maximum_lattice_concept - 1)}' in K[0].A
    assert f'∃R₀₋₁ : C₁₋{to_subscript(maximum_lattice_concept)}' not in K[0].A


def test_rca_exists_makes_sense(create_objects_and_attributes,
                                create_objects_and_attributes_2, create_relation_between_0_and_1):
    relation = create_relation_between_0_and_1
    k_1 = Context(*create_objects_and_attributes)
    number_of_k_1_0_attibutes = len(k_1.A)
    k_2 = Context(*create_objects_and_attributes_2)
    K = [k_1, k_2]
    R = [create_relation_between_0_and_1]
    lattices = rca_get_relations(K, R, EXISTS)
    lattice_k_1 = lattices[0]
    lattice_k_2 = lattices[1]
    exists_symbol = str(EXISTS)
    relation_symbol_idx = number_of_k_1_0_attibutes
    while relation_symbol_idx < len(k_1.A):
        relational_attribute = k_1.A[relation_symbol_idx]
        # Lattice and concept ids
        i, j = relational_attribute.concepts[0][0], relational_attribute.concepts[0][1]
        for obj_idx, o in enumerate(k_1.O):
            found_one = exists_relation(lattice_k_2, j, relation, obj_idx)
            assert (k_1.I[obj_idx][relation_symbol_idx] and found_one) or \
                   (not k_1.I[obj_idx][relation_symbol_idx] and not found_one)
        relation_symbol_idx += 1


@pytest.mark.skip(reason="UI test")
def test_rca_plot(create_objects_and_attributes,
                  create_objects_and_attributes_2, create_relation_between_0_and_1):
    k_1 = create_objects_and_attributes
    k_2 = create_objects_and_attributes_2
    K = [Context(*k_1), Context(*k_2)]
    R = [create_relation_between_0_and_1]
    lattices = rca_get_relations(K, R, EXISTS)
    for lattice in lattices:
        hasse, concepts = lattice.hasse, lattice.concepts
        plot_from_hasse(hasse, concepts)
    assert lattices


def exists_relation(lattice_k_2, j, relation, obj_idx):
    found_one = False
    for o_2 in lattice_k_2.concepts[j].O:
        found_one = found_one or o_2 in relation[obj_idx]
    return found_one

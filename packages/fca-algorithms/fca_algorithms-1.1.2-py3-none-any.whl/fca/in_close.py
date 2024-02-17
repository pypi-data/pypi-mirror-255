from .base_models import Context, Concept
from .utils.utils import inverse_range, is_in, lower_bound, insert_ordered
from fca_algorithms_cpp import inclose as inclose_cpp


def inclose_start(context: Context):
    concepts = inclose_cpp(context.O, [str(y) for y in context.A], context.I)
    ret_concepts = []
    for c in concepts:
        ret_concepts.append(Concept(context, c.X, c.Y))

    return ret_concepts

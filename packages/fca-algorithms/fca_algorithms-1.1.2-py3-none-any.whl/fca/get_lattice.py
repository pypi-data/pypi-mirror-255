import csv

from abc import ABC, abstractmethod
from typing import List

from .base_models import Context, Concept
from .in_close import inclose_start
from .association_rules import get_association_rules
from .border_hasse import calculate_hasse


class FCASolver(ABC):
    @abstractmethod
    def get_concepts(self, ctx: Context) -> List[Concept]:
        return None

    def get_lattice(self, ctx: Context):
        concepts = self.get_concepts(ctx)
        return calculate_hasse(ctx, concepts)

    def get_association_rules(self, ctx, min_support=0.5, min_confidence=1):
        return get_association_rules(ctx, min_support, min_confidence)

    def generate_association_rules(
        self, ctx: Context, filename: str, min_support=0.5, min_confidence=1
    ):
        with open(
            f"{filename if filename.endswith('.csv') else filename + '.csv'}", "w"
        ) as f:
            writer = csv.writer(f)
            writer.writerow(["support", "confidence", "base", "add"])
            for assoc_rule in ctx.get_association_rules(
                min_support=min_support, min_confidence=min_confidence
            ):
                support = assoc_rule.support
                for rule in assoc_rule.ordered_statistics:
                    row = [
                        support,
                        rule.confidence,
                        f'{{{", ".join(x for x in rule.items_base)}}}',
                        f'{{{", ".join(x for x in rule.items_add)}}}',
                    ]
                    writer.writerow(row)


class Inclose(FCASolver):
    def get_concepts(self, ctx: Context) -> List[Concept]:
        # one of the caveats of inclose is that it doesn't include bottom =
        # (A', A)
        res = inclose_start(ctx)
        if not self._has_bottom(ctx, res):
            res.append(self._calculate_bottom(ctx))
        return res

    def _calculate_bottom(self, ctx: Context) -> Concept:
        objects_with_all_attributes = []
        for i in range(len(ctx.O)):
            is_related_to_all = True
            for j in range(len(ctx.A)):
                if not ctx.I[i][j]:
                    is_related_to_all = False
                    break
            if is_related_to_all:
                objects_with_all_attributes.append(i)
        return Concept(ctx, objects_with_all_attributes, [j for j in range(len(ctx.A))])

    def _has_bottom(self, ctx, concepts) -> bool:
        for concept in concepts:
            if len(concept.A) == len(ctx.A):
                return True
        return False

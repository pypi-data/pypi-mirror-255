from typing import List


from apyori import apriori
from .base_models import Concept


def get_association_rules(
        ctx, min_support=0.5, min_confidence=1):
    """Given a list of concepts, it returns a generator of its association rules
    """
    transactions = []
    for i, transaction in enumerate(ctx.O):
        transactions.append([])
        for j, attr in enumerate(ctx.A):
            if ctx.I[i][j]:
                transactions[i].append(attr)
    return apriori(transactions, min_support=min_support,
                   min_confidence=min_confidence)

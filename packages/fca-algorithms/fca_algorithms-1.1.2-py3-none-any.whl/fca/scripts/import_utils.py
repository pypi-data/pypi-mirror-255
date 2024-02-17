import csv

from ..api_models import Context
from ..rca.models import Relation


def parse_rca(args):
    contexts = []
    for ctx_name in args.contexts:
        contexts.append(import_context(ctx_name, args.context_format))

    relations = []
    for relation_name in args.relations:
        relations.append(import_relation(relation_name, contexts))
    
    edge_colours = []
    if args.edge_colours:
        for colour in args.edge_colours:
            edge_colours.append(colour)

    return contexts, relations, edge_colours


def parse_fca(args):
    return import_context(args.context, args.context_format)


def import_context(ctx_name, format):
    res = None
    if format == 'one_line_per_attribute':
        res = import_context_one_line_per_attribute(ctx_name)
    elif format == 'table':
        res = import_context_table(ctx_name)
    return res


def import_context_one_line_per_attribute(filename):
    O = []
    A = []
    I = []
    all_O = dict()
    all_A = dict()
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            obj, attr = row
            if obj not in all_O:
                all_O[obj] = len(O)
                O.append(obj)
                I.append([0 for _ in range(len(A))])
            if attr not in all_A:
                all_A[attr] = len(A)
                A.append(attr)
                for i in range(len(O)):
                    I[i].append(0)
            I[all_O[obj]][all_A[attr]] = 1
    return Context(O, A, I)


def import_context_table(filename):
    O = []
    A = []
    I = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        loading_attributes = True
        for row in reader:
            if loading_attributes:
                for attr in row[1:]:
                    A.append(attr)
                loading_attributes = False
            else:
                O.append(row[0])
                I.append([])
                for attr_i in row[1:]:
                    I[-1].append(len(attr_i) != 0)
    return Context(O, A, I)


def separate_indexes(filename):
    k = 0
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        row = next(reader)
        k = len(row)  # the the arity of the relationship
    # removes .csv, split by _, and then get only the last k elements which
    # should be the indexes
    return filename[:-4].split("_")[-k:]


def import_relation(filename, contexts):
    index_offset = 1
    # This is actually the arity of the relation
    contexts_indexes = [
        int(idx) -
        index_offset for idx in separate_indexes(filename)]

    # for each context, it tells me what's the id of each object
    object_indexes_by_context = []
    for idx in contexts_indexes:
        context = contexts[idx]
        object_indexes = {}
        for i, o in enumerate(context.O):
            object_indexes[o] = i
        object_indexes_by_context.append(object_indexes)

    R = dimension(contexts, contexts_indexes, 0)
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            i = object_indexes_by_context[0][row[0]]
            current = R[int(i) - index_offset]
            to_process = 1
            while to_process < len(contexts_indexes) - 1:
                i = object_indexes_by_context[to_process][row[to_process]]
                current = current[int(i) - index_offset]
                to_process += 1
            # At this point current is a set
            i = object_indexes_by_context[to_process][row[to_process]]
            current.add(int(i) - index_offset)
    return Relation(R, contexts_indexes)


def dimension(contexts, contexts_indexes, i):
    if i == len(contexts_indexes) - 1:
        return set()
    context = contexts[contexts_indexes[i]]
    context_len = len(context.O)
    return [dimension(contexts, contexts_indexes, i + 1)
            for _ in range(context_len)]

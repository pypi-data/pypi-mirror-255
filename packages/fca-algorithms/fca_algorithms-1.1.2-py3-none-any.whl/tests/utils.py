def sort_tuple(t):
        t[0].sort()
        t[1].sort()
        return t


def concept_key(t):
        return sort_tuple(t.to_tuple())

def obj_equals(a, b):
    if not a and not b:
        return True
    if not a or not b:
        return False
    if type(a) != type(b):
        return False
    if type(a) is object:
        if a.keys() != b.keys():
            return False
        for k in a.keys():
            if not obj_equals(a[k], b[k]):
                return False
        return True
    return a == b



from collections import defaultdict
from types import DictType, ListType
from pprint import pprint


def _make_path(base, part):
    if base == '':
        return part
    else:
        return '.'.join((base, part))


def _is_leaf(value):
    return isinstance(value, (int, long, float, basestring))


def _namespaceify(value, current, namespace):
    if _is_leaf(value):
        return True

    if isinstance(value, DictType):
        for key, item in value.iteritems():
            path = _make_path(current, key)
            if _namespaceify(item, path, namespace):
                namespace[path] = item

        return False

    if isinstance(value, ListType):
        for i, item in enumerate(value):
            path = _make_path(current, str(i))
            if _namespaceify(item, path, namespace):
                namespace[path] = item
        return False

    raise Exception(value)

def namespaceify(*values):
    namespace = defaultdict(lambda: [])
    current = ''

    for value in values:
        _namespaceify(value, current, namespace)


    sorted_namespace = sorted(namespace.iteritems())
    return sorted_namespace


def tree_split(namespace):
    tree = {}
    payload = []
    for path, value in namespace:
        parts = path.split('.')

        parent = tree
        subtree = tree

        for part in parts:
            if part not in subtree:
                subtree[part] = {}
            parent = subtree
            subtree = subtree[part]
        else:
            if parent[part] == {}:
                parent[part] = [len(payload)]
                payload.append(value)
            else:
                parent[part].append(len(payload))
                payload.append(value)

    return tree, payload

obj = {'a':[
    {'x': [{'alpha': 1}, 2]},
    {'x': [3.5, 4]},
]}

pprint(obj)
pprint(obj)

namespace = namespaceify(obj) + list(reversed(namespaceify(obj)))
paths = []
values = []
for (path, value) in namespace:
    paths.append(path)
    values.append(value)

tree, payload = tree_split(namespace)

pprint(tree)
pprint(payload)


def unsplit_tree(tree, payload):

    def _unsplit_tree(tree, path_keys):
        for key, subtree in tree.iteritems():
            if isinstance(subtree, ListType):
                for index in subtree:
                    yield '.'.join(path_keys + [key]), payload[index]
            else:
                for path, x in _unsplit_tree(subtree, path_keys + [key]):
                    yield path, x

    return _unsplit_tree(tree, [])


namespace = list(unsplit_tree(tree, payload))
for path, value in namespace:
    print path, value


def _unpath(base, path_parts, value):
    if len(path_parts) == 0:
        return value    
    else:
        head = path_parts[0]
        rest = path_parts[1:]

        return {
            head: _unpath({}, rest, value)
        }

def _merge_onto(bottom, top):
    if isinstance(top, DictType):
        for key, value in top.iteritems():
            if key in bottom:
                bottom[key] = _merge_onto(bottom[key], top[key])
            else:
                bottom[key] = value
        return bottom
    
    if isinstance(bottom, ListType):
        return bottom + [top]

    else:
        return [bottom] + [top]

def unnamespaceify(namespace):
    obj = {}
    for path, value in namespace:
        parts = path.split('.')

        obj = _merge_onto(obj, _unpath(obj, parts, value))
    
    return obj

obj = unnamespaceify(namespace)
pprint(obj)


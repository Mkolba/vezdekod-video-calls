# -*- coding: utf-8 -*-
import json


class BetterDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    @staticmethod
    def loads(obj):
        return json.loads(obj, object_pairs_hook=lambda x: BetterDict(x))


def resolve_cover(sizes):
    sizes = {item['width'] * item['height']: item['url'] for item in sizes}
    return sizes.get(1280 * 720, sizes[max(sizes.keys())])


def incline_views(num):
    text_forms = ['просмотр', 'просмотра', 'просмотров']
    n = abs(num) % 100
    n1 = n % 10
    if 10 < n < 20:
        return text_forms[2]
    if 1 < n1 < 5:
        return text_forms[1]
    if n1 == 1:
        return text_forms[0]
    return text_forms[2]

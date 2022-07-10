# -*- coding: utf-8 -*-
import json


class BetterDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    @staticmethod
    def loads(obj):
        return json.loads(obj, object_pairs_hook=lambda x: BetterDict(x))


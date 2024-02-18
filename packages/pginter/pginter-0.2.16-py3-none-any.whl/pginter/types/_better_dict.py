"""
_better_dict.py
04. February 2023

A dict type similar to the javascript JSON object

Author:
Nilusink
"""


class BetterDict(dict):
    def __getattr__(self, item):
        result = self[item]
        if issubclass(type(result), dict):
            return BetterDict(result)

        return result

    def __setattr__(self, key, value):
        self[key] = value

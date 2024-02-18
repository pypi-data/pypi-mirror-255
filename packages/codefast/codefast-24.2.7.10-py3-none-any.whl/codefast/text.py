#!/usr/bin/env python3
from typing import Any, List


def add_whitespace(sentece: str) -> str:
    # Add space between Chinese and English words if there is no space
    import string
    english_words = string.ascii_letters + string.digits
    s = ''
    pre = '#'
    for c in sentece:
        # check if c is Chinese
        if c == ' ':
            s += c
        elif '\u4e00' <= c <= '\u9fa5':
            if pre and pre in english_words:
                s += ' ' + c
            else:
                s += c
        else:
            if pre and ('\u4e00' <= pre <= '\u9fa5'):
                # print(pre, c)
                s += ' ' + c
            else:
                s += c
        pre = c

    return s


class MarkDownHelper(object):
    @staticmethod
    def to_table(headers: List[Any], data: List[List[Any]]) -> str:
        """ Convert data to markdown table.
        Args:
            headers: list of str
            data: list of list of str
        """
        for d in data:
            assert len(headers) == len(
                d), f'{headers} vs {d} not match on length'
        table = []
        headers = [''] + headers + ['']
        table.append('|'.join(headers))
        splits = [''] + ['-'] * (len(headers) - 2) + ['']
        table.append('|'.join(splits))
        for row in data:
            row = [''] + list(map(str, row)) + ['']
            table.append('|'.join(row))
        return '\n'.join(table)

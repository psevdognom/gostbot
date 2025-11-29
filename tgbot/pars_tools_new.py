#!/usr/bin/python
# -*- coding: utf8 -*-
"""
Parser tools for fetching GOSTs from libgost.ru.

This module is deprecated. Please use data_sources.py for all GOST parsing.
See data_sources.LibGostRuDataSource for the updated implementation.
"""

from tgbot.data_sources import LibGostRuDataSource


def parse():
    """
    Parse GOSTs from libgost.ru.
    
    Returns:
        List of GOST dictionaries with 'name' and 'description' keys.
    """
    source = LibGostRuDataSource()
    return source.fetch_gosts()


if __name__ == '__main__':
    gosts = parse()
    for gost in gosts:
        print(gost)

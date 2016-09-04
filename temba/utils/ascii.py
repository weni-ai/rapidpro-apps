# -*- coding: utf-8 -*-

from unidecode import unidecode

__author__ = 'teehamaral'


def to_ascii(text):
    return unicode(unidecode(text))

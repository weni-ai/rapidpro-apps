# -*- coding: utf-8 -*-

__author__ = 'teehamaral'

from unidecode import unidecode


def to_ascii(text):
    return unicode(unidecode(text))

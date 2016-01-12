# -*- coding: utf-8 -*-

__author__ = 'teehamaral'

from unidecode import unidecode


def to_ascii(text):
    text = unidecode(text.decode('UTF-8'))
    return text.encode('ISO-8859-1', errors='ignore')

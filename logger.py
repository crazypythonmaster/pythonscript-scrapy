#!/usr/bin/env python
from Singleton import Singleton

class logger(object):
    """class: logger"""

    __metaclass__ = Singleton

    def __init__ (self, **kwargs):
        """Constructor"""
        if 'fname' not in kwargs:
            self.fh = open('log.txt', "w")
        else:
            self.fh = open(kwargs['fname'], "w")

    @classmethod
    def dump (cls, text):
        """def: dump"""
        self = cls()
        print text
        self.fh.write(text + "\n")



#!/usr/bin/env python
from Singleton import Singleton
import csv
import re

class rdcsv_filter(object):
    """class: rdcsv_filter"""

    __metaclass__ = Singleton
    data_h = {}

    def __init__ (self, fname):
        """Constructor"""
        self.fname = fname

    def get_heading (self):
        """def: get_heading"""
        with open(self.fname, "rb") as cfh:
            reader = csv.reader(cfh, delimiter=";", quotechar='"')
            idx = 1
            for row in reader:
                if idx == 1 and not re.search('sep=.$', ','.join(row)):
                    self.heading = row
                    break
                if idx == 2:
                    self.heading = row
                    break
                idx += 1

    def filter_get_col (self, value, col_heading):
        """def: filter"""
        if value.decode('cp1252') not in self.data_h:
            return []

        col_values = map(lambda x: x[col_heading], self.data_h[value.decode('cp1252')])
        return col_values
        
    def parse (self, col_heading):
        """def: parse"""
        self.get_heading()

        with open(self.fname, "rb") as cfh:
            reader = csv.DictReader(cfh, fieldnames=self.heading, delimiter=";", quotechar='"')
            idx = 0
            for row in reader:
                idx += 1
                if idx <= 2:
                    continue
                if row[col_heading].decode('cp1252') not in self.data_h:
                    self.data_h[row[col_heading].decode('cp1252')] = []

                self.data_h[row[col_heading].decode('cp1252')].append(row)




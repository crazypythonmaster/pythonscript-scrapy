#!/usr/bin/env python
import csv

class vardcentraler_csv(object):
    """class: vardcentraler_csv"""

    def __init__(self, fname):
        self.fname = fname
        self.csvfh = open(fname, "rb")
        #self.reader = csv.reader(self.csvfh, delimiter=";", quotechar='"')
        self.heading = ['PARENT_WORKPLACE_NAME','PARENT_WORKPLACE_ADDRESS','PARENT_WORKPLACE_ZIP','PARENT_WORKPLACE_CITY','PARENT_WORKPLACE_PHONE']
        self.reader = csv.DictReader(self.csvfh, fieldnames=self.heading, delimiter=";", quotechar='"')
        self.reader.next()
        self.reader.next()
        

    def read (self):
        """def: read"""
        for row_h in self.reader:
            yield row_h



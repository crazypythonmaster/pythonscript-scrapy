#!/usr/bin/env python
from Singleton import Singleton
import csv

class csv_writer(object):
    """class: csv_writer"""

    __metaclass__ = Singleton

    def __init__ (self, **kwargs):
        """Constructor"""
        self.csv_fh = open(kwargs['fname'], "wb")
        self.heading = kwargs['heading']
        self.writer = csv.writer(self.csv_fh, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        self.writer.writerow(['sep=;'])
        self.writer.writerow(self.heading)
        
    @classmethod
    def write_row_h (cls, row_h):
        """def: write_row_h"""

        self = cls()
        row = [row_h.get(field, None) for field in self.heading]
        self.writer.writerow(row)


class csv_doctor(csv_writer):
    """class: csv_doctor"""
    pass

class csv_list_all_doctors(csv_writer):
    """class: csv_doctor"""
    pass

class csv_list_found_doctors(csv_writer):
    """class: csv_doctor"""
    pass

class csv_hitta(csv_writer):
    """class: csv_hitta"""
    pass

class csv_eniro(csv_writer):
    """class: csv_eniro"""
    pass

class csv_hitta_vardcentraler(csv_writer):
    """class: csv_hitta_vardcentraler"""
    pass

class csv_hitta_vardcentraler_summary(csv_writer):
    """class: csv_hitta_vardcentraler_summary"""
    pass

class csv_hitta_eniro_vs_primary_clinic(csv_writer):
    """class: csv_hitta_eniro_vs_primary_clinic"""
    pass

class csv_hitta_eniro_vs_primary_clinic_summary(csv_writer):
    """class: csv_hitta_eniro_vs_primary_clinic_summary"""
    pass




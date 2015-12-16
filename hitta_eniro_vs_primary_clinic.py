#!/usr/bin/env python
# vim: set fileencoding=cp1252 :
import csv
import re
from cp1252 import cp1252
from logger import logger
from csv_writer import csv_hitta_eniro_vs_primary_clinic
from csv_writer import csv_hitta_eniro_vs_primary_clinic_summary
import string
import sys, getopt
reload(sys)  
sys.setdefaultencoding('utf8')

directory = ""

class hitta_vs_primary_clinic(object):
    """class: hitta_vs_primary_clinic"""

    def init_hitta_vardcentraler (self):
        """def: init_hitta_vardcentraler"""
        self.hitta_vardcentraler_csvfh = open(directory + '/hitta_eniro_vardcentraler_result.csv', "rb")
        self.hitta_vardcentraler_heading = [ 'URL', 'SEARCH_NAME', 'FOUND_NAME', 'ADDRESS', 'ZIP', 'CITY', 'PHONE', 'WEBSITE', 'NAME_MATCH?', 'ADDRESS_MATCH?', 'ZIP_MATCH?', 'CITY_MATCH?', 'PHONE_MATCH?', 'VARDCENTRAL', 'HITTA_OR_ENIRO', 'COLOR' ]
        self.hitta_vardcentraler_reader = csv.DictReader(self.hitta_vardcentraler_csvfh, fieldnames=self.hitta_vardcentraler_heading, delimiter=";", quotechar='"')
        self.hitta_vardcentraler_reader.next()
        self.hitta_vardcentraler_reader.next()

    def init_primary_clinic (self):
        """def: init_primary_clinic"""
        self.primary_clinic_csvfh = open(directory + '/hitta_primary_clinic_result.csv', "rb")
        self.primary_clinic_heading = ['URL','SEARCH_NAME','FOUND_NAME','ADDRESS','ZIP','CITY','PHONE','WEBSITE']
        self.primary_clinic_reader = csv.DictReader(self.primary_clinic_csvfh, fieldnames=self.primary_clinic_heading, delimiter=";", quotechar='"')
        self.primary_clinic_reader.next()
        self.primary_clinic_reader.next()
        
    def _parse_hitta_vardcentraler_result (self):
        """def: _parse_hitta_vardcentraler_result"""
        hitta_vardcentraler_results_h = {}
        with open(directory + '/hitta_eniro_vardcentraler_result.csv', "rb") as fh:
            heading = ['URL','SEARCH_NAME','FOUND_NAME','ADDRESS','ZIP','CITY','PHONE','WEBSITE']
            reader = csv.DictReader(fh, fieldnames=heading, delimiter=";", quotechar='"')
            reader.next()
            reader.next()
            for row_h in reader:
                if row_h['FOUND_NAME'] not in hitta_vardcentraler_results_h:
                    hitta_vardcentraler_results_h[row_h['FOUND_NAME']] = []
                hitta_vardcentraler_results_h[row_h['FOUND_NAME']].append(row_h)
        self.hitta_vardcentraler_results_h = hitta_vardcentraler_results_h

    def __init__(self):
        self.hitta_vardcentraler_results_h = {}
        self.summary_row_h = {'# (Vardcentral + Primary Clnic)': 0, '# (Vardcentral)': 0, '# (Primary Clnic)': 0}

    def _compare_hitta_vardcentraler (self):
        """def: _compare_hitta_vardcentraler"""
        for row_h in self.hitta_vardcentraler_reader:
            if row_h ['VARDCENTRAL'] == 'YES':
                row_h ['FOUND_IN'] = 'Both'
                self.summary_row_h ['# (Vardcentral + Primary Clnic)'] += 1 
            elif row_h ['VARDCENTRAL'] == 'NO':
                row_h ['FOUND_IN'] = 'Vardcentraler'
                self.summary_row_h ['# (Vardcentral)'] += 1 

            csv_hitta_eniro_vs_primary_clinic.write_row_h(row_h)
        
    def _compare_primary_clinic (self):
        """def: _compare_primary_clinic"""
        for row_h in self.primary_clinic_reader:
            if row_h ['FOUND_NAME'] not in self.hitta_vardcentraler_results_h:
                row_h ['FOUND_IN'] = 'Primary Clinic'
                self.summary_row_h ['# (Primary Clnic)'] += 1
                csv_hitta_eniro_vs_primary_clinic.write_row_h(row_h)
        
    def compare (self):
        """def: compare"""
        self._parse_hitta_vardcentraler_result ()
        self.init_primary_clinic ()
        self.init_hitta_vardcentraler ()

        self._compare_hitta_vardcentraler ()
        self._compare_primary_clinic ()
        csv_hitta_eniro_vs_primary_clinic_summary.write_row_h(self.summary_row_h)
        

if __name__ == '__main__':
    def main(argv):                         
        grammar = "kant.xml"
        try:                                
            opts, args = getopt.getopt(argv, "d:", ["dir="])
        except getopt.GetoptError:
            Usage()

        if len(opts) == 0:
            Usage()

        return opts
            
    def Usage ():
        print "Usage: python scrape.py -d <Directory>"
        print "       Where: <Directory> is the path of the directory where Vardcentraler.csv and other csv files are kept"
        sys.exit(2)

    opts = main(sys.argv[1:])

    directory = opts[0][1]


    heading_hitta_vardcentraler=[
        'URL',
        'SEARCH_NAME',
        'FOUND_NAME',
        'ADDRESS',
        'ZIP',
        'CITY',
        'PHONE',
        'WEBSITE',
        'FOUND_IN',
        'HITTA_OR_ENIRO',
    ]
    heading_hitta_vardcentraler_summary=[
        '# (Vardcentral + Primary Clnic)',
        '# (Vardcentral)',
        '# (Primary Clnic)',
    ]

    m_csv_hitta_eniro_vs_primary_clinic = csv_hitta_eniro_vs_primary_clinic(fname=directory + '/hitta_eniro_vs_primary_clinic.csv', heading=heading_hitta_vardcentraler)
    m_csv_hitta_eniro_vs_primary_clinic_summary = csv_hitta_eniro_vs_primary_clinic_summary(fname=directory + '/hitta_eniro_vs_primary_clinic_summary.csv', heading=heading_hitta_vardcentraler_summary)

    print "OUTPUT CSV FILE: hitta_eniro_vs_primary_clinic.csv"
    print "OUTPUT CSV SUMMARY FILE: hitta_eniro_vs_primary_clinic_summary.csv"

    m_hitta_vs_primary_clinic = hitta_vs_primary_clinic()
    m_hitta_vs_primary_clinic.compare()





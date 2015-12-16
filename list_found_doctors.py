#!/usr/bin/env python
import mechanize
import cookielib
from find_doctor import find_doctor
from csv_writer import csv_doctor
from csv_writer import csv_list_found_doctors
from rdcsv_filter import rdcsv_filter
import re
import csv
import sys, getopt

directory = ""

class list_found_doctors(object):
    """class: list_found_doctors"""

    def __init__(self):
        self.hitta_eniro_vardcentraler_csvfh = open(directory + '/hitta_eniro_vardcentraler_result.csv', "rb")
        self.hitta_eniro_vardcentraler_heading = [
            'URL',
            'SEARCH_NAME',
            'FOUND_NAME',
            'ADDRESS',
            'ZIP',
            'CITY',
            'PHONE',
            'WEBSITE',
            "NAME_MATCH?",
            "ADDRESS_MATCH?",
            "ZIP_MATCH?",
            "CITY_MATCH?",
            "PHONE_MATCH?",
            "VARDCENTRAL",
            'HITTA_OR_ENIRO',
            'COLOR',
        ]
        self.hitta_eniro_vardcentraler_reader = csv.DictReader(self.hitta_eniro_vardcentraler_csvfh, fieldnames=self.hitta_eniro_vardcentraler_heading, delimiter=";", quotechar='"')
        self.hitta_eniro_vardcentraler_reader.next()
        self.hitta_eniro_vardcentraler_reader.next()

    def find (self):
        """def: find"""
        for row_h in self.hitta_eniro_vardcentraler_reader:
            m_rdcsv_filter = rdcsv_filter ()
            names = m_rdcsv_filter.filter_get_col(row_h['SEARCH_NAME'], 'FULL_NAME')
            # Return if no names are found in 1177
            if len(names) == 0: continue

            if not re.search('^\s*$', row_h['WEBSITE']):
                if not re.search('^http', row_h['WEBSITE']):
                    row_h['WEBSITE'] = "http://" + row_h['WEBSITE']

                m_find_doctor = find_doctor()
                for match in m_find_doctor.find(row_h['WEBSITE'], names):
                    match['SEARCH_PARENT_WORKPLACE_NAME'] = row_h['SEARCH_NAME']
                    match['FOUND_PARENT_WORKPLACE_NAME'] = row_h.get('FOUND_NAME', None)
                    csv_doctor.write_row_h(match)

                    if not 'FOUND_DOCTOR_TAG' in row_h:
                        if 'FOUND_DOCTOR_TAG' in match:
                            row_h ['FOUND_DOCTOR_TAG'] = match['FOUND_DOCTOR_TAG']

                    # Found doctors on home url
                    if 'SEARCH_DOCTOR_NAME' in match:
                        if 'FOUND_DOCTOR_NAME' in match:
                            if 'FOUND_DOCTORS' not in row_h: 
                                row_h['FOUND_DOCTORS'] = match['SEARCH_DOCTOR_NAME']
                            else: 
                                row_h['FOUND_DOCTORS'] = "%s|%s" % (row_h['FOUND_DOCTORS'], match['SEARCH_DOCTOR_NAME'])
                        else:
                            if 'MISSING_DOCTORS' not in row_h: 
                                row_h['MISSING_DOCTORS'] = match['SEARCH_DOCTOR_NAME']
                            else: 
                                row_h['MISSING_DOCTORS'] = "%s|%s" % (row_h['MISSING_DOCTORS'], match['SEARCH_DOCTOR_NAME'])

                    if 'URL' in match:
                        if 'FOUND_DOCTORS_URL' not in row_h:
                            row_h['FOUND_DOCTORS_URL'] = match['URL']
                        elif match['URL'] not in row_h['FOUND_DOCTORS_URL']:
                            row_h['FOUND_DOCTORS_URL'] = "%s|%s" % (row_h['FOUND_DOCTORS_URL'], match['URL'])
            csv_list_found_doctors.write_row_h(row_h)
        


if __name__ == "__main__":
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



    heading_found_doctors=[
        'URL',
        'SEARCH_NAME',
        'FOUND_NAME',
        'ADDRESS',
        'ZIP',
        'CITY',
        'PHONE',
        'WEBSITE',
        "NAME_MATCH?",
        "ADDRESS_MATCH?",
        "ZIP_MATCH?",
        "CITY_MATCH?",
        "PHONE_MATCH?",
        "VARDCENTRAL",
        'HITTA_OR_ENIRO',
        'COLOR',
        'FOUND_DOCTOR_TAG',
        'FOUND_DOCTORS',
        'FOUND_DOCTORS_URL',
        'MISSING_DOCTORS',
    ]
    m_csv_list_found_doctors = csv_list_found_doctors(fname = directory + '/found_doctors_result.csv', heading = heading_found_doctors)

    heading_doctors=[
      'HOME_URL',
      'URL',
      'SEARCH_PARENT_WORKPLACE_NAME',
      'FOUND_PARENT_WORKPLACE_NAME',
      'SEARCH_DOCTOR_NAME',
      'FOUND_DOCTOR_NAME',
      'MATCH?',
    ]
    m_csv_doctor = csv_doctor(fname = directory + '/doctors_result.csv', heading = heading_doctors)

    m_rdcsv_filter = rdcsv_filter(directory + '/ALL_RECORDS_MATCH_73_273_TO_273_373_SPLIT_ADDRESS.csv')
    m_rdcsv_filter.parse('PARENT_WORKPLACE_NAME')

    m_list_found_doctors = list_found_doctors()
    m_list_found_doctors.find()












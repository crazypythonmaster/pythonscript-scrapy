#!/usr/bin/env python

import re
import csv
import mechanize
import cookielib
import sys, getopt
from bs4 import BeautifulSoup
from unidecode import unidecode
from cp1252 import cp1252
from csv_writer import csv_hitta_vardcentraler
reload(sys)  
sys.setdefaultencoding('utf8')

directory = ""

class get_all_doctors(object):
    """class: get_all_doctors"""

    def _init_mech (self):
        """def: _init_mech"""
        mech = mechanize.Browser()

        cj = cookielib.LWPCookieJar()
        mech.set_cookiejar(cj)

        mech.set_handle_equiv(True)
        mech.set_handle_gzip(False)
        mech.set_handle_redirect(True)
        mech.set_handle_referer(True)
        mech.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        mech.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')] 
        return mech
 

    def __init__(self):
        self.doctor_match_result_csvfh = open(directory + '/found_doctors_result.csv', "rb")
        self.doctor_match_result_heading = [
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
        self.doctor_match_result_reader = csv.DictReader(self.doctor_match_result_csvfh, fieldnames=self.doctor_match_result_heading, delimiter=";", quotechar='"')
        self.doctor_match_result_reader.next()
        self.doctor_match_result_reader.next()
        self.mech = self._init_mech()

    def _find_name (self, tag):
        """def: _find_name"""
        if tag.string == None: return 0
        
        # string = tag.string.encode('cp1252')
        string = tag.string
        name_fields = re.split(r'[, ]+', string)

        if name_fields and len(name_fields) > 1:
            match = 1
            for name_field in name_fields:
                name_field_d = unidecode(name_field)
                if not re.search('^[A-Z][a-z]+$', name_field_d):
                    match = 0

            if match == 1:
                if self.doctor_tag and not re.search('^\s*$', self.doctor_tag):
                    if self.doctor_tag != tag.name:
                        match = 0
            return match
        return 0
        
    def get_all_names (self, home_url):
        """def: get_all_names"""
        print "Open: " + home_url
        self.mech.open(home_url)

        #print self.mech.response().read()
        soup = BeautifulSoup(self.mech.response().read(), "html.parser")
        names = soup.find_all(self._find_name)
        names = [name.string for name in names]
        names = list(set(names))
        return names
        
        
    def parse (self):
        """def: parse"""
        for row_h in self.doctor_match_result_reader:
            if not row_h ['FOUND_DOCTORS_URL']: 
                csv_hitta_vardcentraler.write_row_h(row_h)
                continue

            if row_h ['FOUND_DOCTORS_URL'] == "":
                csv_hitta_vardcentraler.write_row_h(row_h)
                continue 

            home_urls = row_h ['FOUND_DOCTORS_URL']
            self.doctor_tag = row_h ['FOUND_DOCTOR_TAG']

            all_names = []
            for home_url in row_h['FOUND_DOCTORS_URL'].split("|"):
                names = self.get_all_names (home_url)
                all_names = all_names + names
            all_names_str = '|'.join(all_names)
            row_h["FOUND_ALL_NAMES"] = cp1252(all_names_str)
            csv_hitta_vardcentraler.write_row_h(row_h)
        
        

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


    heading_all_doctors_names_result=[
      'URL',
      'SEARCH_NAME',
      'FOUND_NAME',
      'ADDRESS',
      'ZIP',
      'CITY',
      'PHONE',
      'WEBSITE',
      'NAME_MATCH?',
      'ADDRESS_MATCH?',
      'ZIP_MATCH?',
      'CITY_MATCH?',
      'PHONE_MATCH?',
      'VARDCENTRAL',
      'HITTA_OR_ENIRO',
      'COLOR',
      'FOUND_DOCTOR_TAG',
      'FOUND_DOCTORS',
      'FOUND_DOCTORS_URL',
      'MISSING_DOCTORS',
      'FOUND_ALL_NAMES',
    ]
    m_csv_hitta_vardcentraler = csv_hitta_vardcentraler(fname= directory + '/get_all_doctors_names_result.csv', heading=heading_all_doctors_names_result)

    m_get_all_doctors = get_all_doctors()
    m_get_all_doctors.parse()


#!/usr/bin/env python
# vim: set fileencoding=cp1252 :
import csv
import re
from cp1252 import cp1252
from logger import logger
from csv_writer import csv_hitta_vardcentraler
from csv_writer import csv_hitta_vardcentraler_summary
import string
import sys, getopt

reload(sys)  
sys.setdefaultencoding('utf8')

directory = ""


class hitta_compare(object):
    """class: hitta_compare"""

    def __init__ (self):
        """Constructor"""
        self.vardcentraler_csvfh = open( directory + '/Vardcentraler.csv', "rb")
        self.vardcentraler_heading = ['PARENT_WORKPLACE_NAME','PARENT_WORKPLACE_ADDRESS','PARENT_WORKPLACE_ZIP','PARENT_WORKPLACE_CITY','PARENT_WORKPLACE_PHONE']
        self.vardcentraler_reader = csv.DictReader(self.vardcentraler_csvfh, fieldnames=self.vardcentraler_heading, delimiter=";", quotechar='"')
        self.vardcentraler_reader.next()
        self.vardcentraler_reader.next()
        self.hitta_results_h = {}
        self.summary_row_h = {
                '# GREEN' : 0,
                '# YELLOW' : 0,
                '# RED' : 0,
                '# NO_HIT' : 0,
                }

    def _parse_hitta_result (self):
        """def: _parse_hitta_result"""
        hitta_results_h = {}
        with open(directory + '/hitta_result.csv', "rb") as fh:
            heading = ['URL','SEARCH_NAME','FOUND_NAME','ADDRESS','ZIP','CITY','PHONE','WEBSITE']
            reader = csv.DictReader(fh, fieldnames=heading, delimiter=";", quotechar='"')
            reader.next()
            reader.next()
            for row_h in reader:
                if row_h['SEARCH_NAME'] not in hitta_results_h:
                    hitta_results_h[row_h['SEARCH_NAME']] = []
                row_h['HITTA_OR_ENIRO'] = "HITTA"
                hitta_results_h[row_h['SEARCH_NAME']].append(row_h)
        self.hitta_results_h = hitta_results_h

    def _parse_eniro_result (self):
        """def: _parse_eniro_result"""
        eniro_results_h = {}
        with open( directory + '/eniro_result.csv', "rb") as fh:
            heading = ['URL','SEARCH_NAME','FOUND_NAME','ADDRESS','ZIP','CITY','PHONE','WEBSITE']
            reader = csv.DictReader(fh, fieldnames=heading, delimiter=";", quotechar='"')
            reader.next()
            reader.next()
            for row_h in reader:
                if row_h['SEARCH_NAME'] not in eniro_results_h:
                    eniro_results_h[row_h['SEARCH_NAME']] = []
                row_h['HITTA_OR_ENIRO'] = "ENIRO"
                eniro_results_h[row_h['SEARCH_NAME']].append(row_h)
        self.eniro_results_h = eniro_results_h

    def _parse_primary_clinic_result (self):
        """def: _parse_primary_clinic_result"""
        primary_clinic_results_h = {}
        with open( directory + '/hitta_primary_clinic_result.csv', "rb") as fh:
            heading = ['URL','SEARCH_NAME','FOUND_NAME','ADDRESS','ZIP','CITY','PHONE','WEBSITE']
            reader = csv.DictReader(fh, fieldnames=heading, delimiter=";", quotechar='"')
            reader.next()
            reader.next()
            for row_h in reader:
                if row_h['FOUND_NAME'] not in primary_clinic_results_h:
                    primary_clinic_results_h[row_h['FOUND_NAME']] = []
                primary_clinic_results_h[row_h['FOUND_NAME']].append(row_h)
        self.primary_clinic_results_h = primary_clinic_results_h

        
    def _matching_criteria (self, string):
        """def: _matching_criteria"""
        yield re.sub('en$', '', string).lower()
        yield re.sub('s$', '', string).lower()
        yield re.sub('vårdcentral', 'hälsocentral', string).lower()
        yield re.sub('läkarcentral', 'hälsocentral', string).lower()
        yield re.sub('hälsocentral', 'vårdcentral', string).lower()
        yield re.sub('läkarcentral', 'vårdcentral', string).lower()
        yield re.sub('hälsocentral', 'läkarcentral', string).lower()
        yield re.sub('vårdcentral', 'läkarcentral', string).lower()
        
    def _compare_name (self, crow_h, vrow_h, hitta_results_row_h):
        """def: _compare_name"""
        if re.search('^\s*$', vrow_h['PARENT_WORKPLACE_NAME']) or re.search('^\s*$', hitta_results_row_h['FOUND_NAME']):
            crow_h['NAME_MATCH?'] = 'NO'
            return

        if vrow_h['PARENT_WORKPLACE_NAME'].lower() == hitta_results_row_h['FOUND_NAME'].lower():
            crow_h['NAME_MATCH?'] = 'EXACT'
        else:
            partial_match = 1
            for field in vrow_h['PARENT_WORKPLACE_NAME'].split():
                tmp_match = 0
                for name in self._matching_criteria (field):
                    if name in hitta_results_row_h['FOUND_NAME'].lower():
                        tmp_match = 1
                if tmp_match == 0: 
                    partial_match = 0
                    break
            if partial_match == 1: crow_h['NAME_MATCH?'] = 'PARTIAL'

            if 'NAME_MATCH?' not in crow_h:
                partial_match = 1
                for field in hitta_results_row_h['FOUND_NAME'].split():
                    tmp_match = 0
                    for name in self._matching_criteria (field):
                        if name in vrow_h['PARENT_WORKPLACE_NAME'].lower():
                            tmp_match = 1
                    if tmp_match == 0:
                        partial_match = 0
                        break
                if partial_match == 1: crow_h['NAME_MATCH?'] = 'PARTIAL'

            if 'NAME_MATCH?' not in crow_h:
                crow_h['NAME_MATCH?'] = 'NO'
        
    def _all_words_present (self, str1, str2):
        words = str1.split()
        match = 1
        for word in words:
            if word not in str2:
                match = 0
        if match == 1:
            return match

        words = str2.split()
        match = 1
        for word in words:
            if word not in str1:
                match = 0
        return match

    def _compare_address (self, crow_h, vrow_h, hitta_results_row_h):
        """def: _compare_zip"""
        if not hitta_results_row_h['ADDRESS']:
            hitta_results_row_h['ADDRESS'] = ""
        if not vrow_h['PARENT_WORKPLACE_ADDRESS']:
            vrow_h['PARENT_WORKPLACE_ADDRESS'] = ""

        #-------------------------------------------------------------------------------
        # Remove ,. etc charactor in address
        hitta_results_row_h['ADDRESS'] = re.sub(r'[.,]', ' ', hitta_results_row_h['ADDRESS'])
        vrow_h['PARENT_WORKPLACE_ADDRESS'] = re.sub(r'[.,]', ' ', vrow_h['PARENT_WORKPLACE_ADDRESS'])

        hitta_results_row_h['ADDRESS'] = re.sub(r'\s+', ' ', hitta_results_row_h['ADDRESS'])
        vrow_h['PARENT_WORKPLACE_ADDRESS'] = re.sub(r'\s+', ' ', vrow_h['PARENT_WORKPLACE_ADDRESS'])

        hitta_results_row_h['ADDRESS'] = re.sub(r'^\s+|\s+$', '', hitta_results_row_h['ADDRESS'])
        vrow_h['PARENT_WORKPLACE_ADDRESS'] = re.sub(r'^\s+|\s+$', '', vrow_h['PARENT_WORKPLACE_ADDRESS'])
        #-------------------------------------------------------------------------------

        if re.search('^\s*$', vrow_h['PARENT_WORKPLACE_ADDRESS']) or re.search('^\s*$', hitta_results_row_h['ADDRESS']):
            crow_h['ADDRESS_MATCH?'] = "NO"
        elif vrow_h['PARENT_WORKPLACE_ADDRESS'].lower() == hitta_results_row_h['ADDRESS'].lower():
            crow_h['ADDRESS_MATCH?'] = "EXACT"
        elif self._all_words_present (vrow_h['PARENT_WORKPLACE_ADDRESS'].lower(), hitta_results_row_h['ADDRESS'].lower()):
            crow_h['ADDRESS_MATCH?'] = "PARTIAL"
        else:
            crow_h['ADDRESS_MATCH?'] = "NO"
        
    def _compare_zip (self, crow_h, vrow_h, hitta_results_row_h):
        """def: _compare_zip"""
        if not vrow_h['PARENT_WORKPLACE_ZIP']:
            vrow_h['PARENT_WORKPLACE_ZIP'] = ""

        if not hitta_results_row_h['ZIP']:
            hitta_results_row_h['ZIP'] = ""

        if vrow_h['PARENT_WORKPLACE_ZIP'].lower() == hitta_results_row_h['ZIP'].lower():
            crow_h['ZIP_MATCH?'] = "EXACT"
        else:
            crow_h['ZIP_MATCH?'] = "NO"
        
    def _compare_city (self, crow_h, vrow_h, hitta_results_row_h):
        """def: _compare_city """
        if not vrow_h['PARENT_WORKPLACE_CITY']: vrow_h['PARENT_WORKPLACE_CITY'] = ""
        if not hitta_results_row_h['CITY']: hitta_results_row_h['CITY'] = ""
            
        hitta_results_row_h['CITY'] = string.capwords(hitta_results_row_h['CITY'])
        if vrow_h['PARENT_WORKPLACE_CITY'].lower() == hitta_results_row_h['CITY'].lower():
            crow_h['CITY_MATCH?'] = "EXACT"
        else:
            crow_h['CITY_MATCH?'] = "NO"
        
    def _compare_phone (self, crow_h, vrow_h, hitta_results_row_h):
        """def: _compare_phone """
        if not vrow_h['PARENT_WORKPLACE_PHONE']: vrow_h['PARENT_WORKPLACE_PHONE'] = ""
        if not hitta_results_row_h['PHONE']: hitta_results_row_h['PHONE'] = ""
            
        hitta_results_row_h['PHONE'] = re.sub('\s+', '', hitta_results_row_h['PHONE'])
        if re.search('^\s*$', vrow_h['PARENT_WORKPLACE_PHONE'].lower()) or re.search('^\s*$', hitta_results_row_h['PHONE'].lower()): 
            crow_h['PHONE_MATCH?'] = "NO"
        elif vrow_h['PARENT_WORKPLACE_PHONE'].lower() in hitta_results_row_h['PHONE'].lower():
            crow_h['PHONE_MATCH?'] = "EXACT"
        elif hitta_results_row_h['PHONE'].lower() in vrow_h['PARENT_WORKPLACE_PHONE'].lower():
            crow_h['PHONE_MATCH?'] = "EXACT"
        else:
            crow_h['PHONE_MATCH?'] = "NO"
        
    def _compare_rows (self, vrow_h, hitta_results_rows_h):
        """def: _compare_row"""
        for hitta_results_row_h in hitta_results_rows_h:
            crow_h = hitta_results_row_h
            self._compare_name(crow_h, vrow_h, hitta_results_row_h)
            self._compare_address(crow_h, vrow_h, hitta_results_row_h)
            self._compare_zip(crow_h, vrow_h, hitta_results_row_h)
            self._compare_city(crow_h, vrow_h, hitta_results_row_h)
            self._compare_phone(crow_h, vrow_h, hitta_results_row_h)
            yield crow_h
        

    def _get_best_matching_row_h (self, vrow_h, hitta_results_rows_h):
        """def: _get_best_matching_row_h"""
        crows_h = []
        for crow_h in self._compare_rows (vrow_h, hitta_results_rows_h):
            crows_h.append(crow_h)

        if len(crows_h) == 0: return {}
        if len(crows_h) == 1: return crows_h[0]

        logger.dump ('Found Multiple partial matches for %s' % crows_h[0]['SEARCH_NAME'])
        logger.dump ('Applying Filter to get best match')

        save_rows_h = crows_h
        filtered_rows_h = [row_h for row_h in crows_h if row_h['NAME_MATCH?'] == 'EXACT']
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        save_rows_h = filtered_rows_h
        filtered_rows_h = [row_h for row_h in filtered_rows_h if row_h['NAME_MATCH?'] == 'PARTIAL']
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        save_rows_h = filtered_rows_h
        filtered_rows_h = [row_h for row_h in filtered_rows_h if row_h['ADDRESS_MATCH?'] == 'EXACT']
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        save_rows_h = filtered_rows_h
        filtered_rows_h = [row_h for row_h in filtered_rows_h if row_h['PHONE_MATCH?'] == 'EXACT']
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        save_rows_h = filtered_rows_h
        filtered_rows_h = [row_h for row_h in filtered_rows_h if row_h['ADDRESS_MATCH?'] == 'PARTIAL']
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        # Remove sub clinic
        filtered_rows_h = [row_h for row_h in filtered_rows_h if not re.search('Distriktssköterska|mottagning', row_h['FOUND_NAME'])]
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        save_rows_h = filtered_rows_h
        filtered_rows_h = [row_h for row_h in filtered_rows_h if row_h['ZIP_MATCH?'] == 'EXACT']
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        save_rows_h = filtered_rows_h
        filtered_rows_h = [row_h for row_h in filtered_rows_h if row_h['CITY_MATCH?'] == 'EXACT']
        if len(filtered_rows_h) == 1:
            return filtered_rows_h [0]
        elif len(filtered_rows_h) == 0:
            filtered_rows_h = save_rows_h

        return filtered_rows_h [0]

    def _set_color (self, row_h):
        """def: _set_color"""
        if row_h ['ADDRESS_MATCH?'] != "NO" and row_h ['ZIP_MATCH?'] != "NO" and row_h ['CITY_MATCH?'] != "NO":
            address_match = "YES"
        else:
            address_match = "NO"

        if row_h ['NAME_MATCH?'] != "NO" and address_match != "NO" and row_h ['PHONE_MATCH?'] != "NO":
            if row_h ['VARDCENTRAL'] == "NO": row_h ['COLOR'] = "YELLOW"
            else: row_h ['COLOR'] = "GREEN"
        elif row_h ['NAME_MATCH?'] != "NO" and address_match != "NO":
            if row_h ['VARDCENTRAL'] == "NO": row_h ['COLOR'] = "YELLOW"
            else: row_h ['COLOR'] = "GREEN"
        elif address_match != "NO" and row_h ['PHONE_MATCH?'] != "NO":
            if row_h ['VARDCENTRAL'] == "NO": row_h ['COLOR'] = "YELLOW"
            else: row_h ['COLOR'] = "GREEN"
        elif row_h ['NAME_MATCH?'] != "NO" and row_h ['PHONE_MATCH?'] != "NO":
            if row_h ['VARDCENTRAL'] == "NO": row_h ['COLOR'] = "YELLOW"
            else: row_h ['COLOR'] = "GREEN"
        elif row_h ['NAME_MATCH?'] == "EXACT" or address_match == "YES":
            if row_h ['VARDCENTRAL'] == "NO": row_h ['COLOR'] = "YELLOW"
            else: row_h ['COLOR'] = "YELLOW"
        elif row_h ['NAME_MATCH?'] != "NO" or address_match != "NO":
            if row_h ['VARDCENTRAL'] == "NO": row_h ['COLOR'] = "RED"
            else: row_h ['COLOR'] = "YELLOW"
        else:
            row_h ['COLOR'] = "RED"

        if row_h ['URL'] == 'NOT FOUND':
            self.summary_row_h['# NO_HIT'] += 1
        elif row_h ['COLOR'] == "RED":
            self.summary_row_h['# RED'] += 1
        elif row_h ['COLOR'] == "YELLOW":
            self.summary_row_h['# YELLOW'] += 1
        elif row_h ['COLOR'] == "GREEN":
            self.summary_row_h['# GREEN'] += 1
            
    def _compare_vardecentraler_with_hitta (self):
        for vrow_h in self.vardcentraler_reader:
            #-------------------------------------------------------------------------------
            # Special Case
            if vrow_h['PARENT_WORKPLACE_NAME'] == 'Familjeläkarna i Sverige AB':
                vrow_h['PARENT_WORKPLACE_NAME'] = 'Familjeläkarna'
            #-------------------------------------------------------------------------------

            hitta_results_rows_h = self.hitta_results_h.get (vrow_h['PARENT_WORKPLACE_NAME'], [])
            eniro_results_rows_h = self.eniro_results_h.get (vrow_h['PARENT_WORKPLACE_NAME'], [])
            hitta_eniro_results_rows_h = hitta_results_rows_h + eniro_results_rows_h
            row_h = self._get_best_matching_row_h (vrow_h, hitta_eniro_results_rows_h)
            if row_h:
                if not row_h['FOUND_NAME']:
                    row_h['VARDCENTRAL'] = "NO"
                elif self.primary_clinic_results_h.get (row_h['FOUND_NAME'], []):
                    row_h['VARDCENTRAL'] = "YES"
                else:
                    row_h['VARDCENTRAL'] = "NO"
                self._set_color (row_h)

                csv_hitta_vardcentraler.write_row_h(row_h)

    def compare (self):
        """def: compare"""
        self._parse_hitta_result()
        self._parse_eniro_result()
        self._parse_primary_clinic_result()
        self._compare_vardecentraler_with_hitta()

        # Summary
        csv_hitta_vardcentraler_summary.write_row_h(self.summary_row_h)


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
        "NAME_MATCH?",
        "ADDRESS_MATCH?",
        "ZIP_MATCH?",
        "CITY_MATCH?",
        "PHONE_MATCH?",
        "VARDCENTRAL",
        'HITTA_OR_ENIRO',
        'COLOR',
    ]
    heading_hitta_vardcentraler_summary=[
        '# GREEN',
        '# YELLOW',
        '# RED',
        '# NO_HIT',
    ]
    m_csv_hitta_vardcentraler = csv_hitta_vardcentraler(fname= directory + '/hitta_eniro_vardcentraler_result.csv', heading=heading_hitta_vardcentraler)
    m_csv_hitta_vardcentraler_summary = csv_hitta_vardcentraler_summary(fname= directory + '/hitta_eniro_vardcentraler_result_summary.csv', heading=heading_hitta_vardcentraler_summary)

    m_hitta_compare = hitta_compare()
    m_hitta_compare.compare()









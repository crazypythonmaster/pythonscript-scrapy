#!/usr/bin/env python
# vim: set fileencoding=cp1252 :

from vardcentraler_csv import vardcentraler_csv
from logger import logger
from cp1252 import cp1252
import urllib
from lxml import html
import re
import sys, getopt
import mechanize
import cookielib
from bs4 import BeautifulSoup
from csv_writer import csv_eniro

from mech_try import mechanize_try

reload(sys)  
sys.setdefaultencoding('utf8')

class eniro(object):
    """class: eniro"""

    def _init_mech (self):
        """def: _init_mech"""
        mech = mechanize_try()
        #mech = mechanize.Browser()

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
        self.mech = self._init_mech ()

    def search_term_gen (self, vrow_h):
        """def: search_term_gen"""
        yield vrow_h['PARENT_WORKPLACE_NAME'] + ' ' + vrow_h['PARENT_WORKPLACE_ADDRESS']
        yield vrow_h['PARENT_WORKPLACE_NAME']
        #yield "%(PARENT_WORKPLACE_ADDRESS)s, %(PARENT_WORKPLACE_ZIP)s %(PARENT_WORKPLACE_CITY)s" % vrow_h
        #yield "%(PARENT_WORKPLACE_ADDRESS)s, %(PARENT_WORKPLACE_CITY)s" % vrow_h

    def _do_search (self, search_term):
        """def: _do_search"""
        search_term = cp1252(search_term)
        logger.dump ('searching %s' % search_term)

        self.mech.addheaders = [('Host', 'www.eniro.se')] 
        query = {'what': 'supersearch', 'search_word': search_term}
        url = 'http://www.eniro.se/query?' + urllib.urlencode(query)
        logger.dump ("Step1 Get: %s" % url)
        self.mech.open(url, timeout=60)

    def _first_element (self, array):
        """def: _first_element"""
        try:
            elm = array[0].decode('utf-8')
            return re.sub('\n$', '', elm)
        except Exception:
            return ""
        
    def _scrape_result (self):
        """def: _scrape_result"""
        result_h = {}
        tree = html.fromstring (self.mech.response().read())
        articles = tree.xpath ('//article[@data-hit-number]')
        for article in articles:
            article = html.fromstring (html.tostring (article))
            result_h ['URL'] = self._first_element (article.xpath('//a[contains(@class,"profile-page-link")]/@href'))
            result_h ['URL'] = "http://gulasidorna.eniro.se" + result_h ['URL']
            result_h ['FOUND_NAME'] = self._first_element (article.xpath('//a[contains(@class,"profile-page-link")]/text()'))
            result_h ['WEBSITE'] = self._first_element (article.xpath ('//a[contains(@class,"hit-homepage-link")]/text()'))
            result_h ['WEBSITE'] = re.sub('.*1177\.se.*', '', result_h ['WEBSITE'])
            result_h ['PHONE'] = self._first_element (article.xpath ('//span[contains(@class,"hit-phone-number")]/text()'))
            result_h ['PHONE'] = re.sub(r'\s+', '', result_h ['PHONE'])
            result_h ['ADDRESS'] = self._first_element (article.xpath ('//span[contains(@class,"street-address")]/text()'))
            result_h ['ZIP'] = self._first_element (article.xpath ('//span[contains(@class,"postal-code")]/text()'))
            result_h ['ZIP'] = re.sub(r'\s+', '', result_h ['ZIP'])
            result_h ['CITY'] = self._first_element (article.xpath ('//span[contains(@class,"locality")]/text()'))
            result_h = cp1252(result_h)
            yield result_h
        
    def search (self, row_h):
        """def: search"""
        for search_term in self.search_term_gen (row_h):
            self._do_search (search_term)
            if not re.search("gav ingen träff", cp1252(self.mech.response().read().decode('utf-8'))):
                break

        if re.search("gav ingen träff", cp1252(self.mech.response().read().decode('utf-8'))):
            result_h = {}
            result_h ['SEARCH_NAME'] = row_h ['PARENT_WORKPLACE_NAME']
            result_h ['URL'] = "NOT FOUND"
            csv_eniro.write_row_h(result_h)

        for result_h in self._scrape_result():
            result_h ['SEARCH_NAME'] = row_h ['PARENT_WORKPLACE_NAME']
            result_h ['MATCHING_CRITERIA'] = search_term
            csv_eniro.write_row_h(result_h)

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

    vcsv = vardcentraler_csv(directory + "/Vardcentraler.csv")
    m_eniro = eniro()

    heading_eniro=[
        'URL',
        'SEARCH_NAME',
        'FOUND_NAME',
        'ADDRESS',
        'ZIP',
        'CITY',
        'PHONE',
        'WEBSITE',
        'MATCHING_CRITERIA',
    ]

    m_csv_eniro = csv_eniro(fname= directory + '/eniro_result.csv', heading=heading_eniro)

    for row_h in vcsv.read():
        m_eniro.search(row_h)


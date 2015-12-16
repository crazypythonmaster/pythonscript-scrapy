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
from csv_writer import csv_hitta

reload(sys)  
sys.setdefaultencoding('utf8')

class hitta(object):
    """class: hitta"""
    trim_space_re = re.compile('\s+')

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
        self.mech = self._init_mech()
        self.url = None

    def _match_phone (self, tag):
        """def: _match_phone"""
            
        if tag.name != 'span': return 0
        if tag.find_previous_sibling(text=None) == None: return 0
        if tag.find_previous_sibling(text=None).name != 'span': return 0
        if 'class' not in tag.find_previous_sibling(text=None).attrs: return 0
        if tag.find_previous_sibling(text=None)['class'][0] != 'phone-label': return 0
        return 1

    def _scrape_result (self):
        """def: _scrape_result"""

        def _scrape_name (soup):
            """def: _scrape_name"""
            heading = soup.find('h1', {'itemprop': 'name'})
            if heading != None:
                return cp1252('' . join(heading.stripped_strings))
            return None
            
        def _scrape_addr (soup):
            if not soup.select('div.address-container'):
                return None
                
            addr_lines = soup.select('div.address-container')[0]
            addr_lines = addr_lines.select('div.address__line')
            addr_lines = [addr_line.string for addr_line in addr_lines if (addr_line.string != None)]
            address = "\n" . join(addr_lines)
            return cp1252(address)

        def _scrape_zip (soup):
            """def: _scrape_zip"""
            if not soup.select('div.address-container'):
                return None
            address = soup.select('div.address-container')[0]
            zipcode = soup.find('span', itemprop = 'postalCode')
            zip_str = hitta.trim_space_re.sub('', zipcode.string)
            return zip_str

        def _scrape_city (soup):
            """def: _scrape_city"""
            if not soup.select('div.address-container'):
                return None
            address = soup.select('div.address-container')[0]
            city = soup.find('span', itemprop = 'addressLocality')
            return cp1252(city.string)
            
        def _scrape_phone_number (soup):
            """def: _scrape_phone_number"""
            tree = html.fromstring (self.mech.response().read())
            phone_num = soup.find(self._match_phone)
            if phone_num == None: return phone_num 
            if 'data-bind' not in phone_num:
                phone_nums = tree.xpath ('//span[contains(@class,"phone-number")]/text()')
                if phone_nums:
                    ph_nums = [ph_num for ph_num in phone_nums if re.search('[0-9]+', ph_num)]
                    ph_nums_str = ','.join(ph_nums)
                    ph_nums_str = hitta.trim_space_re.sub('', ph_nums_str)
                    return ','.join(ph_nums)

            data = phone_num['data-bind']
            match = re.search("phoneNumber: '(.*?)'", data)
            phone_num = None
            if match != None:
                phone_num = match.group(1)
                phone_num = hitta.trim_space_re.sub('', phone_num)
            return phone_num
            
        def _scrape_home_url (soup):
            """def: _scrape_home_url"""
            website = soup.find('a', {'class': 'website'})
            if website == None: return None

            website = website.get('href', None)
            if website != None:
                website = cp1252(website)
                if re.match('/', website): website = 'http://www.hitta.se/' + website
            return website
            
        soup = BeautifulSoup(self.mech.response().read(), "html.parser")

        row_h = {}
        row_h['FOUND_NAME'] = _scrape_name (soup)
        row_h['ADDRESS'] = _scrape_addr (soup)
        row_h['ZIP'] = _scrape_zip (soup)
        row_h['CITY'] = _scrape_city (soup)
        row_h['PHONE'] = _scrape_phone_number (soup)
        row_h['WEBSITE'] = _scrape_home_url (soup)
        if row_h['WEBSITE'] and re.search('hitta\.', row_h['WEBSITE']) : row_h['WEBSITE'] = None
        if row_h['WEBSITE'] and re.search('1177\.', row_h['WEBSITE']) : row_h['WEBSITE'] = None

        return row_h
        
    def _company_links (self):
        """def: _company_links"""

        tree = html.fromstring (self.mech.response().read())
        for link in tree.xpath ('//div[@class="company-name"]/h2/a/@href'):
            yield 'http://www.hitta.se/' + link

    def _try_mech_open (self, url):
        """def: _try_mech_open"""
        while True:
            is_succeed = 0
            try:
                self.mech.open(url, timeout=60)
                is_succeed = 1
            except:
                logger.dump ("Error search: %s" % url)
                logger.dump ("RETRY: %s" % url)
            if is_succeed == 1: break
        
    def _do_search (self, search_term):
        """def: _do_search"""
        search_term = cp1252(search_term)
        logger.dump ('searching %s' % search_term)

        query = {'vad' : search_term}
        url = "http://www.hitta.se/s%C3%B6k?" + urllib.urlencode(query)
        self.url = url

        logger.dump ("Get: %s" % url)
        self._try_mech_open (url)
        tree = html.fromstring (self.mech.response().read())

        # Did You Mean
        if tree.xpath ('//a[contains(@data-track-params,"did_you_mean")]/@href'):
            href = tree.xpath ('//a[contains(@data-track-params,"did_you_mean")]/@href')[0]
            url = "http://www.hitta.se" + href
            print "Did you mean: " + url 
            self._try_mech_open (url)
            tree = html.fromstring (self.mech.response().read())

        if not tree.xpath ('//div[@class="company-name"]/h2/a/@href'):
            query = {'vad' : search_term, 'sida' : 1, 'typ' : 'ftg'}
            url = "http://www.hitta.se/s%C3%B6k?" + urllib.urlencode(query)
            logger.dump ("Get Clinic From Place: %s" % url)
            self._try_mech_open (url)


    def search (self, vrow_h):
        """def: search"""
        search_term = vrow_h['PARENT_WORKPLACE_NAME'] + ',' + vrow_h['PARENT_WORKPLACE_ADDRESS']
        self._do_search (search_term)

        #-------------------------------------------------------------------------------
        # Special Case
        if vrow_h['PARENT_WORKPLACE_NAME'] == 'Familjeläkarna i Sverige AB':
            vrow_h['PARENT_WORKPLACE_NAME'] = 'Familjeläkarna'
        #-------------------------------------------------------------------------------

        if re.search('inget resultat', self.mech.response().read()):
            logger.dump ("NO RESULT FOUND!!")
            search_term = vrow_h['PARENT_WORKPLACE_NAME']
            self._do_search (search_term)
            if re.search('inget resultat', self.mech.response().read()):
                logger.dump ("NO RESULT FOUND!!")
                logger.dump ("Searching with address, zip city!!!!")
                search_term = "%(PARENT_WORKPLACE_ADDRESS)s, %(PARENT_WORKPLACE_ZIP)s %(PARENT_WORKPLACE_CITY)s" % vrow_h
                self._do_search (search_term)
                if re.search('inget resultat', self.mech.response().read()):
                    logger.dump ("NO RESULT FOUND!!")
                    logger.dump ("Searching with address, city!!!!")
                    search_term = "%(PARENT_WORKPLACE_ADDRESS)s, %(PARENT_WORKPLACE_CITY)s" % vrow_h
                    self._do_search (search_term)
                    if re.search('inget resultat', self.mech.response().read()):
                        logger.dump ("NO RESULT FOUND!! Skipping...")
                        row_h = {}
                        row_h['URL'] = 'NOT FOUND'
                        row_h['SEARCH_NAME'] = vrow_h['PARENT_WORKPLACE_NAME']
                        csv_hitta.write_row_h(row_h)
                        return

        link_found = 0
        for link in self._company_links():
            link_found = 1

            while True:
                success = 0
                try:
                    logger.dump ("Result Get: " + link)
                    self.mech.open(link)
                    success = 1
                except Exception as error:
                    logger.dump (error)
                if success == 1: break

            row_h = self._scrape_result()
            row_h['URL'] = link
            row_h['SEARCH_NAME'] = vrow_h['PARENT_WORKPLACE_NAME']
            row_h['MATCHING_CRITERIA'] = search_term

            csv_hitta.write_row_h(row_h)

        if link_found == 0:
            row_h = self._scrape_result()
            row_h['URL'] = self.url
            row_h['SEARCH_NAME'] = vrow_h['PARENT_WORKPLACE_NAME']
            row_h['MATCHING_CRITERIA'] = search_term

            csv_hitta.write_row_h(row_h)



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
    m_hitta = hitta()

    heading_hitta=[
        'URL',
        'SEARCH_NAME',
        'FOUND_NAME',
        'ADDRESS',
        'ZIP',
        'CITY',
        'PHONE',
        'WEBSITE',
        'MATCHING_CRITERIA'
    ]

    m_csv_hitta = csv_hitta(fname= directory + '/hitta_result.csv', heading=heading_hitta)

    for row_h in vcsv.read():
        m_hitta.search(row_h)


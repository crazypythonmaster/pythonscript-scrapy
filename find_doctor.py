#!/usr/bin/env python
import mechanize
import cookielib
import re
from logger import logger
from cp1252 import cp1252
from urlparse import urlparse, parse_qs
from bs4 import BeautifulSoup
from bs4 import NavigableString

class find_doctor(object):
    """class: find_doctor"""

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

        mech.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        mech.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')] 
        return mech

    def __init__(self):
        self.mech = self._init_mech ()

    def _find_doctor (self, tag, full_name):
        """def: _find_doctor"""
        if tag.string == None: return 0

        name_fields = full_name.split()
        match = 1
        for name_field in name_fields:
            if not re.search(name_field, tag.string): match = 0

        return match
        
    def find_match (self, full_name_list):
        """def: find_match"""
        is_succeed = 0
        try:
            soup = BeautifulSoup(self.mech.response().read(), "html.parser")
            is_succeed = 1
        except:
            logger.dump ("Error Socket Timeout, Skipping")
        if is_succeed != 1: return []

        matches = []
        for full_name in full_name_list:
            tags = soup.find_all(lambda tag: self._find_doctor(tag, full_name))
            if len(tags) == 0: continue

            match = {}
            match['URL'] = self.mech.geturl()
            match['SEARCH_DOCTOR_NAME'] = full_name
            match['FOUND_DOCTOR_NAME'] = tags[0].string.encode('cp1252')
            match['FOUND_DOCTOR_TAG'] = tags[0].name
            matches.append(match)

        return matches
        
    def find (self, home_url, full_name_list):
        """def: find"""
        logger.dump ("HOME Get: %s" % home_url)

        retry_count = 1
        while retry_count <= 5:
            is_succeed = 0
            try:
                self.mech.open(home_url, timeout=60.0)
                is_succeed = 1
            except:
                logger.dump ("Error Getting: %s" % home_url)
                logger.dump ("##### RETRYING #####: %s" % home_url)
                retry_count += 1
            if is_succeed == 1: break

        if retry_count > 5:
            parsed_uri = urlparse( home_url )
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            is_succeed = 0
            try:
                self.mech.open(domain, timeout=60.0)
                is_succeed = 1
            except:
                logger.dump ("Error Getting: %s" % home_url)
                logger.dump ("### SKIPTING: %s" % home_url)
            if is_succeed == 0: return

        home_url = self.mech.geturl()
        logger.dump ("HOME URL: %s" % home_url)

        self.find_match (full_name_list)

        matches_h = {}
        for link in list(set(map(lambda x: x.absolute_url, self.mech.links()))):

            EXCLUDED_LINK_EXTENSIONS = ('jpg', 'gif', 'jpeg','pdf', 'doc', 'docx', 'ppt', 'txt', 'png', 'zip', 'rar', 'mp3')
            if link.split('.')[-1].lower() in EXCLUDED_LINK_EXTENSIONS: continue
            parsed_uri = urlparse( home_url )
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            if domain not in link:
                #domain = re.sub('https?://', '', domain)
                domain = re.sub('www\.', '', domain)
                if domain not in link: continue

            if re.search('hitta\.se', link): continue
            if re.search('google', link): continue
            if re.search('twitter', link): continue
            if re.search('itunes\.', link): continue
            if re.search('app\.eu', link): continue
            if re.search('linkedin', link): continue
            if re.search('facebook', link): continue
            if re.search('mailto:', link): continue
            if re.search('apple\.', link): continue
            if re.search('1177\.', link): continue
            # if re.search('jll\.se', link): continue # This domain hangs while getting request
            if len(matches_h) == len(full_name_list): break

            retry_count = 1;
            while retry_count <= 5:
                is_succeed = 0
                try:
                    self.mech.open(link, timeout=60.0)
                    logger.dump ("Search Get: %s" % link)
                    matches = self.find_match (full_name_list)
                    for match in matches:
                        match['HOME_URL'] = home_url
                        match['MATCH?'] = "FOUND"
                        if match['SEARCH_DOCTOR_NAME'] not in matches_h:
                            matches_h[match['SEARCH_DOCTOR_NAME']] = match
                    #if len(matches) != 0: break
                    is_succeed = 1;
                except:
                    logger.dump ("Error getting %s" % link)
                    logger.dump ("#### RETRY {} ###".format(retry_count))
                    retry_count += 1
                if is_succeed == 1: break

        for full_name in full_name_list:
            if full_name in matches_h:
                yield matches_h[full_name]
            else:
                match = {}
                match['HOME_URL'] = home_url
                match['SEARCH_DOCTOR_NAME'] = full_name
                match['MATCH?'] = 'NOT FOUND'
                yield match







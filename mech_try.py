#!/usr/bin/env python
import mechanize
from logger import logger
import os
import re

class mechanize_try(mechanize.Browser):
    """class: mechanize_try"""

    def open(self, url, data=None,
             timeout=mechanize._sockettimeout._GLOBAL_DEFAULT_TIMEOUT):
        if str(type(url)) == "<type 'str'>":
            
            success = 0
            error_303 = 0
            while success == 0 and error_303 == 0:
                try:
                    if re.search('www.eniro.se', url):
                        self.addheaders = [('Host', 'www.eniro.se')] 
                    mechanize.Browser.open(self, url, data, timeout=timeout)
                except Exception as error:
                    print "Error: {}".format(error)
                    if str(error) == 'HTTP Error 303: See Other':
                        error_303 = 1
                else:
                    success = 1

                if error_303 == 1:
                    logger.dump ('Skipping: {}'.format(url))
                    header = self.response().info()
                    location = header ['location']

                    try:
                        logger.dump ('Step2 Get: {}'.format(location))
                        self.addheaders = [('Host', 'gulasidorna.eniro.se')] 
                        mechanize.Browser.open(self, location, data, timeout=timeout)
                    except Exception as error:
                        print "Error: {}".format(error)
                        if str(error) != 'HTTP Error 404: Not Found':
                            error_303 = 0
                    else:
                        success = 1
                    
            return self.response()



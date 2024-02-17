# -*- coding: utf-8 -*-
import datetime
import logging.handlers
import os
import re
import sys
import time
from abc import ABC, abstractmethod

# Temporary file to store search result with grep
search_file_name = 'Found_url.txt'

# Log configuration --------------------------------------
LOG_FILENAME = '/tmp/CacheDns.out'

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

level = logging.NOTSET  # Par défaut, pas de log

if len(sys.argv) > 1:
    level_name = sys.argv[1]
    level = LEVELS.get(level_name, logging.NOTSET)

my_logger = logging.getLogger(__name__)
my_logger.setLevel(level)

# Add the handler
handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=1048576, backupCount=5)
# Formatter creation
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
# Add formatter to handler
handler.setFormatter(formatter)
my_logger.addHandler(handler)

handler = logging.StreamHandler()
# Formatter creation
formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s")
# Add formatter to handler
handler.setFormatter(formatter)
my_logger.addHandler(handler)
# End log configuration --------------------------------------


class FilterTreatment(ABC):
    """Abstract interface to gather specific treatment on URL file"""

    @abstractmethod
    def urlfile_read_treatment(self, my_line):
        pass

    @abstractmethod
    def urlfile_write_treatment(self, url):
        pass


class BlackListFilterTreatment(FilterTreatment):
    """BlackList file treatment"""

    def urlfile_read_treatment(self, my_line):
        """ IP address 0.0.0.0  at the beginning of each line must be removed """
        return my_line.replace('0.0.0.0 ', '', 1)

    def urlfile_write_treatment(self, url):
        """ IP address 0.0.0.0  at the beginning of each line must be added """
        my_line = "0.0.0.0 %s" % url
        return my_line


class UrlFilter(object):
    """URL list read from url file"""

    def __init__(self, name=''):
        self.url_filter = []
        self.url_filter_name = name
        self.treatment = None

    def set_treatment(self, treatment):
        self.treatment = treatment

    def read_url(self, filename):
        my_logger.debug(" UrlFilter.read_url() ".center(60, '-'))
        self.url_filter = []
        try:
            f = open(filename, "r")
            for my_line in f:
                my_line = my_line.strip('\f\n')
                if self.treatment:
                    my_line = self.treatment.urlfile_read_treatment(my_line)
                my_logger.debug('%s %s', filename, my_line)
                self.url_filter.append(my_line)
            f.close()
        except:
            my_logger.info('File "%s" not found. File shall be created.', filename)
            return 0

        return len(self.url_filter)

    def get_url(self):
        my_logger.debug(" UrlFilter.get_url() ".center(60, '-'))
        return self.url_filter

    def write_url(self, file_name):
        my_logger.debug(" UrlFilter.write_url() ".center(60, '-'))
        f = open(file_name, "w")
        for u in range(len(self.url_filter)):
            if self.treatment:
                my_line = self.treatment.urlfile_write_treatment(self.url_filter[u])
            else:
                my_line = self.url_filter[u]
            my_logger.debug(my_line)
            my_line += '\n'
            f.write(my_line)
        f.flush()
        f.close()
        return len(self.url_filter)

    def add(self, n_cache):
        """Add urls in list new_cache that don't exist in self.url_filter"""
        my_logger.debug(" UrlFilter.add() ".center(60, '-'))
        for x in range(len(n_cache)):
            if n_cache[x] not in self.url_filter:
                self.url_filter.append(n_cache[x])
                my_logger.info("New url inserted : %s" % (n_cache[x]))

    def check(self, white):
        """Delete urls in list white that exist in self.url_filter"""
        my_logger.debug(" UrlFilter.check() ".center(60, '-'))
        for x in range(len(white)):
            if white[x] in self.url_filter:
                u = self.url_filter.index(white[x])
                del self.url_filter[u]
                my_logger.info("Url deleted (whitelist) : %s" % (white[x]))


class CacheDnsStat(object):
    """Simple statistic on url found"""

    def __init__(self, mailhost, fromaddr, toaddrs, subject):
        self.file_name = 'StatsDomain'
        self.Cache_SMTP_logger = logging.getLogger('smtp')
        self.Cache_SMTP_logger.setLevel(logging.INFO)
        # Add the log message handler to the logger
        # handler = logging.handlers.SMTPHandler('rasp', 'root@jeudy', 'nicolas@jeudy.mooo.com', 'Stats domaines filtrés')
        hand = logging.handlers.SMTPHandler(mailhost, fromaddr, toaddrs, subject)
        self.Cache_SMTP_logger.addHandler(hand)

    def send_message(self, ma_date_deb, nb_new_url, nb_url):
        """
        Send a mail with simple stats
        :param ma_date_deb: Start date of the period
        :param nb_new_url: Number of new url found
        :param nb_url: Total number of url found
        :return: None
        """
        my_logger.debug(" CacheDnsStat.send_message() ".center(60, '-'))
        my_logger.debug("Start date : %s nb new url : %d total nb url : %d" % (ma_date_deb, nb_new_url, nb_url))
        ma_date_fin = datetime.datetime.today()
        ma_date_fin = str(ma_date_fin).strip('\f\n')
        ma_date_deb = str(ma_date_deb).strip('\f\n')

        text_message =  "Mesure period                          : %s - %s\n" % (ma_date_deb, ma_date_fin)
        text_message += "Number of new url found on the period  : %d\n" % nb_new_url
        text_message += "Total number of url found              : %d" % nb_url
        self.Cache_SMTP_logger.info(text_message)
        my_logger.debug("Message : \n%s" % text_message)

    def save_stats(self, pnb_start_url, pnb_end_url, pnb_measure):
        """
        Simple stats are saved in a file
        :param pnb_start_url: number of url found in the DNS cache file
        :param pnb_end_url: number of url found at the end of the script
        :param pnb_measure: number of measurements to take before sending a message to give stats

        For example, if the script to get new url from the cache is sent every 10 minutes
        To get simple stats every day, pnb_measure must be set to 144
        => 6 mesures for one hour
        => 24 x 6 = 144 mesures for a day
        """

        # File contents
        #  - start date of the period
        #  - number of measurements
        #  - nb_new_url: number of new url found in the DNS cache
        #  - nb_url: total number of url found

        my_logger.debug(" CacheDnsStat.save_stats() ".center(60, '-'))
        try:
            f = open(self.file_name, "r")
            ma_date_deb = f.readline()
            n_measure, n_new_url, n_url = f.readline(), f.readline(), f.readline()
            f.close()
            n_measure, n_new_url, n_url = int(n_measure), int(n_new_url), int(n_url)
        except:
            my_logger.info('File "%s" not found. File shall be created.', self.file_name)
            n_measure, n_new_url, n_url = 0, 0, 0
            ma_date_deb = '-'

        n_measure += 1
        n_new_url += (pnb_end_url - pnb_start_url)

        my_logger.debug("Start date : %s nb url orig : %d total nb url : %d" % (ma_date_deb, pnb_start_url, pnb_end_url))

        if n_measure == pnb_measure:
            self.send_message(ma_date_deb, n_new_url, pnb_end_url)
            n_measure = 0
            n_new_url = 0

        ma_date_deb = datetime.datetime.today()
        ma_date_deb = str(ma_date_deb).strip('\f\n')

        f = open(self.file_name, "w")
        f.write("%s\n" % ma_date_deb)
        f.write("%d\n" % n_measure)
        f.write("%d\n" % n_new_url)
        f.write("%d\n" % pnb_end_url)
        f.flush()
        f.close()


class CacheDns(object):
    """Class that manages cache DNS """

    handler = None

    def __init__(self):
        self.handler = None
        self.cache_dns = None
        self.patterns = []

    @staticmethod
    def set_handler(ha):
        my_logger.debug(" CacheDns.set_handler()() ".center(60, '-'))
        CacheDns.handler = ha

    def set_filter(self, pattern):
        my_logger.debug(" CacheDns.set_filter()() ".center(60, '-'))
        self.patterns.append(pattern)
        my_logger.debug("filters : %s" % self.patterns)

    def get_cache_dns(self):
        if CacheDns.handler:
            CacheDns.handler.init_dns_cache()
            self.cache_dns = CacheDns.handler.dns_cache_selection(self.patterns)
        else:
            my_logger.warning('Hanler not defined on CacheDns object')
        return self.cache_dns


class CacheHandler(object):
    """Class that manage DNS cache"""

    @staticmethod
    def _search_string(pattern, filename):
        my_logger.debug(" CacheHandler._search_string() ".center(60, '-'))
        search_file_string = "/bin/grep %s %s>%s" % (pattern[0], filename, search_file_name)
        my_logger.debug(search_file_string)
        os.system(search_file_string)
        for x in range(len(pattern)):
            if x:
                search_file_string = "/bin/grep %s %s>>%s" % (pattern[x], filename, search_file_name)
                my_logger.debug(search_file_string)
                os.system(search_file_string)

    @staticmethod
    def _search_url(pattern, file_name):
        my_logger.debug(" CacheHandler._search_url() ".center(60, '-'))
        f = open(file_name, 'r')
        line_with_urls_found = f.read()

        for i in range(len(pattern)):
            my_logger.debug('%d. Finding regular expression : %s ----' % (i+1, pattern[i]))
            regex = re.compile(pattern[i])
            res = regex.findall(line_with_urls_found)
            for x in range(len(res)):
                my_logger.info('Url found : %s' % res[x])
                yield res[x]

    @abstractmethod
    def set_cache_file_name(self, file_name):
        pass

    @abstractmethod
    def init_dns_cache(self):
        pass

    @abstractmethod
    def dns_cache_selection(self, pattern):
        pass


class BindCacheHandler(CacheHandler):
    """Cache manager for bind softare on Unix system"""
    # Localization of bind cache
    bind_cache_file = "/var/cache/bind/named_dump.db"
    # Regular expression to apply on pattern to get only URLs
    reg_ex = ['(.+{}).*CNAME', '(.+{})[ \t0-9]+ A', '(.+{})[ \t0-9]+\tA', 'CNAME (.+{})']

    @staticmethod
    def set_regular_expression(r):
        """To set other regular expression than default one
            Regular expression uses re module
            {} designates the pattern to search provided via the method CacheDns.set_filter()
            to get a regular expression with reg_ex[i].format(pattern) """

        BindCacheHandler.reg_ex = r

    @staticmethod
    def _date_size_cache_dns(fich):
        """Log the date and size of the cache file for bind software"""
        stat_r = os.stat(fich)
        my_time_str = datetime.datetime.fromtimestamp(stat_r.st_mtime).strftime('%d-%m-%Y %H:%M')
        my_str = "Cache DNS : {} {} {} Ko".format(fich, my_time_str, stat_r.st_size / 1024)
        my_logger.info(my_str)

    def set_cache_file_name(self, file_name):
        BindCacheHandler.bind_cache_file = file_name

    def init_dns_cache(self):
        """Update cache file of bind """
        os.system('/usr/sbin/rndc dumpdb -cache')
        time.sleep(2)
        BindCacheHandler._date_size_cache_dns(BindCacheHandler.bind_cache_file)

    def dns_cache_selection(self, pattern):
        """Select url in cache file"""
#        search_file_string = "/bin/grep .googlevideo.com %s>%s" % (bind_cache_file, search_file_name)

        # First selection to only get lines with patterns
        my_logger.debug(" dns_cache_selection() ".center(60, '-'))
        CacheHandler._search_string(pattern, BindCacheHandler.bind_cache_file)

        # Second selection to get only url with pattern
        urls_found = []
        for x in range(len(pattern)):
            pat = pattern[x].replace('.', '\\.')
            ex = []
            for i in range(len(BindCacheHandler.reg_ex)):
                ex.append(BindCacheHandler.reg_ex[i].format(pat))
            for url in CacheHandler._search_url(ex, search_file_name):
                urls_found.append(url)
        return urls_found


class TcpDumpCacheHandler(CacheHandler):
    """Cache manager for tcpdump softare on Unix system"""

    # Localization of bind cache
    bind_cache_file = "/tmp/log"

    # Regular expression to apply on pattern to get only URLs
    reg_ex = ['.* (.+{}).*']

    @staticmethod
    def set_regular_expression(r):
        """To set other regular expression than default one
            Regular expression uses re module
            {} designates the pattern to search provided via the method CacheDns.set_filter()
            to get a regular expression with reg_ex[i].format(pattern) """

        TcpDumpCacheHandler.reg_ex = r

    def set_cache_file_name(self, file_name):
        TcpDumpCacheHandler.bind_cache_file = file_name

    def init_dns_cache(self):
        """Generate log of tcpdump """
        # File tcpdump_cache_dns.sh contains the following command :
        # /usr/bin/tcpdump -n -s 0 port 53 > /tmp/log &
        # Permission is done to execute the file with sudo without password
        os.system('sudo /home/nicolas/PycharmProjects/CacheDns/tcpdump_cache_dns.sh %s' % TcpDumpCacheHandler.bind_cache_file)
        a = input("Type enter to stop tcpdump...")
        # To kill process
        # File k_tcpdump_cache_dns.sh contains the following command :
        # pkill tcpdump
        # Permission is done to execute the file with sudo without password
        # pkill doesn't work when launched from Pycharms IDE
        os.system('sudo /home/nicolas/PycharmProjects/CacheDns/k_tcpdump_cache_dns.sh')


    def dns_cache_selection(self, pattern):
        """Select url in cache file"""
        # Selection to get only url with pattern
        urls_found = []
        for x in range(len(pattern)):
            pat = pattern[x].replace('.', '\\.')
            ex = []
            for i in range(len(TcpDumpCacheHandler.reg_ex)):
                ex.append(TcpDumpCacheHandler.reg_ex[i].format(pat))
            for url in CacheHandler._search_url(ex, search_file_name):
                urls_found.append(url)
        return urls_found


if __name__ == "__main__":

    # Test
    # Launch test with following command line :
    # $ python CacheDns.py debug

    stats = CacheDnsStat('rasp','root@jeudy','nicolas@jeudy.mooo.com','Filtered url stats')
    file_not_found = UrlFilter('FileNotFound')
    nb_url = file_not_found.read_url('FileNotFound')

    whitelist = UrlFilter('white_list')
    nb_url_start = whitelist.read_url('whitelist')

    # Blacklist --------------------------------------------
    blacklist = UrlFilter('black_list')
    blacklist.set_treatment(BlackListFilterTreatment())
    nb_url_start = blacklist.read_url('blacklist')
    blacklist.write_url('blacklistbis')

    cache = CacheDns()
    h = BindCacheHandler()
    h.set_cache_file_name('named_dump.db')
    cache.set_handler(h)
    cache.set_filter('.googlevideo.com.')
    cache.set_filter('.gslb.com.')
    new_cache = cache.get_cache_dns()
    blacklist.add(new_cache)
    blacklist.check(whitelist.get_url())
    nb_url_end = blacklist.write_url('blacklistbis')

    stats.save_stats(nb_url_start, nb_url_end, 1)

    # Whitelist --------------------------------------------
    cache = CacheDns()
    h = TcpDumpCacheHandler()
    cache.set_handler(h)
    cache.set_filter('.googlevideo.com.')
    new_cache = cache.get_cache_dns()

    whitelist.add(new_cache)
    nb_url_end = whitelist.write_url('whitelistbis')



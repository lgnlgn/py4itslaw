#coding=utf-8
import sys
import logging

v = sys.version_info[0]

if v == 2:
    from StringIO import StringIO
    import urllib2 as ul
else:
    import urllib.request as ul



header_file = 'headers.txt'

LINES_PER_BLOCK = 500
TIME_EXPIRE_SEC = 3600
NUM_RETRIES = 2

NUM_TO_SLEEP = 100
SLEEP_SEC = 8

year = 2015
case_type=2
judge_type=1
verbose = True
interval = 1000
poweroff = False
proxy_enable = False


logger = logging.getLogger("itslaw_crawler")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

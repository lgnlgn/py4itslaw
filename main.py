#coding=utf-8

import sys
import os
import json
import time
from Request import ItslawRequester
from optparse import OptionParser

data_dir = os.getcwd()

LINES_PER_BLOCK = 100
court_start = 1
court_end = 3568
year = 2015
case_type=1
crawling_info = {'court_id': 0,'total_count': -1, 'finished_idx': 0, 'next_idx': 0, 'next_docid': ''}
verbose = True
interval = 500



def parse_argv():
    usage = "main.py [-y <year>][-t <caseType>][-d [dir]][-s [courtStart]][-e [courtEnd]][-v]"

    parser= OptionParser(usage)
    parser.add_option("-d", "--dir",action="store", metavar="DIR",type="string", dest="data_dir", help="data directory for saving [default = .]")
    parser.add_option("-v", action="store_true", dest="verbose", default=False,help="set it to print crawling detail")
    parser.add_option("-y","--year",action = "store",type="int",dest = "year", metavar="YEAR",  help="set year, e.g. 2015")
    parser.add_option("-t","--case",action = "store", type="choice",dest = "case_type", choices = ['1','2','3','4'], metavar="CASETYPE",  help="set caseType, in [1,2,3,4], 1 = min, 2 = xing")
    parser.add_option("-s","--start",action = "store",default = 1,type="int",dest = "court_start", metavar="COURT_START" ,help="set court_id STARTS from , [default = 1]")
    parser.add_option("-e","--end",action = "store", default = 3568, type="int",dest = "court_end", metavar="COURT_END", help="set court_id ENDS from , [default = 3568]")
    parser.add_option("-i","--interval",action = "store", default = 500, type="int",dest = "interval", metavar="INTERVAL", help="set crawling INTERVAL ms , [default = 500]")

    if len(sys.argv) == 1:
        parser.print_help()

    global court_start, court_end, verbose, data_dir, year, case_type,interval
    (options, args) = parser.parse_args()
    court_start = options.court_start
    court_end= options.court_end
    case_type = options.case_type
    year = options.year
    verbose = options.verbose
    data_dir = os.getcwd() if options.data_dir is None else options.data_dir
    if year is None or year > time.gmtime()[0] or year < 2008:
        sys.stderr.write('<year> format error! Allows integer between [2008, now] \n')
        return [None] * 7
    if court_end > 3568 or court_end < 0:
        sys.stderr.write('court_end value error! it must between [1, 3568] \n')
        return [None] * 7
    if interval <= 0 :
        sys.out.write('(interval <= 0)?!  Set it to the default (500 ms) \n')
    return court_start, court_end, verbose, data_dir, year, case_type, interval


def debug_args():
    sys.out.write("court_start\t%s\n", court_start)
    sys.out.write("court_end\t%s\n", court_end)
    sys.out.write("verbose\t%s\n", verbose)
    sys.out.write("data_dir\t%s\n", data_dir)
    sys.out.write("year    \t%s\n", year)
    sys.out.write("case_type\t%s\n", case_type)
    sys.out.write("interval\t%s\n", interval)
    sys.exit(0)


def main():
    court_start, court_end, verbose, data_dir, year, case_type, interval = parse_argv()
    if year is None or case_type is None or court_end is None:
        exit(0)

    working_dir = data_dir + os.sep + str(year) + os.sep + str(case_type)
    if not os.path.isdir(working_dir):
        os.makedirs(working_dir)

    spider = ItslawRequester(case_type, year)

    court_id = get_last_court(working_dir)
    while court_id <= court_end:
        if court_id == 0:        # only happens at the first time
            sys.stdout.write(" first time of [%s , %s]\n" %(year, case_type))
            court_id = court_start   #go to next loop
            continue
        info = read_info(working_dir, court_id)
        if info is None:         # new court
            sys.stdout.write(" new court : %d  \n" %( court_id ))
            create_info(working_dir, court_id )
            continue

        if info['total_count'] == -1:
            info = prepare_crawl(spider, court_id) # get list
            flush_info(working_dir, info)
            continue_crawl(spider, info, working_dir)           # start crawling from info
        elif info['total_count'] == info['finished_idx']:  # already finished
            pass
        else:
            continue_crawl(spider, info, working_dir)           # continue crawling from info
        court_id += 1


def continue_crawl(spider, info, working_dir):
    court_id = info['court_id']
    next_idx = info['next_idx']
    total_count = info['total_count']
    next_docid = info['next_docid']

    while next_idx <= total_count:
        ts = int(time.time() * 1000)
        content = spider.get_detail(next_idx, total_count, next_docid, court_id )
        doc = json.loads(content)
        write_down(working_dir + os.sep + str(court_id), content, next_idx)

        next_docid = doc['data']['fullJudgement'].get('nextId')
        next_docid = '' if next_docid is None else  next_docid  # set to null

        info = update_info(info, next_docid) # set next_docid into info;
        flush_info(working_dir, info)

        if next_docid == '':
            sys.stdout.write("court:%d\tfinished ! #docs:  %d -> %d \n" %(court_id, next_idx, total_count))
            info[total_count] = next_idx
            break

        if verbose:
            title = doc['data']['fullJudgement']['title']
            sys.stdout.write(str(next_idx) + "\t" + title +"\n")

        next_idx += 1
        ii = int(time.time() * 1000) - ts
        time.sleep( 0 if ii > interval else (interval - ii)/1000.0)  #  sleep a while

def update_info( info, next_docid):
    """updates info; +1 to idx then save {} to info.txt"""
    info['next_docid'] = next_docid
    info['next_idx'] += 1
    info['finished_idx'] += 1
    return info


def flush_info(writing_dir, info):
    court_id = info['court_id']
    f = open(writing_dir + os.sep + str(court_id) + os.sep + "info.txt", 'w')
    f.write(str(info))
    f.close()


def write_down(writing_dir, content, next_idx):
    block_id = int(next_idx / LINES_PER_BLOCK)
    f = open(writing_dir + os.sep + str(block_id), 'a',encoding='utf-8')
    f.write(content + "\n")
    f.close()


def get_last_court(working_dir):
    """
        get max_court_id & create a new info.txt
    """

    courts = os.listdir(working_dir)
    if len(courts) == 0:
        return 0
    # get last court
    return max(map(int, filter(str.isdigit, courts)))   # check again without else


def create_info(working_dir, court_id):
    court_dir = working_dir + os.sep + str(court_id)
    info_path = court_dir + os.sep + "info.txt"
    if not os.path.isdir(court_dir):
        os.mkdir(court_dir)   # ensure dir exits
    if not os.path.isfile(info_path):
        ci = {}
        ci.update(crawling_info)
        ci['court_id'] = court_id
        flush_info(working_dir, ci)



def read_info(working_dir, court_id):
    """ reads from info.txt"""
    court_dir = working_dir + os.sep + str(court_id)
    info_path = court_dir + os.sep + "info.txt"
    if not os.path.isdir(court_dir) or not os.path.isfile(info_path):
        return None
    f = open(info_path)
    cc = eval(f.read())
    f.close()
    return cc


def prepare_crawl(spider, court_id):
    sys.stdout.write(" =>  get_list :" + str(court_id) + "\n")
    list_result = spider.get_list(court_id)
    doc = json.loads(list_result)
    total_count = doc['data']['searchResult']['totalCount']
    if total_count != 0:
        first = doc['data']['searchResult']['judgements'][0]
        info = { 'next_docid': first['id'], 'next_idx': 1 }
    else:
        info = { 'next_docid': '', 'next_idx': 0 }
    info['court_id'] = court_id
    info['finished_idx'] = 0
    info['total_count'] = total_count
    return info


if __name__ == '__main__':
    main()



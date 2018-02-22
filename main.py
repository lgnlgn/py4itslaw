#coding=utf-8

import sys
import os
import json
import time
import logging
from Request import ItslawRequester
from Request import v
from optparse import OptionParser

data_dir = os.getcwd()

LINES_PER_BLOCK = 100
court_start = 1
court_end = 3568
year = 2015
case_type=2
judge_type=1
crawling_info = {'court_id': 0,'total_count': -1, 'finished_idx': 0, 'next_idx': 0, 'next_docid': '', 'next_area': '0'}
verbose = True
interval = 1000

logger = logging.getLogger("itslaw_crawler")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')

usage = "main.py [-y <year>][-t <caseType>][-j <judgeType>][-d [dir]][-s [courtStart]][-e [courtEnd]][-v]"
parser= OptionParser(usage)
# 文件日志


def parse_argv():
    usage = "main.py [-y <year>][-t <caseType>][-j <judgeType>][-d [dir]][-s [courtStart]][-e [courtEnd]][-v]"

    parser= OptionParser(usage)
    parser.add_option("-d", "--dir",action="store", metavar="DIR",type="string", dest="data_dir", help="data directory for saving [default = .]")
    parser.add_option("-v", action="store_true", dest="verbose", default=False,help="set it to print crawling detail")
    parser.add_option("-y","--year",action = "store",type="int",dest = "year", metavar="YEAR",  help="set year, e.g. 2015")
    parser.add_option("-t","--case",action = "store", type="choice",dest = "case_type", choices = ['1','2','3','4'], metavar="CASETYPE",  help=u"set caseType, in [1,2,3,4], 民事刑事行政执行")
    parser.add_option("-j","--judge",action = "store", type="choice",dest = "judge_type", choices = ['1','2','3','4','5'], metavar="JUDGETYPE",  help=u"set judgeType, in [1,2,3,4,5], 判决裁定通知决定调解")
    parser.add_option("-s","--start",action = "store",default = 1,type="int",dest = "court_start", metavar="COURT_START" ,help="set court_id STARTS from max(COURT_START, already_done), [default = 1] ")
    parser.add_option("-e","--end",action = "store", default = 3568, type="int",dest = "court_end", metavar="COURT_END", help="set court_id ENDS from , [default = 3568]")
    parser.add_option("-i","--interval",action = "store", default = 1000, type="int",dest = "interval", metavar="INTERVAL", help="set crawling INTERVAL ms , [default = 1000]")

    if len(sys.argv) == 1:
        parser.print_help()

    global court_start, court_end, verbose, data_dir, year, case_type, judge_type, interval
    (options, args) = parser.parse_args()
    court_start = options.court_start
    court_end= options.court_end
    case_type = options.case_type
    year = options.year
    verbose = options.verbose
    judge_type = options.judge_type
    interval = options.interval
    data_dir = os.getcwd() if options.data_dir is None else options.data_dir
    if year is None or year > time.gmtime()[0] or year < 2008:
        sys.stderr.write('!!! <year> format error! Allows integer between [2008, now] \n')
        return [None] * 8
    if court_end > 3568 or court_end < 0:
        sys.stderr.write('!!! court_end value error! it must between [1, 3568] \n')
        return [None] * 8
    if judge_type is None or case_type is None:
        sys.stderr.write('!!! <caseType>  <judgeType> needs to be set \n')
        return [None] * 8
    if interval <= 0:
        sys.stdout.write('(interval <= 0)?!  Set it to the default (1000 ms) \n')
    return court_start, court_end, verbose, data_dir, year, case_type, judge_type, interval


def debug_args():
    sys.stdout.write("court_start\t%s\n"% court_start)
    sys.stdout.write("court_end\t%s\n"% court_end)
    sys.stdout.write("verbose  \t%s\n"% verbose)
    sys.stdout.write("data_dir\t%s\n"% data_dir)
    sys.stdout.write("year    \t%s\n"% year)
    sys.stdout.write("case_type\t%s\n"% case_type)
    sys.stdout.write("judge_type\t%s\n"% judge_type)
    sys.stdout.write("interval\t%s\n"% interval)

    sys.exit(0)


def main():
    court_start, court_end, verbose, data_dir, year, case_type, judge_type, interval = parse_argv()
    if year is None or case_type is None or court_end is None:
        parser.print_help()
        exit(0)
    # debug_args()
    working_dir = data_dir + os.sep + str(year) + os.sep + case_type + "_" + judge_type
    file_handler = logging.FileHandler(data_dir + os.sep + "log.log")
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    logger.addHandler(file_handler)

    logger.info("starting")

    if not os.path.isdir(working_dir):
        os.makedirs(working_dir)

    spider = ItslawRequester(year, case_type, judge_type)

    court_id = get_last_court(working_dir)
    while court_id <= court_end:  # we will use a court-mapping in the future
        if court_id == 0:         # only happens at the first time
            sys.stdout.write(" first time of [%s , %s]\n" %(year, case_type))
            court_id = court_start   # go to next loop
            continue
        info = read_info(working_dir, court_id)
        if info is None:         # new court
            sys.stdout.write(" new court : %d  \n" %( court_id ))
            create_info(working_dir, court_id )
            continue

        if info['total_count'] == -1:
            try:
                info = prepare_crawl(spider, court_id) # get list
            except:
                logger.error("prepare_crawl error!! retrying")
                time.sleep(30)
                info = prepare_crawl(spider, court_id)  # get list
            flush_info(working_dir, info)
            continue
            # continue_crawl(spider, info, working_dir)           # start crawling from info
        elif info['total_count'] == info['finished_idx'] or info['next_docid'] == '-':  # already finished
            pass
        else:
            sys.stdout.write("continue crawl: %s \n" % str(info))
            continue_crawl(spider, info, working_dir)           # continue crawling from info
        court_id += 1
    # special courts 3647: 北京专利法院
    for court_id in [3647, 3690, 3691]:
        create_info(working_dir, court_id)
        info = prepare_crawl(spider, court_id)
        flush_info(working_dir, info)
        continue_crawl(spider, info, working_dir)


def continue_crawl(spider, info, working_dir):
    court_id = info['court_id']
    next_idx = info['next_idx']
    total_count = info['total_count']
    next_docid = info['next_docid']
    next_area = info['next_area']
    retries = 1
    crawled_num = 0
    while True:  # do not use totalCount for boundary
        ts = int(time.time() * 1000)
        try:
            content = spider.get_detail(next_idx, total_count, court_id, next_area, next_docid)
            crawled_num += 1
            retries = 1
        except:
            sys.stderr.write(" get_detail error####### remaining: %d retries\n" %retries)
            logger.exception(" get_detail error####### remaining: %d retries\n" %retries)
            time.sleep(30)
            if retries:
                retries -= 1
                continue  # re-crawl if http exception
            else:
                raise RuntimeError(' spider fetch error !!%d '%retries)

        doc = json.loads(content)
        write_down(working_dir + os.sep + str(court_id), content, next_idx)

        next_docid = doc['data']['fullJudgement'].get('nextId')
        next_docid = '-' if next_docid is None else next_docid  # set to null
        next_area = doc['data']['fullJudgement'].get('nextArea')

        info = update_info(info, next_docid, next_area) # set next_docid into info;
        flush_info(working_dir, info)

        if verbose:
            sys.stdout.write("%d\t%s\n"%(next_idx, next_docid))

        if next_docid == '-':
            sys.stdout.write("court:%d\tfinished ! #docs:  %d -> %d \n" %(court_id, total_count, next_idx))
            info[total_count] = next_idx
            if next_idx < total_count:
                logger.warning("court:%d\tfinished ! #docs:  %d -> %d \n" % (court_id, total_count, next_idx))
            break

        next_idx += 1
        if crawled_num % 200 == 0:
            sys.stdout.write("sleep a while!\n")
            time.sleep(30)
        ii = int(time.time() * 1000) - ts
        time.sleep(0 if ii > interval else (interval - ii)/1000.0)  #  sleep a while


def update_info( info, next_docid, next_area):
    """updates info; +1 to idx then save {} to info.txt"""
    info['next_docid'] = next_docid
    info['next_area'] = next_area
    info['next_idx'] += 1
    info['finished_idx'] += 1
    return info


def flush_info(writing_dir, info):
    court_id = info['court_id']
    f = open(writing_dir + os.sep + str(court_id) + os.sep + "info.txt", 'w')
    f.write(str(info))
    f.close()


def write_down(writing_dir, content, next_idx):
    block_id = int((next_idx - 1) / LINES_PER_BLOCK)
    if v == 2:
        f = open(writing_dir + os.sep + str(block_id), 'a')
    else:
        f = open(writing_dir + os.sep + str(block_id), 'a', encoding='utf-8')
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
    list_result = spider.get_list(court_id)
    doc = json.loads(list_result)
    total_count = doc['data']['searchResult']['totalCount']
    page_area = doc['data']['searchResult']['pageArea']
    if total_count != 0:
        first = doc['data']['searchResult']['judgements'][0]
        info = {'next_docid': first['id'], 'next_idx': 1 }
    else:
        info = {'next_docid': '', 'next_idx': 0 }
    info['court_id'] = court_id
    info['finished_idx'] = 0
    info['total_count'] = total_count
    info['next_area'] = page_area
    sys.stdout.write(" \tcourt:%d  get_list : total count=>%d\n"%(court_id, total_count))
    return info


if __name__ == '__main__':
    main()



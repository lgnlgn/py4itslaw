#coding=utf-8

import subprocess
import json
import atexit
import platform


from proxy_tool import *
from Request import ItslawRequester
from optparse import OptionParser


data_dir = os.getcwd()
os.chdir(data_dir)


usage = "main.py [-y <year>][-t <caseType>][-j <judgeType>][-d [dir]][-v][-p][-s]"
parser= OptionParser(usage)
# 文件日志


def parse_argv():
    parser.add_option("-d", "--dir",action="store", metavar="DIR",type="string", dest="data_dir", help="data directory for saving [default = .]")
    parser.add_option("-v", action="store_true", dest="verbose", default=False, help="set it to print crawling detail")
    parser.add_option("-y","--year",action = "store",type="int",dest = "year", metavar="YEAR",  help="set year, e.g. 2015")
    parser.add_option("-t","--case",action = "store", type="choice",dest = "case_type", choices = ['1','2','3','4'], metavar="CASETYPE",  help=u"set caseType, in [1,2,3,4], 民事刑事行政执行")
    parser.add_option("-j","--judge",action = "store", type="choice",dest = "judge_type", choices = ['1','2','3','4','5'], metavar="JUDGETYPE",  help=u"set judgeType, in [1,2,3,4,5], 判决裁定通知决定调解")
    parser.add_option("-p", "--proxy", action="store_true", dest="proxy", default=False, help="set it to enable proxy")
    parser.add_option("-i","--interval",action = "store", default = 1000, type="int",dest = "interval", metavar="INTERVAL", help="set crawling INTERVAL ms , [default = 1000]")
    parser.add_option("-s","--shutdown",action = "store_true",dest = "poweroff", default=False, help="set it to poweroff whether task finished or interupted")

    if len(sys.argv) == 1:
        parser.print_help()

    global verbose, data_dir, year, case_type, judge_type, interval, poweroff, proxy_enable

    (options, args) = parser.parse_args()
    case_type = options.case_type
    year = options.year
    verbose = options.verbose
    judge_type = options.judge_type
    interval = options.interval
    poweroff = options.poweroff
    proxy_enable = options.proxy

    data_dir = os.getcwd() if options.data_dir is None else options.data_dir
    if year is None or year > time.gmtime()[0] or year < 1995:
        sys.stderr.write('!!! <year> format error! Allows integer between [1995, now] \n')
        return [None] * 8
    if judge_type is None or case_type is None:
        sys.stderr.write('!!! <caseType>  <judgeType> needs to be set \n')
        return [None] * 8
    if interval <= 0:
        sys.stdout.write('(interval <= 0)?!  Set it to the default (1000 ms) \n')
    return proxy_enable, verbose, data_dir, year, case_type, judge_type, interval, poweroff


def debug_args(exit0=True):
    sys.stdout.write("proxy_enable\t%s\n" % proxy_enable)
    sys.stdout.write("verbose    \t%s\n"% verbose)
    sys.stdout.write("data_dir   \t%s\n"% data_dir)
    sys.stdout.write("year       \t%s\n"% year)
    sys.stdout.write("case_type  \t%s\n"% case_type)
    sys.stdout.write("judge_type \t%s\n"% judge_type)
    sys.stdout.write("interval   \t%s\n"% interval)
    sys.stdout.write("poweroff   \t%s\n" % poweroff)
    sys.stdout.flush()
    if exit0:
        sys.exit(0)


def crawl_courts(data_dir, year, case_type, judge_type, spider):
    year_dir = data_dir + os.sep + str(year)
    court_id = fetch_court(year_dir, case_type, judge_type, goto_end =True)
    while court_id < 3569:
        court_id += 1
        info = prepare_crawl(spider, court_id)
        save_courts(year_dir, case_type, judge_type, info)
        time.sleep(0.5)
    ncourts = [3569, 3647, 3690, 3691]
    while ncourts.index( court_id) < len(ncourts) - 1 :
        court_id = ncourts[ncourts.index( court_id) + 1]
        info = prepare_crawl(spider, court_id)
        save_courts(year_dir, case_type, judge_type, info)


def continue_crawl(spider, info, working_dir):
    court_id = info['court_id']
    next_idx = info['next_idx']
    total_count = info['total_count']
    next_docid = info['next_docid']
    next_area = info['next_area']
    crawled_num = 0
    while True:  # do not use totalCount for boundary
        ts = int(time.time() * 1000)

        content = spider.get_detail(next_idx, total_count, court_id, next_area, next_docid)
        crawled_num += 1

        doc = json.loads(content)
        if doc['result']['code'] != 0:
            sys.stdout.write(doc['result']['message']+ "\n" )
            sys.stdout.flush()
            time.sleep(2)
            continue
        write_down(working_dir + os.sep + str(court_id), content, next_idx)

        next_docid = doc['data']['fullJudgement'].get('nextId')
        next_docid = '-' if next_docid is None else next_docid  # set to null
        next_area = doc['data']['fullJudgement'].get('nextArea')

        info = update_info(info, next_docid, next_area) # set next_docid into info;
        flush_info(working_dir, info)

        if verbose:
            sys.stdout.write("%d\tnext:%s\n"%(next_idx, next_docid))

        if next_docid == '-':
            sys.stdout.write("court:%d\tfinished ! #docs:  %d -> %d \n" %(court_id, total_count, next_idx))
            if next_idx < total_count:
                logger.warning("court:%d\tfinished ! #docs:  %d -> %d \n" % (court_id, total_count, next_idx))
            break

        next_idx += 1
        if crawled_num % NUM_TO_SLEEP == 0:
            sys.stdout.write("sleep a while & update local header! current court:%d\n" % court_id)
            time.sleep(SLEEP_SEC / 2)
        ii = int(time.time() * 1000) - ts

        time.sleep(0 if ii > interval else (interval - ii)/1000.0)  # sleep a while
    #finished


def prepare_crawl(spider, court_id):
    while True:
        list_result = spider.get_list(court_id)

        try:
            doc = json.loads(list_result)
            total_count = doc['data']['searchResult']['totalCount']
            page_area = doc['data']['searchResult']['pageArea']
            if total_count != 0:
                first = doc['data']['searchResult']['judgements'][0]
                info = {'next_docid': first['id'], 'next_idx': 1}
            else:
                info = {'next_docid': '', 'next_idx': 0}
            info['court_id'] = court_id
            info['finished_idx'] = 0
            info['total_count'] = total_count
            info['next_area'] = page_area
            logger.info(" \tcourt:%d  get_list : total count=>%d\n" % (court_id, total_count))
            return info
        except Exception as e:
            print("error parse doc:", doc)
            time.sleep(0.5)
            continue



def shutdown():
    if poweroff:
        sysstr = platform.system()
        if (sysstr == "Windows"):
            os.system("shutdown -s -t 30")
        elif (sysstr == "Linux"):
            os.system("shutdown -t 5 1")
        else:
            pass


def start_and_watch(data_dir, year, case_type, judge_type, proxy_pool = None):

    terminal = crawl_proc.poll()
    last_cp = current_progress("%s/%s" % (data_dir, year), case_type, judge_type)
    last_tick = time.time()
    last_proxy_t = time.time()
    cc = 0
    while terminal is None:
        cp = current_progress("%s/%s" % (data_dir, year), case_type, judge_type)
        if cp == last_cp:
            c_tick = time.time()  ##
            if c_tick - last_tick > 100:  ## stuck
                daemon_f.write("stay %d \t [%s] finished!\n" % (cc, time.asctime()))
                break
            else:
                daemon_f.write("check %d \t [%s]\n" % (cc, time.asctime()))
                daemon_f.flush()
                cc += 1
                pass  # not stuck
        else:  # {info} not equals : re-check
            last_tick = time.time()
            cc = 0
        if proxy_pool and time.time() - last_proxy_t > 600:
            proxy_pool.crawl()
            last_proxy_t = time.time()
        last_cp = cp
        time.sleep(interval * 2 / 1000.0)
        terminal = crawl_proc.poll()


def mkdirs(*auguments):
    paths = [os.sep.join(auguments[0:k]) for k in range(1,len(auguments) + 1)]
    for p in paths :
        if not os.path.isdir(p):
            os.mkdir(p)


def main():
    working_dir = data_dir + os.sep + str(year) + os.sep + case_type + "_" + judge_type
    year_dir = data_dir + os.sep + str(year)

    file_handler = logging.FileHandler(data_dir + os.sep + "log.log")
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    logger.addHandler(file_handler)
    logger.info("starting")

    if not os.path.isdir(working_dir):
        os.makedirs(working_dir)

    spider = ItslawRequester(year, case_type, judge_type, proxy_enable)

    crawl_courts(data_dir, year, case_type, judge_type, spider)  # crawl COURT_LIST first

    court_id = fetch_court(year_dir, case_type, judge_type) #fetch again; 0 if meets the end
    while court_id != 0:  # from COURT_LIST
        dir_info = read_info(working_dir, court_id)
        if dir_info is None or dir_info['next_docid'] == '-' or dir_info['next_idx'] == 0:  # just new or re-crawl-task( finished but 0 manually. )
            dir_info = prepare_crawl(spider, int(court_id))  # get list
            flush_info(working_dir, dir_info, delete = True)
        sys.stdout.write('now :%s\n' % court_id)
        if dir_info['next_idx'] > 0:
            continue_crawl(spider, dir_info, working_dir)  # continue crawling from info
        save_courts(year_dir, case_type, judge_type, dir_info, True)

        court_id = fetch_court(year_dir, case_type, judge_type)
    sys.stdout.write('finish!!!!!')
    sys.stdout.flush()

if __name__ == '__main__':

    proxy_enable, verbose, data_dir, year, case_type, judge_type, interval, poweroff = parse_argv()
    if year is None or case_type is None:
        parser.print_help()
        exit(0)

    args_str = ' '.join(sys.argv[:])
    sys.stdout.write(args_str + "\n")
    mkdirs(data_dir, str(year), case_type + "_" + judge_type)

    if args_str.count(" main_crawling_process") > 0:
        sys.stdout.write(" main crawling ")
        debug_args(False)
        main()
    else:
        if proxy_enable:
            pp = ProxyPool()
            pp.crawl()
        else:
            pp = None
        fetch_cookie(pp)
        sys.stdout.write(" DAEMON PROCESS ENTERED ")
        atexit.register(shutdown)  ##register shutdown
        daemon_f = open(data_dir + "/daemon.log", 'w')
        args_str += " main_crawling_process"
        crawl_proc = subprocess.Popen("python " + args_str) #run main-crawling program
        if v == 2:
            try:
                start_and_watch(data_dir, year, case_type, judge_type, pp)
            except Exception:
                traceback.print_exc()
                logger.exception('error !')
            finally:
                logger.warning("KeyboardInterrupt")
                daemon_f.close()
                crawl_proc.kill()

        else:
            try:
                start_and_watch(data_dir, year, case_type, judge_type, pp)
            except Exception as e:
                logger.exception('error !', exc_info=e)
            finally:
                logger.warning("KeyboardInterrupt")
                daemon_f.close()
                crawl_proc.kill()







#coding=utf-8

import sys
import os
from Request import ItslawRequester
import json

data_dir = os.getcwd()
COURT_MAX = 3568
court_start = 1

crawling_info = {'court_id':0,'total_count': -1, 'finished_idx': 0, 'next_idx':0, 'next_docid': ''}



def process_argv():
    argvs = len(sys.argv)
    if argvs < 3 or argvs > 4:
        sys.stdout("python main.py <year> <caseType> [data_dir]")
        sys.stdout("<caseType> : 1 = min, 2 = xing; default data_dir is './' ")
        return None,None
    else:
        year = sys.argv[1]
        case_type = sys.argv[2]
        if len(year) != 4 or not year.isdigit() or year[0] != '2':
            sys.stdout("<year> must be an integer and greater than 2000 ")
            return None,None
        if len(case_type) != 1 or not case_type.isdigit():
            sys.stdout("<caseType> : 1 = min, 2 = xing;")
            return None,None
        if argvs == 4:
            data_dir = sys.argv[3]
            sys.stdout(" set data_dir => " + data_dir)
        return year, case_type


def main():
    year, case_type = process_argv()
    if year is None or case_type is None:
        return
    working_dir = data_dir + os.sep + year + os.sep + case_type
    os.makedirs(working_dir)

    spider = ItslawRequester(case_type, year)

    court_id = get_last_court(working_dir)
    while court_id <= COURT_MAX:
        if court_id == 0 : # only happens at the first time
            create_info(working_dir, court_id + 1 )
            court_id += 1
        info = read_info(working_dir, court_id)
        if info['total_count'] == -1 :
            info = prepare_crawling(spider, court_id)
            continue_crawl(info)

        elif (info['total_count'] == info['finished_idx'] ):
            pass
        else:
            continue_crawl(info)
        court_id += 1
    # new court -> start
    # new court -> stop
    # continuous -> start
    # continuous & last -> stop



def continue_crawl(info):
    # TODO
    pass

def get_last_court(working_dir):
    """
        get max_court_id & create a new info.txt
    """

    courts = os.listdir(working_dir)
    if len(courts) == 0:
        os.mkdir(working_dir + os.sep + str(court_start)) #create first court
    # get last court
    max_court_id = max(map(int,  os.listdir(working_dir)))   # check again without else

    info = read_info(working_dir, max_court_id)

    return info

def create_info(working_dir, court_id):
    if not os.path.isfile:
        ci = {}
        ci.update(crawling_info)
        ci['court_id'] = court_id
        f = open(working_dir + os.sep + str(court_id) + os.sep + "info.txt")
        f.write(str(ci))
        f.close()

def read_info(working_dir, court_id):
    """ reads from info.txt"""
    if not os.path.isfile:
        return None
    f = open(working_dir + os.sep + str(court_id) + os.sep + "info.txt")
    cc = eval(f.read())
    f.close()
    return cc
##    if cc['total_count'] == 0 or cc['total_count'] == cc['finished_idx']: ##end
##        return -1,''
##    else:
##        return cc['next_idx'], cc['next_docid']


def prepare_crawling(spider, court_id):

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
    working_dir = data_dir + os.sep + year + os.sep + case_type
    os.makedirs(working_dir)



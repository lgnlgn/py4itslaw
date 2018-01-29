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


def parse_list(list_result):
    doc = json.loads(list_result)
    total_count = doc['data']['totalCount']
    next_id = ''
    # TODO
    info = {'total_count': total_count, 'next_docid': next_id, 'next_idx': 1}
    return info

def main():
    year, case_type = process_argv()
    if year is None or case_type is None:
        return
    working_dir = data_dir + os.sep + year + os.sep + case_type
    os.makedirs(working_dir)

    spider = ItslawRequester(case_type, year)

    court_id = get_last_court(working_dir)
    next_idx, next_doc = read_info(working_dir, court_id)
    # new court -> start
    # new court -> stop
    # continuous -> start
    # continuous & last -> stop
    info = prepare_crawling(court_id, next_idx, next_doc, spider)




def get_last_court(working_dir):
    """
        get max_court_id & create a new info.txt
    """

    courts = os.listdir(working_dir)
    if len(courts) == 0:
        os.mkdir(working_dir + os.sep + str(court_start)) #create first court
        crawling_info['court_id'] = court_start
        f = open(working_dir + os.sep + str(court_start) + os.sep + "info.txt")
        f.write(str(crawling_info))
        f.close()

    # get last court
    max_court_id = max(map(int,  os.listdir(working_dir)))   # check again without else
    return max_court_id


def read_info(working_dir, court_id):
    """ reads from info.txt"""
    f = open(working_dir + "/" + str(court_id) + "/info.txt")
    cc = eval(f.read())
    if cc['total_count'] == 0 or cc['total_count'] == cc['finished_idx']: ##end
        return -1,''
    else:
        return cc['next_idx'], cc['next_docid']


def prepare_crawling(court_id, next_idx, next_doc, spider):
    ci = {}
    ci.update(crawling_info)
    if court_id == court_start and next_idx == 0: #call spider.get_list()
        list_result = spider.get_list(court_id)
        info = parse_list(list_result)
        info['court_id'] = court_id
    else:
        ci

    ci.update(info)
    return ci



if __name__ == '__main__':
    working_dir = data_dir + os.sep + year + os.sep + case_type
    os.makedirs(working_dir)



#coding=utf-8

import sys
import os
from Request import ItslawRequester


data_dir = os.getcwd()
COURT_MAX = 3568
year = '2014'
case_type = '1'

crawling_info = {'court_id':0,'total_count': -1, 'finished_idx': 0, 'next_idx':0, 'next_docid': ''}

def process_argv():
    argvs = len(sys.argv)
    if argvs < 3 or argvs > 4:
        sys.stdout("python main.py <year> <caseType> [data_dir]")
        sys.stdout("<caseType> : 1 = min, 2 = xing; default data_dir is './' ")
        return None,None
    else :
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

    spider = ItslawRequester(caseType, year)

    court_id = get_last_court(working_dir)
    next_idx, next_doc = continue_last(working_dir, court_id)

    if court_id == 1 and next_idx == 0: #call spider.get_last()
        pass



def get_last_court(working_dir):
    courts = os.listdir(working_dir)
    if len(courts) == 0:
        court = 1
        os.mkdir(working_dir + "/1") #create first court
        crawling_info['court_id'] = court
        f = open(working_dir + "/1/info.txt")
        f.write(str(crawling_info))
        f.close()
    else:
        court = max(map(int, courts))
    return court

def continue_last(working_dir, court_id):
    f = open(working_dir + "/" + str(court_id) + "/info.txt")
    cc = eval(f.read())
    if cc['total_count'] == 0 or cc['total_count'] == cc['finished_idx']: ##end
        return -1,''
    else:
        return cc['next_idx'], cc['next_docid']

if __name__ == '__main__':
    working_dir = data_dir + os.sep + year + os.sep + case_type
    os.makedirs(working_dir)



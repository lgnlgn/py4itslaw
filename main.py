#coding=utf-8

import sys
import os
from Request import ItslawRequester
import json

data_dir = os.getcwd()
COURT_MAX = 3568
LINES_PER_BLOCK = 100
court_start = 1

crawling_info = {'court_id': 0,'total_count': -1, 'finished_idx': 0, 'next_idx': 0, 'next_docid': ''}
verbose = True


def process_argv():
    global data_dir
    argvs = len(sys.argv)
    if argvs < 3 or argvs > 4:
        sys.stdout.write("python main.py <year> <caseType> [data_dir]\n")
        sys.stdout.write("<caseType> : 1 = min, 2 = xing; default data_dir is './' \n")
        return None, None
    else:
        year = sys.argv[1]
        case_type = sys.argv[2]
        if len(year) != 4 or not year.isdigit() or year[0] != '2':
            sys.stdout.write("<year> must be an integer and greater than 2000 \n")
            return None,None
        if len(case_type) != 1 or not case_type.isdigit():
            sys.stdout.write("<caseType> : 1 = min, 2 = xing;\n")
            return None,None
        if argvs == 4:
            data_dir = sys.argv[3]
            sys.stdout.write(" set data_dir => " + data_dir + "\n")
        return year, case_type


def main():
    year, case_type = process_argv()
    if year is None or case_type is None:
        return
    working_dir = data_dir + os.sep + year + os.sep + case_type
    if not os.path.isdir(working_dir):
        os.makedirs(working_dir)

    spider = ItslawRequester(case_type, year)

    court_id = get_last_court(working_dir)
    while court_id <= COURT_MAX:
        if court_id == 0:        # only happens at the first time
            os.mkdir(working_dir + os.sep + str(court_start))
            sys.stdout.write(" first time of [%s , %s]\n" %(year, case_type))
            create_info(working_dir, court_id + 1 )
            court_id = court_start
        info = read_info(working_dir, court_id)
        if info is None:         # new court
            sys.stdout.write(" new court : %d  \n" %( court_id ))
            create_info(working_dir, court_id )
        if info['total_count'] == -1:
            info = prepare_crawl(spider, court_id) # get list

            continue_crawl(spider, info)           # start crawling from info

        elif info['total_count'] == info['finished_idx']:  # already finished
            pass
        else:
            continue_crawl(info)                   # continue crawling from info
        court_id += 1


def continue_crawl(spider, info, working_dir):
    court_id = info['court_id']
    next_idx = info['next_idx']
    total_count = info['total_count']
    next_docid = info['next_docid']
    update_info(working_dir, info, next_docid)
    while next_idx < total_count:
        content = spider.get_detail(next_idx, total_count, next_docid, court_id )
        doc = json.loads(content)
        next_docid = doc['data']['fullJudegment']['nextId']

        write_down(working_dir + os.sep + str(court_id), content, next_idx)
        info = update_info(working_dir, info, next_docid) # set next_docid into info;

        if verbose:
            doc = json.loads(content)
            title = doc['data']['fullJudegment']['title']
            sys.stdout.write(str(next_idx) + "\t" + title +"\n")

        next_idx += 1

def update_info(writing_dir, info, next_docid):
    """updates info; +1 to idx then save {} to info.txt"""
    info['next_docid'] = next_docid
    info['next_idx'] += 1
    info['finished_idx'] += 1
    f = open(writing_dir + os.sep + "info.txt", 'w')
    f.write(str(info))
    f.close()
    return info


def write_down(writing_dir, content, next_idx):
    block_id = next_idx / LINES_PER_BLOCK
    f = open(writing_dir + os.sep + str(block_id), 'a')
    f.write(content + '\n')
    f.close()


def get_last_court(working_dir):
    """
        get max_court_id & create a new info.txt
    """

    courts = os.listdir(working_dir)
    if len(courts) == 0:
        return 0
        # os.mkdir(working_dir + os.sep + str(court_start)) # create first court's dir
    # get last court
    return max(map(int, courts))   # check again without else
    # return max_court_id if max_court_id else 0


def create_info(working_dir, court_id):
    court_dir = working_dir + os.sep + str(court_id)
    info_path = court_dir + os.sep + "info.txt"
    if not os.path.isdir(court_dir):
        os.mkdir(court_dir)   # ensure dir exits
    if not os.path.isfile(info_path):
        ci = {}
        ci.update(crawling_info)
        ci['court_id'] = court_id
        f = open(info_path, 'w')
        f.write(str(ci))
        f.close()



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



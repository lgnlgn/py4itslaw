import time
import os
import sys

v = sys.version_info[0]
header_file = 'headers.txt'
LINES_PER_BLOCK = 100
TIME_EXPIRE_SEC = 1800
crawling_info = {'court_id': 0,'total_count': -1, 'finished_idx': 0, 'next_idx': 0, 'next_docid': '', 'next_area': '0'}


def load_header():
    with open( header_file) as f:
        hh = f.read()
    return dict([h.strip().split(":", 1) for h in hh.strip().split('\n')])


def update_header():
    headers = load_header()
    headers['time'] =  str(int(time.time()))
    with open(header_file, 'w') as f:
        for k, v in headers.items():
            f.write("%s:%s\n" % (k, v))


def update_info( info, next_docid, next_area):
    """updates info; +1 to idx then save {} to info.txt"""
    info['next_docid'] = next_docid
    info['next_area'] = next_area
    info['next_idx'] += 1
    info['finished_idx'] += 1
    info['time'] = time.asctime()
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


def ck_deprecated():
    headers = load_header()
    tm =  headers.get('time')
    if tm is None:
        cookies = headers.setdefault("Cookie","Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1520693568").split('; ')
        vv = filter(lambda x : x[1].isdigit(),  [x.split('=') for x in cookies])
        for v in vv :
            tm = v[1]
    tm = tm if tm else '1520693568'
    return True if time.time() - int(tm) > TIME_EXPIRE_SEC else False
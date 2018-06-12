
from utils import *


def fill_courts(yeardir, cj):
    courts_file = yeardir + os.sep + "%s_%s.court" % tuple(cj.split("_"))
    ffs = os.listdir(yeardir + "/" + cj)

    f = open(courts_file)
    lines = f.read().strip().split('\n')
    f.close()

    for ff in ffs:
        info = read_info(yeardir + "/" + cj , int(ff))
        print(info['court_id'])
        for idx, line in enumerate(lines):
            info_here = line.split('\t')
            if int(info_here[0]) == info['court_id']:
                sys.stdout.write("save: " + str(info['court_id']) + "\n")
                break
        info_here[1] = str(info['finished_idx'])
        info_here[4] = '1'
        info_here[3] = "%.3f" % ((info['finished_idx'] if info['finished_idx'] > 0 else 0) / (float(info_here[2]) + 0.0000000001))
        lines[idx] = '\t'.join(info_here)

    f = open(courts_file, 'w')
    f.write('\n'.join(lines) + "\n")
    f.close()

if __name__ == '__main__':
    fill_courts(r'D:\itslaw_data\2015', '2_1')
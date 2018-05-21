# _*_ coding:utf-8 _*_
import sys
import json


v = sys.version_info[0]


CHILDREN = 'children'
caseType = 1
year = 2015
court = 3565
caseFile = "case%d_%d.txt"%(caseType, year)

max_court_id = 0

def visit(array, tabs):
    global max_court_id
    for obj in array:
        if CHILDREN in obj:
            court, where, rid = obj['id'].split('::')
            # print(tabs, court, rid , "=>")
            visit(obj[CHILDREN], tabs + "\t")
        else:
            court,where,cid = obj['id'].split('::')
            counts = obj['text'].split('(')[1].strip(')')
            # if cid == 'null':
            print(tabs, court, cid)
            try:
                ccid = int(cid)
                max_court_id = max_court_id if  ccid < max_court_id else ccid
            except Exception as e:
                print(court,cid,"<<<")




if __name__ == '__main__':
    if v == 3:
        f = open(caseFile, encoding='UTF-8')
        content = f.read()
        f.close()
        doc = json.loads(content)
        region_results = doc['data']['searchResult']['regionResults']
        visit(region_results, '')

print(max_court_id)

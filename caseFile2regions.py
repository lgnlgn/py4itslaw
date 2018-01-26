#coding=utf-8
import sys
import json
v = sys.version_info[0]

CHILDREN = 'children'

def visit(arrs = []):
    for obj in arrs:
        if obj.has_key(CHILDREN):
            visit(obj[CHILDREN])
        else:
            court,where,cid = obj['id'].split('::')
            counts = obj['text'].split('(')[1].strip(')')
            print court, cid, counts



if __name__ == '__main__':
    f = open('case.txt')
    content = f.read()
    f.close()
    if v == 2:
        content = content.decode('utf-8')
    doc = json.loads(content)
    region_results = doc['data']['searchResult']['regionResults']
    visit(region_results)



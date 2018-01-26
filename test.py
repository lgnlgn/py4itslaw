#coding=utf-8
from Request import ItslawRequester

caseType=1
year = 2015
court = 3565
caseFile = "case%d_%d.txt"%(caseType, year)
listFile = "list%d_%d_%d.txt"%(caseType, year, court)

aa = ItslawRequester(caseType, year)

result = aa.get_case()

#result = aa.get_list('3565')

#result = aa.get_detail('1','2623', "ce1a6981-8f75-4c6d-a42b-65331d3b2f6f", '7')
# print(result)

f = open(caseFile, 'w')
f.write(result)
f.close()
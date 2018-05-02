#coding=utf-8
from Request import ItslawRequester

caseType=2
judgeType=1
year = 2014
court = 2182
caseFile = "case%d_%d.txt"%(caseType, year)
listFile = "list%d_%d_%d.txt"%(caseType, year, court)

aa = ItslawRequester(year, caseType, judgeType, "http://180.110.249.210:8118")

#result = aa.get_case()

# result = aa.test_req('http://www.xicidaili.com')
#result = aa.get_list(court)
result = aa.get_detail('1','1907', court, 1,"18db9fcb-cab9-4ed7-a298-9db426ea21a5")
print(result)


#
# result = aa.test_req('http://ip.chinaz.com/getip.aspx')
# f = open(listFile, 'w')
# f.write(result)
# f.close()
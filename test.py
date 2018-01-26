#coding=utf-8
from Request import ItslawRequester

aa = ItslawRequester(2, 2014)

result = aa.get_case()

#result = aa.get_detail('1','2623', "ce1a6981-8f75-4c6d-a42b-65331d3b2f6f", '7')
# print(result)

f = open('case2.txt', 'w')
f.write(result)
f.close()
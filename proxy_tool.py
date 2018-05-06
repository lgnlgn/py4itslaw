from utils import *
import re
XICI_PAGES = 1;
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
xici_headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
           'Cache-Control': 'max-age=0',
           'Pragma': 'no-cache',
           'Host':'www.xicidaili.com'
           }

ip111_headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
           'Referer':'http://www.ip111.cn/',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
           'Cache-Control': 'max-age=0',
           'Host': '45.32.164.128',
           'Pragma': 'no-cache',
           }

chinaz_headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate, sdch',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Cache-Control': 'max-age=0',
           'Host': 'ip.chinaz.com',
           'Upgrade-Insecure-Requests': '1',
           }

def check_proxy_ok(protocal, host, port ):

    return_ip = request_with_proxy("http://ip.chinaz.com/getip.aspx", add_headers=chinaz_headers, proxy= {protocal: host + ":" + port})
    return return_ip.strip()


# resp = get_resp('http://www.xicidaili.com/nn/1', add_headers= headers)
# print(resp.info()['Set-Cookie'])
# headers['Cookie'] = resp.info()['Set-Cookie']
# headers['Host']= 'www.xicidaili.com'

    # resp = get_resp('http://www.xicidaili.com/nn/%d' % i, add_headers= headers)
    # print(decompress_response(resp))
proxy_pages = [request_with_proxy('http://www.xicidaili.com/nn/%d' % i, add_headers= xici_headers) for i in range(1, XICI_PAGES + 1)]
print('--')
print(check_proxy_ok('http', '183.20.9.60', '61234'))
# f = open('proxy_list.txt' , 'w')
# for html in proxy_pages:
#     print('---')
#     ips = re.findall(r'\<tr.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*?\<\/tr\>', html.replace('\n', ''))
#     for ip_str in ips:
#         attr = re.findall(r'\<td>(.*?)\<\/td\>', ip_str)
#         protocal, host,port  = attr[3].lower() , attr[0], attr[1]
#         check_proxy_ok(protocal, host, port)
# f.close()
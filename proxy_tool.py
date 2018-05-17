from utils import *
import re
import random

XICI_PAGES = 5;
PROXY_POOL_FILE = "proxy_availables.txt"
PROXY_ABANDON_FILE = "proxy_abandons.txt"

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


class ProxyPool(object):

    proxies = {}
    abandons = {}
    proxy_crawl_pages = XICI_PAGES;

    def __init__(self, proxy_crawl_pages = XICI_PAGES):
        if os.path.isfile(PROXY_POOL_FILE):
            self.__read_dict(self.proxies, PROXY_POOL_FILE)
        if os.path.isfile(PROXY_ABANDON_FILE):
            self.__read_dict(self.abandons, PROXY_ABANDON_FILE)
        self.proxy_crawl_pages = proxy_crawl_pages

    def get_random(self):
        ps = [x for x in self.proxies.items() if x not in self.abandons]
        d = random.randint(0, len(ps)-1)
        return ps[d]

    def confirm_success(self, p):
        self.abandons.pop(p)
        self.proxies[p] = 3

    def confirm_fail(self, p):
        self.proxies[p] -= 1
        if self.proxies[p] == 0:
            self.abandons[p] = time.time()
            self.__dump()

    def __dump_dict(self, proxy_dict, save_path):
        f = open(save_path, 'w')
        f.write('\n'.join(["%s\t%d" % c for c in proxy_dict.items()]))
        f.close()

    def __read_dict(self, proxy_dict, save_path):
        while True:
            try:
                f = open(save_path)
                content = f.read()
                proxy_dict = dict([x.split('\t') for x in content.strip().split('\n')])
                f.close()
            except :
                time.sleep(0.02)

    def crawl(self):
        proxy_pages = [request_with_proxy('http://www.xicidaili.com/nn/%d' % i, add_headers=xici_headers) for i in
                       range(1, self.proxy_crawl_pages + 1)]
        proxy_tmp = {}
        for html in proxy_pages:
            ips = re.findall(r'\<tr.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*?\<\/tr\>', html.replace('\n', ''))
            for ip_str in ips:
                attr = re.findall(r'\<td>(.*?)\<\/td\>', ip_str)
                protocal, host, port = attr[3].lower(), attr[0], attr[1]
                proxy_tmp[host + ":" + port] = 3
        proxy_tmp.update(self.proxies)
        self.proxies = proxy_tmp

        self.__dump_dict(self.proxies, PROXY_POOL_FILE)


    # resp = get_resp('http://www.xicidaili.com/nn/1', add_headers= headers)
# print(resp.info()['Set-Cookie'])
# headers['Cookie'] = resp.info()['Set-Cookie']
# headers['Host']= 'www.xicidaili.com'

    # resp = get_resp('http://www.xicidaili.com/nn/%d' % i, add_headers= headers)
    # print(decompress_response(resp))
print('--')

# f = open('proxy_list.txt' , 'w')
# for html in proxy_pages:
#     print('---')
#     ips = re.findall(r'\<tr.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*?\<\/tr\>', html.replace('\n', ''))
#     for ip_str in ips:
#         attr = re.findall(r'\<td>(.*?)\<\/td\>', ip_str)
#         protocal, host,port  = attr[3].lower() , attr[0], attr[1]
#         check_proxy_ok(protocal, host, port)
# f.close()

pp = ProxyPool(1)
pp.crawl()

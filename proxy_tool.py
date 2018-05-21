from utils import *
import re
import random
import requests

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
           'Host': 'www.ip111.cn',
           'Pragma': 'no-cache',
           }
#
chinaz_headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate, sdch',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Cache-Control': 'max-age=0',
           'Host': 'ip.chinaz.com',
           'Upgrade-Insecure-Requests': '1',
           }
#
def check_proxy_ok(*address):
    proxy = {"http": 'http:' + ":".join(address[1:])}
    print(proxy)
    resp = requests.get("http://ip.chinaz.com/getip.aspx", headers = chinaz_headers, proxies = proxy, timeout = 20)
    resp = requests.get("http://www.ip111.cn/", headers=ip111_headers,
                        proxies={address[0]: ":".join(address)}, timeout=20)

    # return_ip = request_with_proxy("http://ip.chinaz.com/getip.aspx", add_headers=chinaz_headers, proxy= {protocal: host + ":" + port})
    return str(resp.content, 'utf-8')[1436:1469]

def c_ip111():
    resp = requests.get("http://www.ip111.cn/", headers=ip111_headers, timeout=20)
    print(resp.headers)
    dd = str(resp.content, "utf-8")
    p = dd.index(u'国内网站')
    p2 = dd.index("</td>", p+6)
    print(p+19, p2)
    print(dd[1436:1469])

class ProxyPool(object):

    __RETRIES = 3
    proxies = {}
    abandons = {}
    proxy_crawl_pages = XICI_PAGES;

    def __init__(self, proxy_crawl_pages = XICI_PAGES):
        if os.path.isfile(PROXY_POOL_FILE)    and time.time() - os.path.getmtime(PROXY_POOL_FILE) < 7200:
            self.__read_dict(PROXY_POOL_FILE, self.proxies)
        if os.path.isfile(PROXY_ABANDON_FILE):
            self.__read_dict(PROXY_ABANDON_FILE, self.abandons)
        self.proxy_crawl_pages = proxy_crawl_pages

    def get_random(self):
        timec = time.time()
        abandons1 = len(self.abandons)
        self.abandons = dict([k for k in self.abandons.items() if timec - k[1] > 56400]) #refresh
        abandons2 = len(self.abandons)
        if abandons2 < abandons1:
            self.__dump_dict(self.abandons, PROXY_ABANDON_FILE)  #pop expired-fail proxy
        ps = [k for k,v in self.proxies.items() if k not in self.abandons]
        if len(ps) <= 0:
            return ''
        d = random.randint(0, len(ps)-1)
        return ps[d]

    def confirm_success(self, p):
        self.abandons.pop(p, 1)
        self.proxies[p] = self.__RETRIES

    def confirm_fail(self, p):
        self.proxies[p] -= 1
        if self.proxies[p] == 0:
            sys.stdout.write(p + " fail\n")
            sys.stdout.flush()
            self.abandons[p] = time.time()
            self.__dump_dict(self.abandons, PROXY_ABANDON_FILE)  #record fail proxy

    def __dump_dict(self, proxy_dict, save_path):
        f = open(save_path, 'w')
        f.write('\n'.join(["%s\t%d" % c for c in proxy_dict.items()]))
        f.close()

    def __read_dict(self, save_path, proxy_dict = {}):
        while True:
            try:
                f = open(save_path)
                content = f.read()
                proxy_strs = [x.split('\t') for x in content.strip().split('\n')]
                proxy_dict.update( dict([(x[0], int(x[1])) for x in proxy_strs if int(x[1]) > 0]) )
                f.close()
                return
            except IOError:
                time.sleep(0.02)
            except ValueError:
                break
            except IndexError:
                break

    def crawl(self):
        """invoke by daemon thread """
        proxy_pages = [request_with_proxy('http://www.xicidaili.com/nn/%d' % i, add_headers=xici_headers) for i in
                       range(1, self.proxy_crawl_pages + 1)]
        proxy_tmp = {}
        for html in proxy_pages:
            ips = re.findall(r'\<tr.*?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*?\<\/tr\>', html.replace('\n', ''))
            for ip_str in ips:
                attr = re.findall(r'\<td>(.*?)\<\/td\>', ip_str)
                protocal, host, port = attr[3].lower(), attr[0], attr[1]
                proxy_tmp[protocal + "://" + host + ":" + port] = self.__RETRIES
        sys.stdout.write("%d + %d = " %(len(self.proxies), len(proxy_tmp)))
        proxy_tmp.update(self.proxies)
        self.proxies = proxy_tmp
        sys.stdout.write("%d\n" % len(self.proxies))
        sys.stdout.flush()
        self.__dump_dict(self.proxies, PROXY_POOL_FILE)


if __name__ == '__main__':
    proxy_pool = ProxyPool()
    proxy_pool.crawl()
    import urllib

    for i in range(10):
        pro, host,port = proxy_pool.get_random().split(':')
        try:
            ip = check_proxy_ok(pro, host, port)
            print(ip, " back")
        except urllib.error.URLError as e:
            print(e)
        except Exception as e2:
            print(e2)
        time.sleep(4)

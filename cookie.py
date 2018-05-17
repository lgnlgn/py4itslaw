import http.cookiejar
import gzip
import urllib.request as ul

import requests

# 设置保存cookie的文件，同级目录下的cookie.txt
user_agent = r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4620.400 QQBrowser/9.7.13014.400'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
           'Cache-Control': 'no-cache',
           'Host': 'ip.chinaz.com',
           'Pragma': 'no-cache',
           }

chinaz_headers = {'User-Agent': user_agent,
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate, sdch',
           'Accept-Language': 'zh-CN,zh;q=0.8',
           'Cache-Control': 'max-age=0',
           'Host': 'ip.chinaz.com',
           'Upgrade-Insecure-Requests': '1',
           }

filename = 'cookie.txt'
# 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
cjar = http.cookiejar.CookieJar()
# 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
cookie_handler = ul.HTTPCookieProcessor(cjar)

proxy_handler = ul.ProxyHandler({"http":"http://60.177.231.0:18118"})

# 通过handler来构建opener
opener = ul.build_opener(cookie_handler, proxy_handler)
# 创建一个请求，原理同urllib2的urlopen

req = ul.Request("https://www.itslaw.com/api/v1/users/user/loginInfo", headers = {})
#req = ul.Request("http://ip.chinaz.com/getip.aspx", headers= headers)

ul.install_opener(opener)
resp = ul.urlopen(req, timeout=30)

#ss = requests.Session()
#resp = ss.get("http://ip.chinaz.com/getip.aspx",proxies = {"http":"http://49.79.192.21:61234"}  , timeout=30)
#resp = requests.get("http://ip.chinaz.com/getip.aspx", headers= chinaz_headers ,
#                   proxies = {"http":"49.79.192.21:61234"}, verify = True , timeout=30)



resphead = resp.info()
print(resphead)
data = resp.read()
# data = resp.content
print(data)
if 'gzip' in resphead['Content-Encoding']:
    data = gzip.decompress(data)

print(str(data, encoding='utf-8'))
print(cjar)



# py4itslaw
A simple python crawler for www.itslaw.com

```
目前在Python2.6 和Python3.5上经过测试可用；可能有一些没遇到的错误。 

在写爬虫期间，发现itslaw也有反扒机制，会直接封禁IP（猜测是抓了多久就封多久，抓1天封1天，又或者是抓多少条封多少秒），所以只做了单线程并且默认每个请求延迟1秒。

整个网站的文书按 年\裁判类型\文书类型 的组合切分出每次任务，欢迎大家一起使用，合力抓下全部文书。
```


### py4itslaw是什么?

一个抓取itslaw 法律文书的简单爬虫


### py4itslaw如何使用？

* 准备

使用浏览器打开https://www.itslaw.com; F12取出请求头按 headers.txt格式复制粘贴进去。

* 基本用法

 Usage: main.py [-y <year>][-t <caseType>][-j <judgeType>][-d [dir]][-s [courtStart]][-e [courtEnd]][-v]

* Options:
```
  -h, --help            show this help message and exit
  -d DIR, --dir=DIR     data directory for saving [default = .]；Error log will be stored here. 
  -v                    set it to print crawling detail
  -y YEAR, --year=YEAR  set year, e.g. 2015
  -t CASETYPE, --case=CASETYPE
                        set caseType, in [1,2,3,4], 民事、刑事、行政、执行
  -j JUDGETYPE, --judge=JUDGETYPE
                        set judgeType, in [1,2,3,4,5], 判决、裁定、通知、决定、调解
  -s COURT_START, --start=COURT_START
                        set court_id STARTS from max(COURT_START,
                        already_done), [default = 1]
  -e COURT_END, --end=COURT_END
                        set court_id ENDS from , [default = 3568]
  -i INTERVAL, --interval=INTERVAL
                        set crawling INTERVAL ms , [default = 1000]
```


* 参数解释

 年份`year`；案由类型`caseType`；文书类型`judgeType`；为**必填**参数。 爬虫脚本每次任务以此三参数为准
 
 爬虫启动之后会在`DIR`下创建 `YEAR/CASETYPE_JUDGETYPE` 目录
 
 之后为每个法院创建目录开始抓取，法院id由`COURT_START`，`COURT_END`设置，按法院id升序顺序抓取它的文书
 
 每抓取一篇文书会停留至多`INTERVAL`毫秒
 
### 改进的方向
1. 遍历法院id方式，目前采用法院id从1~3568方式抓取。而上很多年份（2010年前）、类型下的文书不足，统计后法院并无3500个。因此可以改成根据caseFile中的regionResult实际情况来抓取（起初设计也是这样，但后来发现很多法院缺少id, 需要补全所有法院的id）
2. 支持代理
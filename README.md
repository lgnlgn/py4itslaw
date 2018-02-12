# py4itslaw
a simple python crawler for www.itslaw.com

```
目前在Python2.6 和Python3.5上经过测试；已经可以用，但可能也会经常遇到错误而退出进程 

在写爬虫期间，发现itslaw也有反扒机制，有时候会直接封禁IP，所以只做了单线程并且默认每个请求延迟1秒。欢迎大家一起使用，共同抓取文书。
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
                        set caseType, in [1,2,3,4], 民事刑事行政执行
  -j JUDGETYPE, --judge=JUDGETYPE
                        set judgeType, in [1,2,3,4,5], 判决裁定通知决定调解
  -s COURT_START, --start=COURT_START
                        set court_id STARTS from max(COURT_START,
                        already_done), [default = 1]
  -e COURT_END, --end=COURT_END
                        set court_id ENDS from , [default = 3568]
  -i INTERVAL, --interval=INTERVAL
                        set crawling INTERVAL ms , [default = 1000]
```


* 参数解释

 年份`year`；案由类型`caseType`；文书类型`judgeType`；为**必填**参数。 爬虫每次任务以此三参数为准
 
 爬虫启动之后会在`DIR`下创建 `YEAR/CASETYPE_JUDGETYPE` 目录
 
 之后为每个法院创建目录开始抓取，法院id由`COURT_START`，`COURT_END`设置，按法院id升序顺序抓取它的文书
 
 每抓取一篇文书会停留至多`INTERVAL`毫秒
 
### 改进的方向
1. 遍历法院id方式，目前采用法院id从1~3568方式抓取。而上很多年份（2010年前）、类型下的文书不足，统计后法院并无3500个。因此可以改成根据caseFile中的regionResult实际情况来抓取（起初设计也是这样，但后来发现很多法院缺少id, 需要补全所有法院的id）

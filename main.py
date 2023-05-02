#import所有爬虫需要的库
import requests
from bs4 import BeautifulSoup
import re
import time
import random
import os
import sys
import json
import redis

#连接redis，127.0.0.1:6379
r = redis.StrictRedis(host='127.0.0.1', port=6379, db=0,decode_responses=True, charset='UTF-8', encoding='UTF-8')

#写入key
def write_key(key, value):
    r.set(key, value)
    print("写入成功")

#读取key
def read_key(key):
    value = r.get(key)
    print("读取成功")
    return value




#定义一个函数，用来获取网页的源代码
def get_html(url):
    try:
        #伪装成浏览器
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "ERROR"
 #定义一个函数，用post方法来获取网页的源代码，并且携带参数  

def get_html_post(url,data=None):
    try:
        #伪装成浏览器
        headers = {
            
                   'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
                   'Referer': 'http://guba.eastmoney.com/',
                   'Proxy-Connection': 'keep-alive',
                   'Origin': 'http://guba.eastmoney.com',
                   'Accept': '*/*',
                   'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
                   }
        r = requests.post(url,data=data, headers=headers, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "ERROR"
    

#入口，用于获取需要爬的子网页，把古巴的首页的第一页拿到
#TODO 不仅拿到首页，还要触发加载更多，获取更多的首页信息
def main():
    #定义一个变量，用来存放网页的url
    url = "http://guba.eastmoney.com/api/dynamicInfo"
    #调用get_html()函数，获取网页的源代码
    page=1
    html = get_html_post(url,data={'prama':'uid=&keychainId=&condition=null&isReload=true&fundLogin=false&hffCloseTime=0&deviceId=guba_home&fundIds=&fundId=&hkFundLogin=&hkFundId=&mbid=&line=10&pageSize=100'})
    #判断网页是否获取成功
    if html == "ERROR":
        print("网页获取失败")
        sys.exit()
    #解析网页源代码
    soup = BeautifulSoup(html, "html.parser")
    html_dict=json.loads(html)
    print(html_dict)
    
    #获取当前时间，用 年-月-日-小时-分钟的格式
    now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
    main_page_key='mainPage_'+url+'.'+str(now_time)+'.'+str(page)
    write_key(main_page_key,json.dumps(html))
    return main_page_key


#根据首页信息，去获取每一个文章的url，然后拿到文章中的评论
def get_article(main_page_key):
    main_page=json.loads(json.loads(read_key(main_page_key)))
    #获取main_page中的每一个文章的url
    return main_page['data']


#html_dict=read_key('mainPage_http://guba.eastmoney.com/api/dynamicInfo.2023-04-21-00-43.1')
#time.sleep(10)

#将redis中读取的二进制中文转化成中文
res=get_article("mainPage_http://guba.eastmoney.com/api/dynamicInfo.2023-05-02-23-40.1")
#for key in res:
    #print(key)
    #print(res[key])
realTimeFixedItems=res["realTimeFixedItems"][0]
print(realTimeFixedItems)
print("==========")
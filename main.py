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
from selenium import webdriver
#import driver中的By
from selenium.webdriver.common.by import By

class Driver(object):

    #记录第一个被创建对象的引用
    instance = None

    def __new__(cls, *args, **kwargs):

        #1.判断类属性是否为空对象，若为空说明第一个对象还没被创建
        if cls.instance is None:
        #2.对第一个对象没有被创建，我们应该调用父类的方法，为第一个对象分配空间
            cls.instance = super().__new__(cls)
        #3.把类属性中保存的对象引用返回给python的解释器
        return cls.instance

    def __init__(self):
        driver=webdriver.Chrome()

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
        #发起request时跟踪跳转页面
        r = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
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
def get_main_page_write_to_redis():
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
def get_article_list_write_to_redis(main_page_key):
    main_page=json.loads(json.loads(read_key(main_page_key)))["data"]
    items=main_page["items"]
    item_data=[]
    for item in items:
        if(item["infoType"]==2201):
            url_start_with="https://finance.eastmoney.com/a/"
        else:
            url_start_with="https://caifuhao.eastmoney.com/news/"
        item_data.append({"infocode":item["itemData"]["code"],"title":item["itemData"]["title"],"url_start_with":url_start_with})
    #获取main_page中的每一个文章的url
    item_key=main_page_key+".items"
    write_key(item_key,json.dumps(item_data))
    return item_key


#使用selenium获取redis中item的信息,并访问文章，同时写入到redis
def read_redis_article_list_get_url_write_to_redis(item_key):
    item_list=json.loads(read_key(item_key))
    driver=webdriver.Chrome()
    for item in item_list:
        if(item["url_start_with"]=="https://finance.eastmoney.com/a/"):
            url=item["url_start_with"]+"{}.html#gubaComment".format(item["infocode"])
        else:
            url=item["url_start_with"]+"{}".format(item["infocode"])
        print(url)
        driver.get(url)
        time.sleep(5)
        try:
        #检查页面上是否有加载更多的按钮，如果有就点击
            if(driver.find_elements(By.CSS_SELECTOR, "a[class='view_morebtn bottombtn fl']")):
                driver.find_element(By.CSS_SELECTOR, "a[class='view_morebtn bottombtn fl']").click()
                time.sleep(5)
                windows = driver.window_handles   # 获取当前页句柄
                driver.switch_to.window(windows[-1])
        except Exception as e:
            print(e)
        #获取跳转后页面上的全部评论，如果有下一页按钮就点击
        page=1
        while(page==1 or driver.find_elements(By.CSS_SELECTOR, "a[class='nextp']")):
            #点击下一页
            if(page!=1):
                driver.find_element(By.CSS_SELECTOR, "a[class='nextp']").click()
                time.sleep(0.5)
            #解析网页源代码
            html=driver.page_source
            if html == "ERROR":
                print("网页获取失败")
                sys.exit()
            #解析网页源代码
            soup = BeautifulSoup(html, "html.parser")
            #获取当前时间，用 年-月-日-小时-分钟的格式
            now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
            article_key='article_'+url+'.'+str(now_time)+'.page_'+str(page)
            write_key(article_key,json.dumps(html))
            page+=1
    return article_key

@DeprecationWarning
def read_redis_article_list_get_url_write_to_redis_depricated(item_key):
    item_list=json.loads(read_key(item_key))
    for item in item_list:
        if(item["url_start_with"]=="https://finance.eastmoney.com/a/"):
            url=item["url_start_with"]+"{}.html".format(item["infocode"])
        else:
            url=item["url_start_with"]+"{}".format(item["infocode"])
        print(url)
        html=get_html(url)
        if html == "ERROR":
            print("网页获取失败")
            sys.exit()
        #解析网页源代码
        soup = BeautifulSoup(html, "html.parser")
        #获取当前时间，用 年-月-日-小时-分钟的格式
        now_time = time.strftime("%Y-%m-%d-%H-%M", time.localtime())
        article_key='article_'+url+'.'+str(now_time)
        write_key(article_key,json.dumps(html))
        time.sleep(5)
    return article_key













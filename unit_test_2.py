from main import *

#article_key="article_https://caifuhao.eastmoney.com/news/20230502194711347679840.2023-05-03-02-59"
#article=read_key(article_key)
#html=article
#soup = BeautifulSoup(html, "html.parser")
#html_dict=json.loads(html)

#print(html_dict)

import  requests_html
from selenium import webdriver

driver=webdriver.Chrome()
driver.get("https://caifuhao.eastmoney.com/news/20230502200546479423010")


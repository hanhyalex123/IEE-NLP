from main import *

article_key="article_https://finance.eastmoney.com/a/202305032710822132.html.2023-05-03-17-24.page_1"
article=read_key(article_key)
html=json.loads(article)
soup = BeautifulSoup(html, "html.parser")


#正则匹配所有包含full_text的内容
import re


full_reply_class_list=re.findall(r'class="reply_title"',html)
#list内容去除重复
full_reply_class_list=list(set(full_reply_class_list))
full_reply_list=[]
for i in full_reply_class_list:
    i=i.split('"')[1]
    print(i)
    for item in soup.find_all("div",class_=i):
        full_reply_list.append(item.span.text)
print(full_reply_list)
print(html)

#import  requests_html

#driver.get("https://caifuhao.eastmoney.com/news/20230502200546479423010")


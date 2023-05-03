from main import *

article_key="article_https://finance.eastmoney.com/a/202305022710771344.html.2023-05-03-04-09"
article=read_key(article_key)
html=article
soup = BeautifulSoup(html, "html.parser")
html_dict=json.loads(html)
print(html_dict)

#import  requests_html

#driver.get("https://caifuhao.eastmoney.com/news/20230502200546479423010")


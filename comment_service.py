from main import *
import re

#获取redis中所有article开头的key
def get_all_article_keys():
    keys=r.keys()
    article_keys=[]
    for key in keys:
        if key.startswith("article"):
            article_keys.append(key)
    return article_keys

#遍历所有article开头的key，获取内容
def get_all_article():
    article_keys=get_all_article_keys()
    article_list=[]
    for article_key in article_keys:
        article=read_key(article_key)
        article_list.append({"article_key": article_key,"article":json.loads(article)})
    return article_list

def get_all_comments():
    article_list=get_all_article()
    comments=[]
    for article_dict in article_list:  
        if("finance" in article_dict["article_key"]):
            article_key=article_dict["article_key"]
            html=article_dict["article"]
            soup = BeautifulSoup(html, "html.parser")
            full_reply_class_list=re.findall(r'class="reply_title"',html)
            #list内容去除重复
            full_reply_class_list=list(set(full_reply_class_list))
            full_reply_list=[]
            for i in full_reply_class_list:
                i=i.split('"')[1]
                for item in soup.find_all("div",class_=i):
                    full_reply_list.append(item.span.text)
            comments.append({"article_key": article_key,"comments":full_reply_list})
    return comments
def write_comments_to_txt(comments):
    with open("comments.txt","w",encoding="utf-8") as f:
        for comment in comments:
            f.write(comment["article_key"]+"\n")
            for item in comment["comments"]:
                f.write(item+"\n")
            f.write("\n")

main_page_key=get_main_page_write_to_redis()
item_key=get_article_list_write_to_redis(main_page_key)
article_key=read_redis_article_list_get_url_write_to_redis(item_key)

comments=get_all_comments()
write_comments_to_txt(comments)
#将comments写成txt保存






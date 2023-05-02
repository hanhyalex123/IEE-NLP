from main import *

main_page_key=get_main_page_write_to_redis()
item_key=get_article_list_write_to_redis(main_page_key)
article_key=read_redis_article_list_get_url_write_to_redis(item_key)


#将redis中读取的二进制中文转化成中文
article=json.loads(read_key(article_key))
print(article)





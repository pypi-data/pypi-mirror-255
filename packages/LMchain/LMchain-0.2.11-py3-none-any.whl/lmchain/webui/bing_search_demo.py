import re,urllib.parse,urllib.request,urllib.error
from bs4 import BeautifulSoup as BS
# 搜索框中的搜索内容
word = '偷心的歌词是什么'

# 获取bing搜索的结果
def get_bing_results(word):
    baseUrl = 'http://cn.bing.com/search?'
    word = word.encode(encoding='utf-8', errors='strict')

    data = {'q':word}
    data = urllib.parse.urlencode(data)
    url = baseUrl+data
    print(url)

    try:
        html = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print(e.code)
    except urllib.error.URLError as e:
        print(e.reason)

    # 解析html
    soup = BS(html,"html.parser")
    context = soup.findAll(class_="b_lineclamp4 b_algoSlug")
    # print(context)
    results = ""
    for i in range(len(context)):
        if '\u2002·\u2002' not in str(context[i]): continue
        results += (str(i)+'）')
        results += (str(context[i]).split('\u2002·\u2002')[1].replace('</p>',''))

    # 返回soup, context用于debug，有时候results是空的，这是因为搜索失败导致的
    return results, soup, context

results, soup, context = get_bing_results(word)
# print(soup)
print(results)
print(soup)
print(context)
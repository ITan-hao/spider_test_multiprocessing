from multiprocessing.dummy import Pool
import requests
from lxml import etree
import re
import bs4

# 需求爬取梨视频的视频数据
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
}
# 原则：线程池处理的是阻塞且较为耗时的操作
# 对下述url发起请求解析出视频详情页的url和视频的名称

url = 'https://www.pearvideo.com/category_2'

page_text = requests.get(url=url, headers=headers).text
tree = etree.HTML(page_text)#使用BeautifulSoup的HTML方法解析文本内容

li_list = tree.xpath('//ul[@id="listvideoListUl"]/li') #使用XPath表达式获取视频列表
# 储存所有视频的链接
urls = []
for li in li_list:
    detail_url = 'http://www.pearvideo.com/' + li.xpath('./div/a/@href')[0]
    title = li.xpath('./div/a/div[2]/text()')[0] + '.mp4'
    print(detail_url,title)
    # 请求详情页面 获取下载链接
    contId = detail_url.split("_")[1]
    video_url =f"https://www.pearvideo.com/video_{contId}"
    #https: // video.pearvideo.com / mp4 / short / 20240823 / cont - 1795972 - 16035507 - hd.mp4

    #detail_text = requests.get(url=detail_url, headers=headers).text
    # 解析视频地址url  是js加载来的，不在本页面.(bs4和xpath只能解析标签)
    #print(detail_text)

    #video_url = re.findall('srcUrl="(.*?)",vdoUrl', detail_text)[0]

    dic = {
        'title': title,
        'url': video_url,
    }
    urls.append(dic)


def get_video_data(dic):
    url = dic['url']
    title = dic['title']
    print(title, 'download -ing...')
    data = requests.get(url=url, headers=headers).content

    # 持久化存储
    with open(title, 'wb') as f:
        f.write(data)
        print(title, 'download -success!!')


# 使用线程池进行视频数据的请求
pool = Pool(4)
pool.map(get_video_data, urls)  # func,可迭代对象
pool.close()
pool.join()

'''asyncio.ensure_future() 和 get_event_loop().run_until_complete() 是异步I/O编程中用于启动异步任务的关键功能。

asyncio.ensure_future(coroutine, loop=None)1:
这个函数用于将给定的协程（coroutine）包装成一个Future对象，并将其添加到事件循环的任务队列中。
它允许你在不创建新线程的情况下异步执行任务。你可以通过传递当前事件循环来指定特定的循环，如果不指定，则默认使用当前活动的事件循环。

loop.run_until_complete(task_or_future)2:
这个方法是通过Event Loop调用来运行一个Task或Future直到其完成。它阻塞当前线程直到所给任务完成，适合用于同步控制异步操作的结果。
这个方法通常配合await关键字一起使用，因为它会等待task_or_future的结果返回。

简而言之，asyncio.ensure_future() 是异步启动任务，而loop.run_until_complete() 是同步地等待并处理任务的结果。前者适用于分散任务的启动，后者则用于执行和跟踪整个任务流程。
如果你有一个完整的异步操作，可能会先使用ensure_future开始它，然后再在其上使用run_until_complete来获取结果。'''
#coding=utf-8
import json
import queue
import random
import re
import time
import traceback
import urllib
import urllib.request
import uuid

import requests
import wipe_off_html_tag
from bs4 import BeautifulSoup

import data_storager


class ParentChild(object):
    def __init__(self):
        self._parent_id = None
        self._parent_title = None
        self._parent_url = None
        self._parent_layer = None
        self._child_id = None
        self._child_title = None
        self._child_url = None
        self._child_layer = None


class Spider(object):
    """
    layer：第一层，首页， 科学百科
           第二层，航空航天
           第三层，3·8马来西亚航班失踪事件
           第四层，马来西亚航空公司
           第h层
    """
    def __init__(self):
        self._post_lemmas_url = 'https://baike.baidu.com/wikitag/api/getlemmas'
        self._get_zhixin_url = 'https://baike.baidu.com/wikiui/api/zhixinmap?lemmaId='
        self._get_guess_like_url = 'https://baike.baidu.com/api/wikiui/guesslike?url='
        self._parent_childs = queue.Queue()  # relationship队列
        self._crawl_layers = 4-1  # 需要爬取的最后一层的上一层

    def execute(self):
        # 录入首页，科学百科
        root_url = 'https://baike.baidu.com/science'
        root_title = r'科学百科'
        root_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(root_url)))
        # data_storager.insert_webpage(root_id, root_title, root_url, None)
        # print("wxm entity:", root_title, root_url)

        # 录入首页下二级页面
        first_page_html = self.get_firstpage_content("https://baike.baidu.com/science")
        first_page_urls = self.get_firstpage_url(first_page_html)  # 10条二级页面信息
        tag_ids = self.get_firstpage_tagid(first_page_urls)  # 9条二级页面信息
        first_page_urls_slice = first_page_urls[1:2]  # 获取前半部分URL
        tag_ids_slice = tag_ids[1:2]  # 获取前半部分Tag

        for page_id in range(0, 61):
            try:
                for i in range(0, len(tag_ids_slice)):
                    # 处理每一个二级页面，如航空航天，天文学，环境生态
                    print("page_id:" + str(page_id) + ", tagids：" + str(tag_ids_slice[i]))
                    time.sleep(random.choice(range(1, 3)))
                    title = first_page_urls_slice[i].get_text()
                    url = first_page_urls_slice[i].get('href')
                    id = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(url)))  # 为当前网页生成UUID
                    data_storager.insert_relationship(root_id, root_title, id, title)  # 插入首页与二级页面的relationship，如<科学百科_id, 航空航天_id>
                    data_storager.insert_webpage(id, title, url, None)  # 插入二级页面webpage信息,页面内容为空，如航空航天
                    print("wxm entity:",title, url)
                    # 录入所有的<二级页面，三级页面>配对信息到缓存中,如航空航天下面的当前page_id下的所有条目,如马航,911事件
                    self.get_second_page_url(id, title, url, tag_ids_slice[i], page_id)
                while (self._parent_childs):  # 从第三层（马航,911事件，位于缓存对象的child_xx中）开始，处理队列每一个页面
                    pc = self._parent_childs.get(0)
                    self.deal_with_child_webpage(pc)  # 用layer控制爬虫爬取深度，调用deal_with_child_webpage方法即插入数据库
            except:
                print(traceback.format_exc())
                print("wxmException，page_id：" + str(page_id))
            print("wxmmmmmmmmmmmmmm， tag_ids_slice:" + str(tag_ids_slice[i]))
        print("wxmmmmmmmmmmmmmm， page_id：" + str(page_id))

    def deal_with_child_webpage(self, pc):
        """ 处理当前缓存队列中的对象中的child对象，该方法始终以child为中心处理，parent在前面处理了；从第三层开始的 """
        try:
            htmL_content = self.get_sub_page_content(pc._child_url)  # 获取当前孩子页面的html内容
            if htmL_content == None:
                return
            real_content = self.get_web_real_content(htmL_content) # 获取网页的真正需要入库的content
            if len(real_content)>100 and real_content!=None:
                real_content=real_content[:100]
            data_storager.insert_relationship(pc._parent_id, pc._parent_title, pc._child_id, pc._child_title)  # 插入二级页面与三级页面的relationship，如<航空航天_id, 马航_id>
            data_storager.insert_webpage(pc._child_id, pc._child_title, pc._child_url, real_content)  # 插入当前孩子页面信息，如马航 todo, 解析出htmlcontent中汉字
            print("wxm entity:",pc._child_title, pc._child_url)
            self.batch_insert_webpage_attributes(pc._child_id, pc._child_title, htmL_content)  # 插入当前页面的所有属性信息，如马航下的中文名 3·8马来西亚航班失踪事件
            self._crawl_layers = random.choice(range(3, 7))
            if pc._child_layer <= self._crawl_layers:  # 3<=4,仅从第三层爬到第四层
                self.get_sub_urls(pc._child_id, pc._child_title, pc._child_url, pc._child_layer, htmL_content)  # 获取当前网页下所有连接，传入第三层的id，title，url，获取第四层信息，加入到缓存队列中
        except:
            print(traceback.format_exc())
            print("wxmException, ", pc._child_id, pc._child_title, pc._child_url)

    def batch_insert_webpage_attributes(self, id, title, htmL_content):
        soup_findattribute = BeautifulSoup(htmL_content, 'html.parser')
        data_findattribute = soup_findattribute.find_all('div', {'class': 'basic-info cmn-clearfix'})
        for attributes in data_findattribute:
            attribute_names = attributes.find_all('dt', {'class': 'basicInfo-item name'})
            names_list = []
            for a in attribute_names:
                attribute_name = a.get_text()
                names_list.append(attribute_name)
            attribute_values = attributes.find_all('dd', {'class': 'basicInfo-item value'})
            values_list = []
            for b in attribute_values:
                attributes_value = b.get_text()
                values_list.append(attributes_value)
            nvs = zip(names_list, values_list)
            nvDict = dict((str(names_list), str(values_list)) for names_list, values_list in nvs)
            for names_lists, values_lists in nvDict.items():
                names_lists_insert = names_lists
                value_lists_insert = values_lists.strip("\n")
                data_storager.insert_attributes(id, title, names_lists_insert, value_lists_insert)

    def get_web_real_content(self, htmL_content):
        soup = BeautifulSoup(htmL_content, 'html.parser')
        main_content = soup.find('div', {'class': 'main-content'})
        return wipe_off_html_tag.filter_tags(str(main_content)).strip(r'收藏\n查看我的收藏\n').\
            strip(r'有用+1\n已投票\n').strip(r'编辑\n锁定\n').strip(r'审核\n。')

    def get_sub_urls(self, id, title, url, layer, content):
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.body  # 获取body部分

        # 爬取para中连接词条
        try:
            link_list1 = {}
            link_body1 = body.find_all('div', {'class': 'para', 'label-module': "para"})
            for link_body in link_body1:
                result_list = link_body.find_all('a', {'target': '_blank'})
                if result_list:
                    for link in result_list:
                        fourth_page_url_postfix = link.get('href')
                        pattern = re.compile(r'/pic')
                        match = pattern.match(fourth_page_url_postfix)
                        if not match:
                            sub_title = link.get_text()
                            sub_url = "http://baike.baidu.com" + fourth_page_url_postfix
                            link_list1[sub_title] = sub_url
        except:
            print(traceback.format_exc())
            print("wxmException, 爬取para中连接词条 todo print 出错更详细信息:" + id + ", " + title + ", " + url)

        # 爬取相关信息词条
        try:
            link_list2 = {}
            link_body2 = body.find('div', {'class': 'zhixin-box'})
            newlemmaid = link_body2['data-newlemmaid']
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'
            }
            data = {"lemmaId": newlemmaid}
            request_url = self._get_zhixin_url + str(newlemmaid)
            content = requests.get(request_url, params=data, headers=headers).content
            response = content.decode('unicode-escape').replace("\/", "/")
            js = json.loads(response)
            for i in range(len(js)):
                title_urls = js[i]['data']
                for j in range(len(title_urls)):
                    sub_title = js[i]['data'][j]['title']
                    sub_url = js[i]['data'][j]['url']
                    link_list2[sub_title] = sub_url
        except:
            print(traceback.format_exc())
            print("wxmException, 爬取相关信息词条 todo print 出错更详细信息:" + id + ", " + title + ", " + url)

        # 爬取猜你喜欢词条
        try:
            link_list3 = {}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'
            }
            data = {
                "url": sub_url,
                "lemmaTitle": sub_title,
                "eid": 202
            }
            request_url = self._get_guess_like_url + str(sub_url) + "&lemmaTitle=" + sub_title + "&eid=202"
            content = requests.get(request_url, params=data, headers=headers).content
            try:
                jso1 = json.loads(content)
                ad_place_data = jso1["ad_place_list"][0]["ad_place_data"]
                ad_place_data2 = ad_place_data.replace("\/", "/")
                jso2 = json.loads(ad_place_data2)
                ads = jso2["ads"]
                for ad in ads:
                    sub_title = ad['title']
                    sub_url = ad['url']
                    link_list3[sub_title] = sub_url
            except:
                print(traceback.format_exc())
                print("wxmException, 爬取猜你喜欢词条 json 解析失败")
        except:
            print(traceback.format_exc())
            print("wxmException, 爬取猜你喜欢词条 todo print 出错更详细信息:" + id + ", " + title + ", " + url)
        try:
            dictMerged2 = {}
            dictMerged1 = dict(link_list1, **link_list2)
            dictMerged2 = dict(dictMerged1, **link_list3)
        except:
            print(traceback.format_exc())
            print("wxmException, 合并dict失败")

        for sub_title, sub_url in dictMerged2.items():
            pc = ParentChild()
            pc._parent_id = id
            pc._parent_title = title
            pc._parent_url = url
            pc._parent_layer = layer
            child_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(sub_url)))  # 为当前孩子页面生成UUID
            pc._child_id = child_id
            pc._child_title = sub_title
            pc._child_url = sub_url
            pc._child_layer = pc._parent_layer + 1
            self._parent_childs.put(pc)

    def get_sub_page_content(self, url3, data=None):
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
        }
        timeout = 180
        try:
            result2 = requests.get(url3, headers=header, timeout=timeout)
            result2.encoding = 'utf-8'
            return result2.text
        except urllib.request.HTTPError as e:
            print(traceback.format_exc())
            print('wxmException,  1:', e.code)
        except urllib.request.URLError as e:
            print(traceback.format_exc())
            print('wxmException,  2:', e.reason)
        except:
            print(traceback.format_exc())
            print('wxmException,  0')
        return None

    def get_second_page_url(self, id, title, url, tagId, page):
        """
            父亲id是传入的，孩子id是生成的
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'
        }
        data = {
            "limit": "24",
            "timeout": 3000,
            "filterTags": [],
            "tagId": tagId,
            "fromLemma": False,
            "contentLength": 40,
            "page": page
        }
        try:
            content = requests.post(self._post_lemmas_url, data=data, headers=headers).content
            response = content.decode('unicode-escape').replace("\/", "/")
            js = json.loads(response)
            for i in range(len(js['lemmaList'])):
                sub_title = (js['lemmaList'][i]['lemmaTitle'])
                sub_url = (js['lemmaList'][i]['lemmaUrl'])
                pc = ParentChild()
                pc._parent_id = id
                pc._parent_title = title
                pc._parent_url = url
                pc._parent_layer = 2
                child_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, str(sub_url)))  # 为当前孩子页面生成UUID
                pc._child_id = child_id
                pc._child_title = sub_title
                pc._child_url = sub_url
                pc._child_layer = 3
                self._parent_childs.put(pc)
        except:
            print(traceback.format_exc())
            print("wxmException, ", id, title, url, tagId, page)  # todo 描述

    def get_firstpage_content(self, url, data=None):
        header = {
            'Accept': 'text/css,*/*;q=0.1',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.143 Safari/537.36'
        }
        timeout = random.choice(range(80, 180))
        while True:
            try:
                rep = requests.get(url, headers=header, timeout=timeout)
                rep.encoding = 'utf-8'
                req = urllib.request.Request(url, data, header)
                response = urllib.request.urlopen(req, timeout=timeout)
                response.close()
                break
            except urllib.request.HTTPError as e:
                print(traceback.format_exc())
                print('wxmException,  1:', e)
                time.sleep(random.choice(range(1,3)))
            except urllib.request.URLError as e:
                print(traceback.format_exc())
                print('wxmException,  2:', e)
                time.sleep(random.choice(range(1,3)))
            except:
                print(traceback.format_exc())
                print('wxmException 0')
        return rep.text

    def get_firstpage_url(self, html):
        bs = BeautifulSoup(html, "html.parser")
        body = bs.body  # 获取body部分
        data = body.find_all('div', {'class': 'category-info'})  # 找到id为7d的div
        urls_list = []
        for a in data:
            ul = a.find('h5')
            url = ul.find('a')
            urls_list.append(url)
        return urls_list

    def get_firstpage_tagid(self, first_page_urls):
        links_list = []
        for i in first_page_urls:
            links = i.get('href')
            links_list.append(links)
        tagid_list = []
        for b in links_list:
            tagid = b[46:51]
            tagid_list.append(tagid)
        # 这里可以del 多个first_page_urls，将其分成多部分，供两台机器一起跑
        # 可以用切片，将tagid_list选择出对应的部分来
        del first_page_urls[0]
        del tagid_list[0]
        return tagid_list  # 检测出返回值最好跟你要输出的内容保持一直，出错率比较低

if __name__ == '__main__':
    spider = Spider()
    spider.execute()
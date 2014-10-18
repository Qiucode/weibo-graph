# -*- coding: utf-8 -*-
import re
import binascii
import random

import scrapy
import rsa
from scrapy.http import Request, FormRequest
from bs4 import BeautifulSoup

from weibo.items import UserItem


class UserSpider(scrapy.Spider):
    name = "user"
    allowed_domains = ["weibo.com", "weibo.cn", "sina.com.cn", "127.0.0.1"]

    username = 'cct439@163.com'
    password = 'cct437'
    wbclient = 'ssologin.js(v1.4.18)'
    crawl_domain = 'http://weibo.cn'

    def start_requests(self):
        """
        get the pubkey, servertime, nonce and rsakv from prelogin address
        """
        preloginurl = 'http://3g.sina.com.cn/prog/wapsite/sso/login.php?' \
                      'ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&' \
                      'backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='
        yield Request(url=preloginurl, method='get',
                      headers={'User-Agent': 'Mozilla/5.0 (Windows;U;Windows'
                                             ' NT 5.1;zh-CN;rv:1.9.2.9)Gecko'
                                             '/20100824 Firefox/3.6.9',
                               'Referer': ''},
                      callback=self.post_message)

    def post_message(self, response):
        """
        log in
        """
        rand = response.selector.xpath(u"//form/@action").extract()[0]
        passwd = response.selector.xpath(u"//input[@type='password']/@name").extract()[0]
        vk = response.selector.xpath(u"//input[@name='vk']/@value").extract()[0]
        data = {'mobile': self.username,
                passwd: self.password,
                'remember': 'on',
                'backURL': 'http://weibo.cn/',
                'backTitle': '新浪微博',
                'vk': vk,
                'submit': '登录',
                'encoding': 'utf-8'}

        loginurl = 'http://3g.sina.com.cn/prog/wapsite/sso/' + rand
        yield FormRequest(url=loginurl, formdata=data, callback=self.parse)

    def parse(self, response):
        """
        now we start to crawl users and their relationships
        """
        # gen seed

        uid = random.choice(['1663317954', '5061214872', '1638988052'])
        u = UserItem()
        u['uid'] = uid
        profile_url = '/'.join((self.crawl_domain, u['uid'], 'profile'))
        yield Request(url=profile_url,
                      method='get',
                      callback=self.parse_profile,
                      meta={'u': u})

    def parse_profile(self, response):
        u = response.meta['u']
        soup = BeautifulSoup(response.body)
        u['n_follow'] = re.search(r'\w+', soup.find(href=re.compile(r'/follow')).text).group(0)
        u['n_fans'] = re.search(r'\w+', soup.find(href=re.compile(r'/fans')).text).group(0)
        u['n_weibo'] = re.search(r'\w+', soup.find(class_='tc').text).group(0)

        info = '/'.join((self.crawl_domain, u['uid'], 'info'))
        yield Request(url=info,
                      method='get',
                      callback=self.parse_info,
                      meta={'u': u})


    def parse_info(self, response):
        u = response.meta['u']
        soup = BeautifulSoup(response.body)
        is_match_img = re.search(r'src="(.+)"', str(soup.find(alt=u'头像')))
        if is_match_img:
            u['profile_img'] = is_match_img.group(1)
        uname = soup.find(text=re.compile(u'昵称'))
        u['uname'] = uname[3:] if uname else None
        sex = soup.find(text=re.compile(u'性别'))
        u['sex'] = sex[3:] if sex else None
        address = soup.find(text=re.compile(u'地区'))
        u['address'] = address[3:].split(' ') if address else None
        emotion_status = soup.find(text=re.compile(u'感情状况'))
        u['emotion_status'] = emotion_status[5:] if emotion_status else None
        desc = soup.find(text=re.compile(u'简介'))
        u['desc'] = desc[3:] if desc else None
        verified_info = soup.find(text=re.compile(u'认证'))
        u['desc'] = desc[3:] if desc else None

        work_info = soup.find(text=u'工作经历')
        u['work_info'] = work_info.next.text if work_info else None
        edu_info = soup.find(text=u'学习经历')
        u['edu_info'] = edu_info.next.text if edu_info else None
        url_name = soup.find(text=u'其他信息')
        u['url_name'] = re.search(r'http://weibo.com/(\w+)', url_name.next.text).group(1) \
            if url_name else None

        u['fans'] = []
        u['followers'] = []
        # find tags
        tag_page = re.search(r'"(/account/privacy/tags/.+?)"', response.body).group(1)
        if (tag_page):
            tag_url = "http://weibo.cn" + tag_page
            yield Request(url=tag_url, callback=self.parse_tags, meta={'u': u})
        else:
            fans = '/'.join((self.crawl_domain, u['uid'], 'fans'))
            yield Request(url=fans, callback=self.parse_fans, meta={'u': u})

            # yield Request(url=)

    def parse_tags(self, response):
        u = response.meta['u']
        soup = BeautifulSoup(response.body)
        tags = []
        for t in soup.findAll(href=re.compile(r".*/search/\?keyword=.+&stag=1")):
            tags.append(t.text)
        u['tags'] = tags
        fans_url = '/'.join((self.crawl_domain, u['uid'], 'fans?page=1'))
        yield Request(url=fans_url, callback=self.parse_fans, meta={'u': u})

    def parse_fans(self, response):
        u = response.meta['u']
        fans_base_url = '/'.join((self.crawl_domain, u['uid'], 'fans?page='))
        reg = re.compile(r'href="http://weibo.cn/attention/add\?uid=([0-9]*)&')
        page_fans = set(reg.findall(response.body))
        u['fans'].extend(page_fans)

        page_info = re.search(ur'([0-9]{1,2})/([0-9]{1,2})页', response.body.decode('utf8'))
        cur_page, total_page = page_info.groups()
        if int(cur_page) <= int(total_page):
            yield Request(url=fans_base_url + str(int(cur_page) + 1),
                          callback=self.parse_fans,
                          meta={'u': u})
        else:
            # go on~~~ process followers
            follow_url = '/'.join((self.crawl_domain, u['uid'], 'follow?page=1'))
            yield Request(url=follow_url,
                          callback=self.parse_followers,
                          meta={'u': u})


    def parse_followers(self, response):
        u = response.meta['u']
        follow_base_url = '/'.join((self.crawl_domain, u['uid'], 'follow?page='))
        reg = re.compile(r'href="http://weibo.cn/attention/add\?uid=([0-9]*)&')
        page_followers = set(reg.findall(response.body))
        u['followers'].extend(page_followers)
        page_info = re.search(ur'([0-9]{1,2})/([0-9]{1,2})页', response.body.decode('utf8'))
        cur_page, total_page = page_info.groups()
        if int(cur_page) <= int(total_page):
            yield Request(url=follow_base_url + str(int(cur_page) + 1),
                          callback=self.parse_followers,
                          meta={'u': u})
        else:
            # finished parsing a uid
            # return UserItem
            yield u
            yield Request(url="http://weibo.cn",
                          callback=self.parse)


    @staticmethod
    def encrypt_passwd(passwd, pubkey, servertime, nonce):
        key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(passwd)
        passwd = rsa.encrypt(message.encode('utf-8'), key)
        return binascii.b2a_hex(passwd)

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()  # 用户id
    profile_img = scrapy.Field()  # 用户头像链接
    uname = scrapy.Field()  # 用户昵称
    url_name = scrapy.Field()  # 用户独一无二的域名后缀
    sex = scrapy.Field()  # 用户性别
    address = scrapy.Field()  # 用户地址
    emotion_status = scrapy.Field()  # 用户感情状况
    desc = scrapy.Field()  # 用户的描述
    n_fans = scrapy.Field()  # 粉丝数
    n_follow = scrapy.Field()  # 关注数
    n_weibo = scrapy.Field()  # 微博数
    verified_info = scrapy.Field()  # 认证信息
    tags = scrapy.Field()  # 用户标签
    edu_info = scrapy.Field()  # 学习经历
    work_info = scrapy.Field()  # 工作经历
    followers = scrapy.Field()  # 关注列表
    fans = scrapy.Field()  # 粉丝列表

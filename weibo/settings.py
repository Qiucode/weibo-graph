# -*- coding: utf-8 -*-

# Scrapy settings for weibo project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'weibo (+http://www.yourdomain.com)'

# My definitions
# DEFAULT_REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows;U;Windows'
# ' NT 5.1;zh-CN;rv:1.9.2.9)Gecko'
# '/20100824 Firefox/3.6.9',
#                            'Referer': ''}

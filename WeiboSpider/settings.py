# -*- coding: utf-8 -*-

# Scrapy settings for WeiboSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'WeiboSpider'

SPIDER_MODULES = ['WeiboSpider.spiders']
NEWSPIDER_MODULE = 'WeiboSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'WeiboSpider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:

# 请将Cookie替换成你自己的Cookie
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) Gecko/20100101 Firefox/61.0',
    'Cookie': '_T_WM=63026180584; WEIBOCN_FROM=1110106030; MLOGIN=1; SSOLoginState=1559802101; ALF=1562394101; SCF=ApQjNIh6QNqgIQ-rY6cQ5Vd-Ht3cDeOXBCYhu7Thh5eHq398aEchal9YOFrldnP2s-y2kA6xrLyieiMgIWBJpjs.; SUB=_2A25x_MClDeRhGeBP6lAT8S7FyD6IHXVTHuDtrDV6PUNbktAKLVSjkW1NRZBMrmsZ6yihxV588XVqgEdU_CLHdqcF; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFH-e7il7QNLoufDR1NovI_5JpX5KzhUgL.FoqpeKzEeK54e0z2dJLoIpjLxK.L1-zLB-2LxKqLB.eLB-zLxKnLBK2LB-zt; SUHB=0M2FZ4A1eGD2gJ; M_WEIBOCN_PARAMS=lfid%3D1076032803301701%26luicode%3D20000174%26uicode%3D20000174'

}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'WeiboSpider.middlewares.WeibospiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'WeiboSpider.middlewares.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'WeiboSpider.pipelines.MongoDBPipeline': 300,
}
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# MongoDb 配置

LOCAL_MONGO_HOST = '127.0.0.1'
LOCAL_MONGO_PORT = 27017
DB_NAME = 'weibocn'
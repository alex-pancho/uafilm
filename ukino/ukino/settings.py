# -*- coding: utf-8 -*-

# Scrapy settings for flats project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'ukino'

SPIDER_MODULES = ['ukino.spiders']
NEWSPIDER_MODULE = 'ukino.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'flats (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Scrapy provides 5 logging levels:
#    CRITICAL - for critical errors
#    ERROR - for regular errors
#    WARNING - for warning messages
#    INFO - for informational messages
#    DEBUG - for debugging messages

LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(os.getcwd(), 'ukino.log')
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32
# Configure maximum page connection count
#CLOSESPIDER_PAGECOUNT = 10

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False


ROTATING_PROXY_LIST_PATH = os.path.join(os.getcwd(), 'httpproxies.txt')  # Path that this library uses to store list of proxies
NUMBER_OF_PROXIES_TO_FETCH = 30  # Controls how many proxies to use

DOWNLOADER_MIDDLEWARES = {
    'rotating_free_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_free_proxies.middlewares.BanDetectionMiddleware': 620,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'ukino.pipelines.UkinoPipeline': 300,
    #'scrapy.pipelines.images.ImagesPipeline': 1,
    #'scrapy.pipelines.images.S3ImagesStore': 1
}

#  AWS parametrs
#  AWS_ACCESS_KEY_ID = ''
#  AWS_SECRET_ACCESS_KEY= ''

#IMAGES_STORE = 'images'
#  IMAGES_STORE = 's3://images/'
#  IMAGES_STORE_S3_ACL = 'public-read'
#FEED_URI='s3://images/filename.json'

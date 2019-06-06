# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ..items import *

from WeiboSpider.spiders.utils import time_fix
import time
import re

class WeiboSpiderSpider(scrapy.Spider):
    name = 'weibo_spider'
    allowed_domains = ['weibo.cn']
    # start_urls = ['http://weibo.cn/']
    base_url = "https://weibo.cn"

    def start_requests(self):
        start_uids = [
            '2803301701',  # 人民日报
            '1699432410'  # 新华社
        ]
        for uid in start_uids:
            yield Request(url="https://weibo.cn/{}/info".format(uid), callback=self.parse_information)

    def parse_information(self, response):
        """ 抓取个人信息 """
        information_item = InformationItem()
        information_item['crawl_time'] = int(time.time())
        information_item['_id'] = re.findall('(\d+)/info', response.url)[0]
        # 获取标签里的所有text()
        information_text = ";".join(response.xpath('//div[@class="c"]//text()').extract())

        nick_name = re.findall('昵称;?[：:]?(.*?);', information_text)
        if nick_name and nick_name[0]:
            information_item["nick_name"] = nick_name[0].replace(u"\xa0", "")
        gender = re.findall('性别;?[：:]?(.*?);', information_text)
        if gender and gender[0]:
            information_item["gender"] = gender[0].replace(u"\xa0", "")
        place = re.findall('地区;?[：:]?(.*?);', information_text)
        if place and place[0]:
            place = place[0].replace(u"\xa0", "").split()
            information_item["province"] = place[0]
            if len(place) > 1:
                information_item["city"] = place[1]
        briefIntroduction = re.findall('简介;?[：:]?(.*?);', information_text)
        if briefIntroduction and briefIntroduction[0]:
            information_item["brief_introduction"] = briefIntroduction[0].replace(u"\xa0", "")
        birthday = re.findall('生日;?[：:]?(.*?);', information_text)
        if birthday and birthday[0]:
            information_item['birthday'] = birthday[0]
        sex_orientation = re.findall('性取向;?[：:]?(.*?);', information_text)
        if sex_orientation and sex_orientation[0]:
            if sex_orientation[0].replace(u"\xa0", "") == gender[0]:
                information_item["sex_orientation"] = "同性恋"
            else:
                information_item["sex_orientation"] = "异性恋"
        sentiment = re.findall('感情状况;?[：:]?(.*?);', information_text)
        if sentiment and sentiment[0]:
            information_item["sentiment"] = sentiment[0].replace(u"\xa0", "")
        vip_level = re.findall('会员等级;?[：:]?(.*?);', information_text)
        if vip_level and vip_level[0]:
            information_item["vip_level"] = vip_level[0].replace(u"\xa0", "")
        authentication = re.findall('认证信息;?[：:]?(.*?);', information_text)
        if authentication and authentication[0]:
            information_item["authentication"] = authentication[0].replace(u"\xa0", "")
        labels = re.findall('标签;?[：:]?(.*?)更多>>', information_text)
        if labels and labels[0]:
            information_item["labels"] = labels[0].replace(u"\xa0", ",").replace(';', '').strip(',')

        yield Request(self.base_url + '/u/{}'.format(information_item['_id']),
                      callback=self.parse_further_information,
                      meta={'item': information_item},
                      dont_filter=True, priority=1)

    def parse_further_information(self, response):

        information_item = response.meta['item']
        tweets_num = re.findall('微博\[(\d+)\]', response.text)
        if tweets_num:
            information_item['tweets_num'] = int(tweets_num[0])
        follows_num = re.findall('关注\[(\d+)\]', response.text)
        if follows_num:
            information_item['follows_num'] = int(follows_num[0])
        fans_num = re.findall('粉丝\[(\d+)\]', response.text)
        if fans_num:
            information_item['fans_num'] = int(fans_num[0])
        yield information_item

        # 获取该用户微博
        yield Request(url=self.base_url + '/{}/profile?page=1'.format(information_item['_id']),
                      callback=self.parse_tweet, dont_filter=True, priority=1)

        # 获取关注列表
        yield Request(url=self.base_url + '/{}/follow?page=1'.format(information_item['_id']),
                      callback=self.parse_follow,
                      dont_filter=True)
        # 获取粉丝列表
        yield Request(url=self.base_url + '/{}/fans?page=1'.format(information_item['_id']),
                      callback=self.parse_fans,
                      dont_filter=True)

    # 解析该用户微博
    def parse_tweet(self, response):
        """
        解析本页的数据
        """
        tweet_nodes = response.xpath('//div[@class="c" and @id]')
        for tweet_node in tweet_nodes:
            try:
                tweet_item = TweetsItem()
                # 抓取时间戳
                tweet_item['crawl_time'] = int(time.time())
                tweet_repost_url = tweet_node.xpath('.//a[contains(text(),"转发[")]/@href').extract()[0]
                user_tweet_id = re.search(r'/repost/(.*?)\?uid=(\d+)', tweet_repost_url)
                # 微博URL
                tweet_item['weibo_url'] = 'https://weibo.com/{}/{}'.format(user_tweet_id.group(2),
                                                                           user_tweet_id.group(1))
                # 发表该微博用户的id
                tweet_item['user_id'] = user_tweet_id.group(2)
                # 微博id
                tweet_item['_id'] = '{}_{}'.format(user_tweet_id.group(2), user_tweet_id.group(1))

                create_time_info = ''.join(tweet_node.xpath('.//span[@class="ct"]').xpath('string(.)').extract())
                if "来自" in create_time_info:
                    # 微博发表时间
                    tweet_item['created_at'] = time_fix(create_time_info.split('来自')[0].strip())
                    # 发布微博的工具
                    tweet_item['tool'] = create_time_info.split('来自')[1].strip()
                else:
                    tweet_item['created_at'] = time_fix(create_time_info.strip())
                # 点赞数
                like_num = tweet_node.xpath('.//a[contains(text(),"赞[")]/text()').extract()[0]
                tweet_item['like_num'] = int(re.search('\d+', like_num).group())
                # 转发数
                repost_num = tweet_node.xpath('.//a[contains(text(),"转发[")]/text()').extract()[0]
                tweet_item['repost_num'] = int(re.search('\d+', repost_num).group())
                # 评论数
                comment_num = tweet_node.xpath(
                    './/a[contains(text(),"评论[") and not(contains(text(),"原文"))]/text()').extract()[0]
                tweet_item['comment_num'] = int(re.search('\d+', comment_num).group())
                # 图片
                images = tweet_node.xpath('.//img[@alt="图片"]/@src')
                if images:
                    tweet_item['image_url'] = images.extract()[0]
                # 视频
                videos = tweet_node.xpath('.//a[contains(@href,"https://m.weibo.cn/s/video/show?object_id=")]/@href')
                if videos:
                    tweet_item['video_url'] = videos.extract()[0]
                # 定位信息
                map_node = tweet_node.xpath('.//a[contains(text(),"显示地图")]')
                if map_node:
                    tweet_item['location'] = True
                # 原始微博，只有转发的微博才有这个字段
                repost_node = tweet_node.xpath('.//a[contains(text(),"原文评论[")]/@href')
                if repost_node:
                    tweet_item['origin_weibo'] = repost_node.extract()[0]

                # 检测有没有阅读全文:
                all_content_link = tweet_node.xpath('.//a[text()="全文" and contains(@href,"ckAll=1")]')
                if all_content_link:
                    all_content_url = self.base_url + all_content_link.xpath('./@href').extract()[0]
                    yield Request(all_content_url, callback=self.parse_all_content, meta={'item': tweet_item},
                                  priority=1)
                else:
                    # 微博内容
                    tweet_item['content'] = ''.join(tweet_node.xpath('./div[1]').xpath('string(.)').extract()
                                                    ).replace(u'\xa0', '').replace(u'\u3000', '').replace(' ',
                                                                                                          '').split(
                        '赞[', 1)[0]

                    if 'location' in tweet_item:
                        tweet_item['location'] = tweet_node.xpath('.//span[@class="ctt"]/a[last()]/text()').extract()[0]
                    yield tweet_item
                # 抓取该微博的评论信息
                comment_url = self.base_url + '/comment/' + tweet_item['weibo_url'].split('/')[-1] + '?page=1'
                yield Request(url=comment_url, callback=self.parse_comment, meta={'weibo_url': tweet_item['weibo_url']})

            except Exception as e:
                self.logger.error(e)

        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield Request(url, callback=self.parse_tweet, dont_filter=True)

    def parse_all_content(self, response):
        # 有阅读全文的情况，获取全文
        tweet_item = response.meta['item']
        tweet_item['content'] = ''.join(response.xpath('//*[@id="M_"]/div[1]').xpath('string(.)').extract()
                                        ).replace(u'\xa0', '').replace(u'\u3000', '').replace(' ', '').split('赞[', 1)[0]
        if 'location' in tweet_item:
            tweet_item['location'] = \
            response.xpath('//*[@id="M_"]/div[1]//span[@class="ctt"]/a[last()]/text()').extract()[0]
        yield tweet_item

    def parse_follow(self, response):
        """
        抓取关注列表
        """
        urls = response.xpath('//a[text()="关注他" or text()="关注她" or text()="取消关注"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/follow', response.url)[0]
        for uid in uids:
            relationships_item = RelationshipsItem()
            relationships_item['crawl_time'] = int(time.time())
            relationships_item["fan_id"] = ID
            relationships_item["followed_id"] = uid
            relationships_item["_id"] = ID + '-' + uid
            yield relationships_item

        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield Request(url, callback=self.parse_follow)

    def parse_fans(self, response):
        """
        抓取粉丝列表
        """
        urls = response.xpath('//a[text()="关注他" or text()="关注她" or text()="移除"]/@href').extract()
        uids = re.findall('uid=(\d+)', ";".join(urls), re.S)
        ID = re.findall('(\d+)/fans', response.url)[0]
        for uid in uids:
            relationships_item = RelationshipsItem()
            relationships_item['crawl_time'] = int(time.time())
            relationships_item["fan_id"] = uid
            relationships_item["followed_id"] = ID
            relationships_item["_id"] = uid + '-' + ID
            yield relationships_item

        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield Request(url, callback=self.parse_follow)

    # 抓取该微博的评论信息
    def parse_comment(self, response):
        for comment_node in response.xpath('//div[@class="c" and contains(@id,"C_")]'):
            comment_item = CommentItem()
            comment_item['crawl_time'] = int(time.time())
            comment_item['weibo_url'] = response.meta['weibo_url']
            comment_item['comment_user_id'] = comment_node.xpath('./a[1]/@href'
                                                                 ).extract()[0].split('/u/', 1)[-1].split('/', 1)[-1]
            comment_item['content'] = ''.join(comment_node.xpath('string(.)').extract()
                                              ).replace(u'\xa0', '').replace(' ', '').split('举报赞[', 1)[0]
            comment_item['_id'] = comment_node.xpath('./@id').extract()[0]

            like_num = comment_node.xpath('.//a[contains(text(),"赞[")]/text()').extract()[-1]
            comment_item['like_num'] = int(re.search('\d+', like_num).group())

            created_at_info = comment_node.xpath('.//span[@class="ct"]/text()').extract()[0]
            comment_item['created_at'] = time_fix(created_at_info.split('\xa0')[0])
            yield comment_item

        next_page = response.xpath('//div[@id="pagelist"]//a[contains(text(),"下页")]/@href')
        if next_page:
            url = self.base_url + next_page[0].extract()
            yield Request(url, callback=self.parse_comment,
                          meta={'weibo_url': comment_item['weibo_url']})

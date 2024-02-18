# Scrapy settings for nieuwbouwscraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

settings = {
    "BOT_NAME": "nieuwbouwscraper",
    "SPIDER_MODULES": ["ClappScrapers.nieuwbouw.spider"],
    "NEWSPIDER_MODULE": "ClappScrapers.nieuwbouw.spider",
    "ROBOTSTXT_OBEY": True,
    "ITEM_PIPELINES": {
        "ClappScrapers.nieuwbouw.spider.pipelines.MergedDataPipeline": 100,
    },
    "DOWNLOADER_MIDDLEWARES":{
        "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware":None,
        "scrapy_user_agents.middlewares.RandomUserAgentMiddleware":700,
        "ClappScrapers.nieuwbouw.spider.middlewares.NieuwbouwscraperDownloaderMiddleware":500,
    },
    "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    "FEED_EXPORT_ENCODING": "utf-8",
    #"CUSTOM_LOG_EXTENSION":True,
    # "EXTENSIONS":{
    #     'scrapy.extensions.telnet.TelnetConsole': None,
    #     'ClappScrapers.nieuwbouw.spider.extension.CustomLogExtension': 1,}
}

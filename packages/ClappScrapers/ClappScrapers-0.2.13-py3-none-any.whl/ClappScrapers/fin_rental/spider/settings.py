
settings = {
  "BOT_NAME": "finlandrentalscraper",
  "SPIDER_MODULES": ["ClappScrapers.fin_rental.spider"],
  "NEWSPIDER_MODULE": "ClappScrapers.fin_rental.spider",
  "ROBOTSTXT_OBEY": True,
  "ITEM_PIPELINES": {
      "ClappScrapers.fin_rental.spider.pipelines.MergedDataPipeline": 100,
  },
  "DOWNLOADER_MIDDLEWARES": {
      "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
      "scrapy_user_agents.middlewares.RandomUserAgentMiddleware": 700,
  },
  "AUTOTHROTTLE_ENABLED": True,
  "AUTOTHROTTLE_START_DELAY": 0.5,
  "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
  "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
  "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
  "FEED_EXPORT_ENCODING": "utf-8",
  "CUSTOM_LOG_EXTENSION":True,
  "EXTENSIONS":{
    'scrapy.extensions.telnet.TelnetConsole': None,
    'ClappScrapers.fin_rental.spider.extension.CustomLogExtension': 1,}
}
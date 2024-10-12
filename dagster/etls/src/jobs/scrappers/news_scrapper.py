from dagster import AutoMaterializePolicy, FreshnessPolicy, asset, get_dagster_logger
from bson import ObjectId
from etls.src.spiders.eldeber_spider import ElDeberSpider
from scrapy.crawler import CrawlerProcess

logger = get_dagster_logger()

@asset(
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def news_scrapper():
    
    process = CrawlerProcess()
    process.crawl(ElDeberSpider)
    process.start()

if __name__ == "__main__":
    try:
        news_scrapper()
    except Exception as e:
        logger.error(e)
    
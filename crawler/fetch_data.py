import threading

from usp.tree import sitemap_tree_for_homepage
import scrapy
from scrapy.crawler import CrawlerProcess
from fastapi import FastAPI
from fastmcp import FastMCP
app = FastAPI()
mcp = FastMCP("WebCrawler")


def crawl_sitemap(link):
    tree = sitemap_tree_for_homepage(link)
    return list({page.url for page in tree.all_pages()})


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 5,
    }

    def start_requests(self):
        target_url = getattr(self, 'target_url', 'https://nitsan.ai/')
        sitemap_urls = crawl_sitemap(target_url)

        for link in sitemap_urls:
            yield scrapy.Request(url=link, callback=self.parse)

    def parse(self, response):
        yield {
            "url": response.url,
            "title": response.css("title::text").get(),
            "headings": response.css("h1::text, h2::text").getall(),
            "paragraphs": response.css("p::text").getall(),
            "links": response.css("a::attr(href)").getall(),
        }


def run_spider(target_url='https://nitsan.ai/'):
    process = CrawlerProcess(settings={
        "FEEDS": {"/tmp/output.csv": {"format": "csv", "overwrite": True}},
    })
    process.crawl(QuotesSpider, target_url=target_url)
    process.start()


@mcp.tool("fetch_website", description="Crawl a website and extract data")
def fetch_website():
    thread = threading.Thread(target=run_spider)
    thread.start()
    return {"status": "crawling started"}

if __name__ == "__main__":
    mcp.run(transport="stdio")
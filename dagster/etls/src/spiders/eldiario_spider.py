import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy import Request
from scrapy.spiders import Spider
from datetime import datetime

import os
from etls.src.jobs.mongodb_client import MongoDBClient
mongo_uri = os.getenv("MONGO_DB_URI")
db_name = os.getenv("DB_NAME")
collection = os.getenv("COLLECTION_NAME")

client = MongoDBClient(mongo_uri, db_name, collection)

class ElDiarioSpider(Spider):
    name = "eldiario"
    allowed_domains = ["eldiario.net"]
    start_urls = [
        f"https://www.eldiario.net/portal/page/{i}/?s=feminicidio" for i in range(1, 60)
        
    ]
    def __init__(self):
        self.items = []
        self.mongo_client = client
    def date_formatter(self, date_str, date_format="%Y-%m-%d"):
        try:
            new_date = datetime.strptime(date_str, date_format)
            return new_date
        except Exception as e:
            self.logger.error(f"Error al formatear fecha: {e}")
            return None

    def tittle_formatter(self, title):
        try:
            new_title = title.replace("“", '"').replace("”", '"')
            return new_title
        except Exception as e:
            self.logger.error(f"Error al formatear título: {e}")
            return title

    def section_formatter(self, section):
        try:
            new_section = section.lower()
            return new_section
        except Exception as e:
            self.logger.error(f"Error al formatear sección: {e}")
            return section

    def body_formatter(self, body):
        try:
            new_body = [b for b in body if "Lea tamb" not in b and b.strip()]
            new_body = [
                b.strip()
                .replace("\xa0", " ")
                .replace("\ufeff", " ")
                .replace("“", '"')
                .replace("”", '"')
                .replace("\u200b", " ")
                for b in new_body
            ]
            new_body = [b for b in new_body if b != " "]
            return new_body
        except Exception as e:
            self.logger.error(f"Error al formatear cuerpo: {e}")
            return body

    def start_requests(self):
        for url in self.start_urls:
            self.logger.info(f"Enviando request a: {url}")
            yield Request(url=url, callback=self.parse_response)

    def parse_response(self, response):
        self.logger.info(f"Recibida respuesta: {response.url}")
        try:
            noticias = response.xpath("//h3[contains(@class, 'entry-title')]/a/@href").getall()
            self.logger.info(f"Total noticias encontradas: {len(noticias)}")
            for noticia in noticias:
                self.logger.info(f"Enviando request a: {noticia}")
                yield Request(url=noticia, callback=self.parse_news)
        except Exception as e:
            self.logger.error(f"Error al procesar la respuesta JSON: {e}")
            return

    def parse_news(self, response):
        title = response.xpath("//h1[@class='tdb-title-text']/text()").get()
        item = {}
        item["url"] = response.url
        item["title"] = self.tittle_formatter(title)
        section = response.xpath("//a[@class='tdb-entry-category']/text()").get()
        item["section"] = self.section_formatter(section)
        body = [
            p.xpath("string(.)").get()
            for p in response.xpath("//div[contains(@class, 'td-fix-index')]/p")
        ]
        item["body"] = self.body_formatter(body)
        item["tags"] = []
        date_published = response.xpath("//time[contains(@class, 'td-module-date')]/text()").get()
        item["date_published"] = self.date_formatter(date_published,"%d/%m/%Y")
        item["source"] = "eldiario"
        if item["section"] not in ["Portada"]:
            self.items.append(item)
            self.logger.info(f"Noticia agregada: {item['title']}")

    def close(self, reason):
        self.mongo_client.connect()
        self.logger.info("Guardando datos en MongoDB")
        for item in self.items:
            try:
                self.mongo_client.insert_new_document(item, "url")
            except Exception as e:
                self.logger.error(f"Error al insertar en MongoDB: {e}")

        self.logger.info(f"Spider cerrado por la razón: {reason}")
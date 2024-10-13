import scrapy
import pandas as pd
from scrapy import Request
from scrapy.spiders import Spider
from datetime import datetime

import os
from etls.src.jobs.mongodb_client import MongoDBClient

mongo_uri = os.getenv("MONGO_DB_URI")
db_name = os.getenv("DB_NAME")
collection = os.getenv("COLLECTION_NAME")

client = MongoDBClient(mongo_uri, db_name, collection)

class ElDeberSpider(Spider):
    name = "eldeber"
    allowed_domains = ["eldeber.com.bo"]
    start_urls = [
        "https://eldeber.com.bo/api/news/getMoreSearch?from=0&tag=feminicidios"
        
    ]
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
    }

    def __init__(self):
        self.items = []
        self.mongo_client = client

    def full_url_formatter(self, base_url, url, nodo, n_id):
        try:
            repl = {
                "à": "a",
                "á": "a",
                "â": "a",
                "ã": "a",
                "é": "e",
                "ê": "e",
                "í": "i",
                "ó": "o",
                "ô": "o",
                "õ": "o",
                "ú": "u",
                "ü": "u",
            }
            if len(nodo) > 1:
                new_nodo = nodo[1].lower()
            else:
                new_nodo = nodo[0].lower()

            new_nodo = "".join([repl[c] if c in repl else c for c in new_nodo])
            new_nodo = new_nodo.strip().replace(" ", "-")
            full_url = base_url + "/{}/{}_{}".format(new_nodo, url, n_id)
            return full_url
        except Exception as e:
            self.logger.error(f"Error al formatear URL: {e}")
            return None

    def date_formatter(self, date_str):
        try:
            new_date = datetime.strptime(date_str, "%Y-%m-%d")
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

    def tag_formatter(self, tags):
        try:
            new_tags = [t.lower() for t in tags]
            return new_tags
        except Exception as e:
            self.logger.error(f"Error al formatear tags: {e}")
            return tags

    def start_requests(self):
        for url in self.start_urls:
            self.logger.info(f"Enviando request a: {url}")
            yield Request(url=url, callback=self.parse_api_response)

    def parse_api_response(self, response):
        self.logger.info(f"Recibida respuesta de la API: {response.url}")
        try:
            noticias = response.json()
            self.logger.info(f"Total noticias encontradas: {len(noticias)}")
            self.logger.info(noticias)
        except Exception as e:
            self.logger.error(f"Error al procesar la respuesta JSON: {e}")
            return

        for n in noticias:
            self.logger.debug(f"Procesando noticia: {n}")
            excluded_paths = [
                "/opinion/",
                "/mundo/",
                "/bbc/",
                "/tendencias/",
                "/economia/",
                "/escenas/",
            ]
            data = {}

            try:
                data["url"] = self.full_url_formatter(
                    "https://eldeber.com.bo", n["Url"], n["Nodes_en"], n["Id"]
                )
                if all(excluded not in data["url"] for excluded in excluded_paths):
                    data["date_published"] = self.date_formatter(
                        n["PublicationDate"][:10]
                    )
                    data["source"] = "eldeber"
                    self.logger.debug(f"Datos recuperados: {data}")
                    yield Request(data["url"], self.parse_news, meta={"data": data})
            except Exception as e:
                self.logger.error(f"Error al procesar noticia: {e}")
                continue

    def parse_news(self, response):
        item = response.meta["data"]
        title = response.xpath("//div[@class='text']/h1/text()").get()
        item["title"] = self.tittle_formatter(title)
        section = response.xpath("//span[@class='section']/text()").get()
        item["section"] = self.section_formatter(section)
        body = [
            p.xpath("string(.)").get()
            for p in response.xpath("//div[contains(@class, 'text-editor')]/div/p")
        ]
        item["body"] = self.body_formatter(body)
        tags = response.xpath(
            "//div[contains(@class,'widget-content')]/ul/li/a/text()"
        ).getall()
        item["tags"] = self.tag_formatter(tags)
        self.logger.debug(f"Tags recuperadas: {tags}")
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

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class OlxPipeline:
    def __init__(self):
        hostname = "176.102.65.29"
        port = "5432"
        username = "bot"
        password = "1992"
        database = "apartments"
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database, port=port)
        self.cursor = self.connection.cursor()

    def open_spider(self, spider):
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS apartments_tb(
        id BIGSERIAL NOT NULL PRIMARY KEY,
        title TEXT NOT NULL,
        price INT NOT NULL,
        currency VARCHAR(10) NOT NULL,
        floor INT NOT NULL,
        rooms INT NOT NULL,
        district TEXT,
        city TEXT,
        region TEXT,
        date TIMESTAMP,
        created TIMESTAMP,
        url TEXT,
        description TEXT NOT NULL,
        images TEXT[]
        )
        """)

    def process_item(self, item, spider):
        self.cursor.execute("""
            INSERT INTO apartments_tb (title, price, currency, floor, rooms, description, district, city, 
            region, date, url, images, created)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, [
            item['title'],
            item['price'],
            item['currency'],
            item['floor'],
            item['rooms'],
            item['description'],
            item['district'],
            item['city'],
            item['region'],
            item['date'],
            item['url'],
            item['images'],
            item['created']
        ]
                            )

        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

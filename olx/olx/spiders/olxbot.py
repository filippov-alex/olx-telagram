import scrapy
import dateparser
from datetime import datetime
import json
from ..items import OlxItem


class OlxSpider(scrapy.Spider):
    name = "olx"
    start_urls = [
        "https://www.olx.ua/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/1-komnata/",
        "https://www.olx.ua/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/2-komnaty/",
        "https://www.olx.ua/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/3-komnaty/",
        "https://www.olx.ua/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/4-komnaty/",
        "https://www.olx.ua/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/5-komnat/",
        # "https://www.scrapethissite.com/pages/forms/"
    ]

    def parse(self, response):
        location_links = response.css("div.locationlinks.margintop10 a::attr(href)").getall()
        if len(location_links) > 0:
            for location in location_links:
                yield response.follow(location, callback=self.parse)
        else:
            page_links = response.css("#offers_table h3.lheight22.margintop5 a::attr(href)").getall()
            for link in page_links:
                yield response.follow(link, callback=self.parse_ad)
            next_page = response.css("span.next a.link.pageNextPrev::attr(href)").get()
            if next_page is not None:
                yield response.follow(next_page, self.parse)

    def parse_ad(self, response):
        items = OlxItem()
        items["title"] = response.css("h1.css-r9zjja-Text.eu5v0x0::text").get()
        items["price"] = int(response.css(".css-okktvh-Text::text").getall()[0].replace(" ", ""))
        items["currency"] = response.css(".css-okktvh-Text::text").getall()[2]
        description = self.parse_description(response.css("li.css-ox1ptj p::text").getall())
        items["description"] = json.dumps(description, ensure_ascii=False)  # utf8 not supported
        items["district"] = self.parse_address(response.css(".css-7dfllt:nth-child(8) .css-tyi2d1::text").get())
        items["city"] = self.parse_address(response.css(".css-7dfllt:nth-child(7) .css-tyi2d1::text").get())
        items["region"] = self.parse_address(response.css(".css-7dfllt:nth-child(6) .css-tyi2d1::text").get())
        items["date"] = self.timestamp_from_rus_date(response.css("div.css-sg1fy9 span.css-19yf5ek::text").get())
        items["url"] = response.url
        items["rooms"] = int(description["Количество комнат"][1])
        items["floor"] = int(description["Этаж"][1])
        items["images"] = response.css(".swiper-zoom-container img::attr(data-src)").getall()
        items["images"].append(response.css("div.swiper-container img::attr(src)").get())
        items["created"] = datetime.now()
        yield items

    def parse_description(self, description):
        desc_dict = {}

        for item in description:
            if ":" in item:
                desc_dict[item.split(":")[0]] = item.split(":")[1]
            else:
                desc_dict["Others"] = item

        return desc_dict

    def parse_address(self, address):
        if address is not None:
            if "-" in address:
                return address.split(" - ")[1].strip()
        else:
            return address

    def timestamp_from_rus_date(self, rus_date):
        date_obj = dateparser.parse(rus_date)
        # date_timestamp = datetime.timestamp(date_obj)
        return date_obj

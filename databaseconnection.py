import psycopg2
from pprint import pprint


class DatabaseConnection:
    def __init__(self):
        self.hostname = "176.102.65.29"
        self.port = "5432"
        self.username = "bot"
        self.password = "1992"
        self.database = "apartments"
        self.table = "apartments_tb"

    def to_connect(self):
        self.connect = psycopg2.connect(host=self.hostname, user=self.username, password=self.password,
                                        dbname=self.database, port=self.port)
        self.cursor = self.connect.cursor()

    def get_regions(self):
        command = f"""SELECT DISTINCT region FROM {self.table}
                    ORDER BY region"""
        self.to_connect()
        self.cursor.execute(command)
        regions = self.create_list(self.cursor.fetchall())
        self.connect.close()
        return regions

    def get_cities(self, region):
        command = f"""SELECT DISTINCT city FROM {self.table} WHERE region = '{region}'
                    ORDER BY city"""
        self.to_connect()
        self.cursor.execute(command)
        cities = self.create_list(self.cursor.fetchall())
        self.connect.close()
        return cities

    def get_districts(self, region, city):
        command = f"""SELECT DISTINCT district FROM {self.table} WHERE region = '{region}' AND city = '{city}'
                    ORDER by district"""
        self.to_connect()
        self.cursor.execute(command)
        districts = self.create_list(self.cursor.fetchall())
        self.connect.close()
        return districts

    def get_rooms(self, region, city, district=''):
        if district != "":
            command = f"""SELECT DISTINCT rooms FROM {self.table} 
                        WHERE region = '{region}' AND city = '{city}' AND district='{district}'"""
        else:
            command = f"""SELECT DISTINCT rooms FROM {self.table} 
                        WHERE region = '{region}' AND city = '{city}'"""
        self.to_connect()
        self.cursor.execute(command)
        rooms = self.create_list(self.cursor.fetchall())
        self.connect.close()
        return rooms

    def get_price(self, rooms, region, city, district=''):
        if district !="":
            command = f"""SELECT min(price) FROM {self.table} 
                        WHERE region = '{region}' AND city = '{city}' AND district='{district}' and rooms='{rooms}'"""
            self.to_connect()
            self.cursor.execute(command)
            price_min = self.create_list(self.cursor.fetchall())
            command = f"""SELECT max(price) FROM {self.table} 
                        WHERE region = '{region}' AND city = '{city}' AND district='{district}' and rooms='{rooms}'"""
            self.to_connect()
            self.cursor.execute(command)
            price_max = self.create_list(self.cursor.fetchall())
        else:
            command = f"""SELECT min(price) FROM {self.table} 
                        WHERE region = '{region}' AND city = '{city}' and rooms='{rooms}'"""
            self.to_connect()
            self.cursor.execute(command)
            price_min = self.create_list(self.cursor.fetchall())
            command = f"""SELECT max(price) FROM {self.table} 
                        WHERE region = '{region}' AND city = '{city}' and rooms='{rooms}'"""
            self.to_connect()
            self.cursor.execute(command)
            price_max = self.create_list(self.cursor.fetchall())
        return price_min[0], price_max[0]

    def create_list(self, values):
        new_list = []
        for value in values:
            new_list.append(value[0])
        return new_list

    def get_list(self, region, city, district, price_low, price_top, rooms: int):
        if district !="":
            command = f"""SELECT * FROM {self.table} WHERE region = '{region}' AND city = '{city}' AND district = '{district}' AND rooms = {rooms} AND price BETWEEN {price_low} and {price_top}
                        ORDER BY date DESC """
        else:
            command = f"""SELECT * FROM {self.table} WHERE region = '{region}' AND city = '{city}' AND rooms = {rooms} AND price BETWEEN {price_low} and {price_top}
                        ORDER BY date DESC """
        self.to_connect()
        self.cursor.execute(command)
        apartments = self.cursor.fetchall()
        self.connect.close()
        return apartments

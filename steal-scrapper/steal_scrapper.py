from bs4 import BeautifulSoup
#import re
import numpy as np
import pandas as pd
#import sys
import cfscrape
import threading
#import os
import csv
import json
from igdb.wrapper import IGDBWrapper
import requests
from pymongo import MongoClient


class Steal:
    def __init__(
        self,
        csv_name,
        page_limit,
        twitch_client_id,
        twitch_client_secret,
        db_passwd,
        pushdb=False,
    ):
        self.start_page_num = 1
        self.scraper = cfscrape.create_scraper()
        self.csv_name = csv_name
        self.page_limit = page_limit
        self.twitch_client_id = twitch_client_id
        self.twitch_client_secret = twitch_client_secret
        self.reset_lists()

        ## mongo database
        self.pushdb = pushdb
        self.db_passwd = db_passwd
        ## change the link to your own DO NOT HARD CODE THE PASSWORD
        self.cluster = f"mongodb+srv://steal:{self.db_passwd}@cluster0.qvfna.mongodb.net/?retryWrites=true&w=majority"
        self.client = MongoClient(self.cluster)
        self.db = self.client.gamesdb
        self.gamesdb = self.db.games

    def reset_lists(self):
        self.urllist = []
        self.filenamelist = []
        self.seederlist = []
        self.leecherlist = []
        self.sizelist = []
        self.datelist = []
        self.splitarr = []
        self.magnetlinks = []

    def task1(self):
        for url1 in self.splitarr[0]:
            self.scrape_induvidual(url1)

    def task2(self):
        for url2 in self.splitarr[1]:
            self.scrape_induvidual(url2)

    def task3(self):
        for url3 in self.splitarr[2]:
            self.scrape_induvidual(url3)

    def scrape_induvidual(self, url):
        source = self.scraper.get(url).text
        soup = BeautifulSoup(source, "lxml")

        leftside = []
        rightside = []

        for h1_tag in soup.find("h1"):
            self.filenamelist.append(h1_tag)

        for ul_tag in soup.find_all("ul", {"class": "list"}):
            for li_tag in ul_tag.find_all("li"):
                leftside.extend(
                    strong_tag.text for strong_tag in li_tag.find_all("strong")
                )
                rightside.extend(span_tag.text for span_tag in li_tag.find_all("span"))

        combined = np.column_stack([leftside, rightside])

        for each_detail in combined:
            if "Seeders" in each_detail[0]:
                self.seederlist.append(each_detail[1])
            if "Leechers" in each_detail[0]:
                self.leecherlist.append(each_detail[1])
            if "Total size" in each_detail[0]:
                self.sizelist.append(each_detail[1])
            if "Date uploaded" in each_detail[0]:
                self.datelist.append(each_detail[1])
        self.magnetlinks.append(
            soup.find(string="Magnet Download").find_parent("a").get("href")
        )

    def run(self):
        print("scrapping for games")

        while True:
            if self.start_page_num == self.page_limit:
                print("scrapping is done")
                self.clean()
                self.to_json()

                if self.pushdb:
                    self.push_to_db()

                exit()
            else:
                source = self.scraper.get(
                    f"https://1337x.to/johncena141-torrents/{self.start_page_num}/"
                ).content
                soup = BeautifulSoup(source, "lxml")

                tablebody = soup.find("tbody")
                # extract page links for every torrent and store it in an array
                for tag in tablebody.find_all("a"):
                    temp_url = tag.get("href").split("/")
                    if "torrent" in temp_url[1]:
                        self.urllist.append("https://1337x.to" + (tag.get("href")))

                # split array for parralel scraping
                self.splitarr = np.array_split(self.urllist, 3)

                t1 = threading.Thread(target=self.task1, name="t1")
                t2 = threading.Thread(target=self.task2, name="t2")
                t3 = threading.Thread(target=self.task3, name="t3")

                t1.start()
                t2.start()
                t3.start()

                t1.join()
                t2.join()
                t3.join()

                combined = np.column_stack(
                    [
                        self.filenamelist,
                        self.seederlist,
                        self.leecherlist,
                        self.sizelist,
                        self.datelist,
                        self.magnetlinks,
                    ]
                )
                df = pd.DataFrame(combined)

                df.to_csv(f"{self.csv_name}.csv", mode="a", index=False)
                self.start_page_num += 1
                self.reset_lists()

    def clean(self):
        print("cleaning dataset")
        df0 = pd.read_csv(f"{self.csv_name}.csv")
        df1 = df0.loc[df0["0"] != "0"]

        df2 = df1.loc[df1["3"] != "0"]

        df3 = df2.loc[df2["3"] != "1"]

        # df3.drop("Unnamed: 6", axis=1, inplace=True)

        ### adding readable rows
        data = [
            {
                "no": "",
                "name": "",
                "seeders": "",
                "leechers": "",
                "size": "",
                "date": "",
                "magnet": "",
                "pltfrm": "",
                "cover": "",
                "summary": "",
            }
        ]
        df = pd.DataFrame(data)
        df.to_csv(f"{self.csv_name}.csv", mode="w", index=False)

        df3.to_csv(f"{self.csv_name}.csv", mode="a", index=True)
        print("cleaning is done")

    def to_json(self):
        print("converting csv to json")
        data = {}
        # Open a csv reader called DictReader
        with open(f"{self.csv_name}.csv", encoding="utf-8") as csvf:
            csvReader = csv.DictReader(csvf)

            # Convert each row into a dictionary
            # and add it to data
            for rows in csvReader:
                key = rows["no"]
                data[key] = rows

        # Open a json writer, and use the json.dumps()
        # function to dump data

        del data[""]
        with open(f"{self.csv_name}.json", "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(data, indent=4))

        print("converting to json is done")

        ## update pltfrm and trim name and get cover art
        self.pltfrm()

    def cover(self, game):
        r = requests.post(
            f"https://id.twitch.tv/oauth2/token?client_id={self.twitch_client_id}&client_secret={self.twitch_client_secret}&grant_type=client_credentials"
        )

        access_token = json.loads(r._content)["access_token"]

        wrapper = IGDBWrapper(f"{self.twitch_client_id}", access_token)

        # JSON API request
        byte_array = wrapper.api_request(
            "games", f'search "{game}"; fields cover, summary; offset 0;'
        )
        # parse into JSON however you like...

        data = json.loads(byte_array)

        with open("mine.json", "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(data, indent=4))

        df = pd.read_json("mine.json")
        df.dropna(inplace=True)

        df.reset_index(drop=True, inplace=True)
        # int(df['id'].values)
        print(df)
        return self.get_cover(int(df["cover"][0])), df["summary"][0]

    def get_cover(self, cover_id):
        r = requests.post(
            f"https://id.twitch.tv/oauth2/token?client_id={self.twitch_client_id}&client_secret={self.twitch_client_secret}&grant_type=client_credentials"
        )

        access_token = json.loads(r._content)["access_token"]

        wrapper = IGDBWrapper(f"{self.twitch_client_id}", access_token)

        # JSON API request
        byte_array = wrapper.api_request(
            "covers", f"fields url; where id = {cover_id};"
        )
        # parse into JSON however you like...

        data = json.loads(byte_array)

        with open("mine.json", "w", encoding="utf-8") as jsonf:
            jsonf.write(json.dumps(data, indent=4))

        df = pd.read_json("mine.json")
        url = "https:" + str(df["url"].values[0])
        return url.replace("thumb", "1080p")

    def pltfrm(self):
        print("updating pltfrm")
        df = pd.read_json(f"{self.csv_name}.json")
        dic = dict(df)
        num = int(list(dic.keys())[-1])

        for i in range(num + 1):
            try:
                if df[i]["magnet"].find("Wine") != -1:
                    df[i]["pltfrm"] = "wine"
                elif df[i]["magnet"].find("Native") != -1:
                    df[i]["pltfrm"] = "native"
            except KeyError:
                continue
        print("updating pltfrm is done")

        print("trimming names and fetching covers")
        for i in range(num + 1):
            try:
                if df[i]["name"].find("-") != -1:
                    df[i]["name"] = df[i]["name"].split("-", 1)[0]
                else:
                    df[i]["name"] = df[i]["name"].split("[", 1)[0]

                print(df[i]["no"])

                df[i]["cover"], df[i]["summary"] = self.cover(
                    df[i]["name"].replace("–", "-").replace("’", "'")
                )
            except KeyError:
                continue
        print("fetching covers is done")

        df.to_json(f"{self.csv_name}.json")

    def push_to_db(self):
        print("deleting old db")
        self.gamesdb.delete_many({})
        print("pushing to database")
        df = pd.read_json(f"{self.csv_name}.json")
        data = dict(df)
        num = int(list(data.keys())[-1])
        print(num)
        for i in range(num + 1):
            try:
                if data[i]["pltfrm"] != "wine" and data[i]["pltfrm"] != "native":
                    continue
                else:
                    self.gamesdb.insert_one(dict(data[i]))
            except KeyError:
                continue
        print("pushing to db done")

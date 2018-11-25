# niter.py
# docs and impl to talk to the nelson json server thingy
# see the readme for more info.

import requests

GET_EXP_INTER = "http://www.mynelson.com/mynelson/service/explorer/getexplorerinterface.json"
GET_LINKS     = "http://www.mynelson.com/mynelson/service/productdetail/links.json"
GET_CONT_URL  = "https://www.mynelson.com/mynelson/service/openlink/getLinkURL.json"

class Link:
    def __init__(self, book, level, link_data):
        self.book = book
        self.info = link_data
        self.level = level

    @property
    def title(self):
        return self.info["title"]

    @property
    def url(self):
        content_url = self.book.access_url + "/" + self.info["contentURL"]
        # send request to getLinkURL
        token = self.book.send_request(GET_CONT_URL, params={
            "linkID": self.link_id,
            "levelID": self.level.level_id
        }).json()["Response"]["Token"]

        return content_url + "?token=" + token

    @property
    def file_type(self):
        return self.info["fileType"]

    @property
    def link_id(self):
        return self.info["navLinkId"]

class Level:
    def __init__(self, book, link_data):
        self.book = book
        self.info = link_data

        self.has_links = self.info["hasLinks"]
        if self.has_links:
            link_info = self.book.send_request(GET_LINKS, params={"productid": book.product_id, "levelid": self.level_id}).json()["Response"]["NavLinkTitleList"]
            self.link_info = [Link(book, self, x) for x in link_info]

    @property
    def title(self):
        return self.info["title"]

    @property
    def level_id(self):
        return self.info["navLevelId"]

    def __len__(self):
        return len(self.info["childList"])

    def __getitem__(self, k):
        return Level(self.book, self.info["childList"][k])

class Book:
    def __init__(self, product_id, session_id, server_id):
        self.product_id = product_id
        self.session_id = session_id
        self.server_id = server_id
        self.info = None
        self.load()

    def send_request(self, url, **kwargs):
        return requests.get(url, cookies={"JSESSIONID": self.session_id,
                                          "BIGipServerwhcinxtomcat8p": self.server_id},
                                headers={"User-Agent": "curl/7.58.0"}, **kwargs)

    def load(self):
        self.info = self.send_request(GET_EXP_INTER, params={"productid": str(self.product_id)}).json()["Response"]

    @property
    def title(self):
        return self.info["ProductInfo"]["title"]

    @property
    def access_url(self):
        return self.info["ProductInfo"]["accessUrl"]

    def __len__(self):
        return len(self.info["NavLevelTitleList"])
    
    def __getitem__(self, k):
        return Level(self, self.info["NavLevelTitleList"][k])

# Author: vugz @ GitHub
# Python 3.10.6

from dataclasses import dataclass
import os

import asyncio
import aiohttp
import aiosqlite

from bs4 import BeautifulSoup
import datetime

from db_handler import DBHandler
from parse import Parser
from log import Log

class Subscriber:
    """ 
        A Subscriber identified by a name, webhook endpoint and feed URL.

        The name will be used to differenciate Subscribers internally.
        All subscriber instances should have different names.
    """
    def __init__(self, webhook_name: str, webhook_url: str, feed_url: str, parser: Parser):
        self._name = webhook_name 
        self._webhook_url = webhook_url
        self._feed_url = feed_url
        self._parser = parser
        self._db_handler = DBHandler()
        self._session = aiohttp.ClientSession()
    

    @property
    def name(self):
        return self._name

    async def update(self):
        # check for no updates
        etag, last_modified, last_build = self._get_modification_information()

        # make a conditional GET request
        resp = await self._make_conditional_get_request(etag, last_modified)
        if resp.status == 304:
            # 304 -> Not modified resource
            print(f"No new logs for {self.name}")
            await self._session.close()
            return

        # store new ETag and Last-Modified values
        try:
            new_etag = resp.headers["Etag"]
            new_last_modified = resp.headers["Last-Modified"]
        except KeyError:
            # some websites don't provide this functionality 
            new_etag = new_last_modified = "***"
        
        feed_content = await resp.text()

        # get last build date
        soup = BeautifulSoup(feed_content, "xml")
        new_last_build = soup.find("channel").find("lastBuildDate").text[:-6]

        # convert recorded stamp and new stamp to datetime objects
        last_build_obj = datetime.datetime.strptime(last_build, "%a, %d %b %Y %H:%M:%S")
        last_build_reg_obj = datetime.datetime.strptime(new_last_build, "%a, %d %b %Y %H:%M:%S")

        # compare stored last build date and new one 
        if last_build_obj == last_build_reg_obj:
            await self._session.close()
            print(f"No new logs for {self.name}")
            return

        # update information
        self._update_modification_information(new_etag, new_last_modified, new_last_build)

        # initialize db handler
        await self._db_handler.initialize(self.name)

        # parse all the logs in feed
        logs = await self._parse_feed(feed_content)

        # ditch previously submitted logs 
        new_logs = [log for log in logs if not 
                                await self._db_handler.is_log_in_db(self.name, log)]

        # attempt to fetch a preview image for each log
        results = await asyncio.gather(*[self._fetch_preview_image(log) 
                                        for log in new_logs])

        # assign all image previews
        for i in range(len(results)):
            if results[i] != -1:
                new_logs[i].image = results[i]

        # post all new logs to webhook
        results = await asyncio.gather(*[self._post_log_to_hooks(log) 
                                                for log in new_logs])

        # save submitted logs to database, if log was not succesfully delivered it isn't saved 
        succesful_logs = [new_logs[i] for i in range(len(results)) 
                                                if results[i] == 0]
        await self._db_handler.save_new_logs(self.name, succesful_logs)

        await self._session.close()
        await self._db_handler.close_session()

    async def _post_log_to_hooks(self, log: Log) -> int:
        # attempt to post 5 times every 10 seconds (in case we get 429 responses)
        attempts = 5 
        while attempts > 0:
            resp = await self._session.post(self._webhook_url, json=log.to_payload(self.name))

            # if we make too many requests we might be timed out
            if resp.status == 429:
                await asyncio.sleep(10)
                attempts += 1
                continue
            elif resp.status not in [200, 204]:
                # if an error occurred
                return -1
            
            return 0
        
        # if we were timed out on every request
        return -1 


    async def _fetch_preview_image(self, log: Log) -> str:
        """ Attempt to get a preview image in new Log location """
        if log.image != "":
            return -1

        async with self._session.get(log.url) as resp:
            page = BeautifulSoup(await resp.text(), "lxml")
            try:
                img_src = page.find(attrs={"alt": log.title})['src']
            except TypeError:
                return -1
        
        return img_src


    def _get_modification_information(self) -> tuple[str, str, str]:
        """ Returns last stored Etag and Last Modified GET header values and XML Last Build date"""
        with open(os.getenv("NOTIFIER_HOME") + "/resources/" + self.name, "a+") as f:
            if(not f.tell()):
                # no previous record
                f.write("***\n***\nThu, 1 Jan 1970 00:00:00")
            f.seek(0)
            return "".join(f.readlines()).split("\n")
    

    def _update_modification_information(self, etag: str, last_modified: str, last_build_date: str):
        with open(os.getenv("NOTIFIER_HOME") + "/resources/" + self.name, "w+") as f:
            f.write(f"{etag}\n{last_modified}\n{last_build_date}")

    
    async def _make_conditional_get_request(self, etag, last_modified) -> aiohttp.ClientResponse:
        return await self._session.get(self._feed_url, headers={"If-None-Match": etag,
                                                       "If-Modified-Since": last_modified})
    
   
    async def _parse_feed(self, feed_content: str) -> list[Log]:
        return await self._parser.parse(feed_content)

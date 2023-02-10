# Author: vugz @ GitHub
# Python 3.10.6

from log import Log

from abc import abstractmethod, ABC

from bs4 import BeautifulSoup
import re
import bleach

class Parser(ABC):
    """ Interface of a Parser """
    @abstractmethod
    async def parse(self, xml_feed) -> list[Log]:
        """ Parse and XML file and return a list with all Logs found. """
        ...

###
# Other parsers can be implemented here
# Parsers are the only thing necessary to be implemented to get this compatible with new feeds ( if already available parsers don't work )
###
class CMParser(Parser):
    """ Example parser of a terrible RSS feed """
    async def parse(self, feed):
        soup = BeautifulSoup(feed, "xml")

        entries = []
        for item in soup.find_all("item"):
            for url in item.find("link"):
                # remove GET params
                url = re.sub("\/\?.*", "", url)
                title = str(item.find("title").string)
                # parse descrption
                desc = item.find("description")
                desc = BeautifulSoup(desc.text, "lxml")
                desc = desc.find("p").text
                # parse date
                date = str(item.find("pubDate").string)[:-9]
                # parse author
                author = str(item.find("creator").string)
                entries.append(Log(title, url, desc, date, author))

        return entries

class AlbionParser(Parser):
    """ Example parser of a beautifully maintained and taken care of RSS feed! """
    async def parse(self, feed):
        soup = BeautifulSoup(feed, "xml")

        entries = []
        # everything is straighforward, except for the image lookup
        for item in soup.find_all("item"):
            url = str(item.find("link").string)
            title = str(item.find("title").string)
            desc = str(item.find("description").string)
            # strip all bold and anchor tags
            desc = bleach.clean(desc, tags=[], strip=True)
            # usually the posts have an image on the first line 
            tmp = desc.split("\n")[0]
            if ".jpeg" in tmp or ".png" in tmp or ".jpg" in tmp:
                img = "https://assets.albiononline.com/uploads/media/default/media/" + tmp 
                # remove image from desc
                desc = "\n".join(desc.split("\n")[2:])
            else:
                img = ""
            date = str(item.find("pubDate").string)[:-9]
            author = str(item.find("dc:creator").string)

            entries.append(Log(title, url, desc, date, author, img))
        
        return entries
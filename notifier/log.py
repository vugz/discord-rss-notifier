from dataclasses import dataclass

@dataclass
class Log:
    """ A Log that we wish to notify subscribers with """
    title:  str
    url:   str
    desc:   str
    date:   str
    author: str
    image:  str=""

    def to_payload(self, webhook_name: str) -> dict:
        """ 
        Return a JSON compatible Python object that can be
        passed onto an aiohttp request
        """
        return {
            "username": webhook_name,
            "content": "",
            "embeds": [{
                "title": f":newspaper: {self.title}",
                "author": {
                    "name": self.author,
                },
                "color": 1677215,
                "url": self.url,
                "description": self.desc,
                "image": {
                    "url": self.image 
                },
                "footer": {
                    "text": self.date
                }
            }]
        }


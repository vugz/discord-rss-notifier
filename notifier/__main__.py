# Author: vugz @ GitHub
# Python 3.10.6

from dotenv import load_dotenv
import asyncio
import os

# Please hardcode the absolute path to the root dir of your project here e.g "/home/user/repos/notifier"
NOTIFIER_DIR = ""

if not os.path.exists(NOTIFIER_DIR):
    print("Please provide a valid directory path for the root directory of the project in __main__.py")
    os.sys.exit(1)

# discard trailling "/"
NOTIFIER_DIR = NOTIFIER_DIR[:-1] if NOTIFIER_DIR[-1] == "/" else NOTIFIER_DIR 

os.environ['NOTIFIER_HOME'] = NOTIFIER_DIR

# Your env variables should be located on $NOTIFIER_DIR/.env, e.g "~/repos/notifier/.env"
load_dotenv(NOTIFIER_DIR + "/.env")

# Run all the Subscriber instances here
async def entry():
    # Example for the parsers defined in parse.py
    ...
    # cm = subscriber.Subscriber("cm", os.getenv("CM_WEBHOOK"), os.getenv("CM_FEED"), parse.CMParser())
    # albion = subscriber.Subscriber("albion", os.getenv("ALBION_WEBHOOK"), os.getenv("ALBION_FEED"), parse.AlbionParser())
    # res = await asyncio.gather(cm.update(), albion.update(), return_exceptions=True)

    ## check and log results here if necessary
    # for r in res:
    #   do stuff

if __name__ == '__main__':
    import parse
    import subscriber

    asyncio.run(entry())

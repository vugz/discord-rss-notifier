![Python](https://img.shields.io/badge/python-3.10-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# Discord RSS Notifier

This is a simple program I wrote to get notifications for RSS feeds updates on Discord.
It was tested in Python 3.10 and also requires sqlite3 installed on the machine.

## Configuration 
To get it ready just run `./setup.sh` on the root directory of the repository.
After that just place your webhook and feed urls in the `.env` file and set the path of the root directory of the project on `__main__.py`.

To have your own RSS feeds you will simply need to place your Subscriber instances with a Parser for their respective RSS feeds in the `entry` function on `__main__.py`, two examples are already provided, one of them is for the MMO Sandbox Albion Online (see https://forum.albiononline.com/index.php/Thread/31615-RSS-Feed/)

## Usage 
Ideally the script should be run every hour or minute, depending on the activity of the resources you're trying to get notified on.
An example of configuration is to have this on a server running every minute with **Vixie Cron** by setting the following in your crontab: 

``` * * * * * /home/user/notifier/venv/bin/python3 /home/user/notifier/notifier```

This prompts the Python interperter in the virtual environment to run the module every minute, checking for updates on the RSS feeds and posting to the Discord webhooks.

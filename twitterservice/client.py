import pycurl
import urllib
import json


FIREHOSE_URL = "https://userstream.twitter.com/2/%s.json"


def attach_nozzle(api_fun, callback, args):
    nozzle_url = FIREHOSE_URL % api_fun

    conn = pycurl.Curl()
    conn.setopt(pycurl.URL, nozzle_url)
    conn.setopt(pycurl.WRITEFUNCTION, callback)

    data = urllib.urlencode(args)
    conn.setopt(pycurl.POSTFIELDS, data)

    conn.perform()


def hose(data):
    print data
    # write stuff to database or something...


if __name__ == "__main__":

    # This varies for each nozzle
    args = {
	'follow': '68668957',
	'oauth_token': '66869384-zgMGFtRyigYqUF0ffY0F8S4WM1fOX9LMgPlAV9Xfj',
	'oauth_token_secret':'nZoduKEnksGcs6nxFAjJjGhEP7kllP4BKM5b6r2qk'
    }

    attach_nozzle('user', hose, args)

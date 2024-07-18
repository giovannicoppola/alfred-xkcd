#!/usr/bin/env python3


import json
import os
from config import CACHE_FOLDER_IMAGES
import urllib.request
import sys

def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


myTitle=os.path.expanduser(os.getenv('comicTitle', ''))
myURL=os.path.expanduser(os.getenv('imageURL', ''))
comicN=os.path.expanduser(os.getenv('comicN', ''))
comicAlt=os.path.expanduser(os.getenv('comicAlt', ''))
comicDate=os.path.expanduser(os.getenv('comicDate', ''))


ICON_PATH = f"{CACHE_FOLDER_IMAGES}{comicN}.png"
if not os.path.exists(ICON_PATH):
  log ("retrieving image" + ICON_PATH)
  try:
    urllib.request.urlretrieve(myURL, ICON_PATH)
  except urllib.error.URLError as e:
    log("Error retrieving image:", e.reason)  # Log the specific error reason



myJSON = {
  "variables": {
    "fruitxx": ICON_PATH,
    "comicNum": comicN
  },
  #"rerun": 0.5,
  "response": f"# {myTitle} \n![]({ICON_PATH}) \n{comicAlt}",
  "footer": f"{comicDate}",
  "behaviour": {
    "response": "append",
    "scroll": "end",
    "inputfield": "select"
  }
}


print (json.dumps(myJSON)) 
#!/usr/bin/env python3


import json
import os
from config import log, fetchComicsPath, toggle_read


import sys

from time import time

if sys.argv[1]:
  MYNUM = sys.argv[1]


main_start_time = time()








myTitle=os.path.expanduser(os.getenv('comicTitle', ''))
myURL=os.path.expanduser(os.getenv('imageURL', ''))
comicN=os.path.expanduser(os.getenv('comicN', ''))
comicAlt=os.path.expanduser(os.getenv('comicAlt', ''))
comicDate=os.path.expanduser(os.getenv('comicDate', ''))
imagePath=os.path.expanduser(os.getenv('imagePath', ''))

fetchComicsPath(MYNUM,myURL)
toggle_read(MYNUM)

myJSON = {
  "variables": {
    "comicPath": imagePath,
    "comicNum": comicN
  },
  #"rerun": 0.5,
  "response": f"# {myTitle} \n![]({imagePath}) \n{comicAlt}",

  "footer": f"#{comicN} {comicDate}",
  "behaviour": {
    "response": "append",
    "scroll": "end",
    "inputfield": "select"
  }
}


print (json.dumps(myJSON)) 



main_timeElapsed = time() - main_start_time
log(f"\nscript duration (create textView): {round (main_timeElapsed,3)} seconds")


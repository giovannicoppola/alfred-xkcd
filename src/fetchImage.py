#!/usr/bin/env python3


from config import log, fetchComicsPath
import sys
import os
from time import time


MYNUM = sys.argv[1]
myURL=os.path.expanduser(os.getenv('imageURL', ''))




main_start_time = time()
COMICS_PATH = fetchComicsPath(MYNUM,myURL)

main_timeElapsed = time() - main_start_time
log(f"\nscript duration (fetchImage): {round (main_timeElapsed,3)} seconds")
print (COMICS_PATH, end='')




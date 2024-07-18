import sys
import os

CACHE_FOLDER = os.getenv('alfred_workflow_cache')
CACHE_FOLDER_IMAGES = CACHE_FOLDER+"/images/"

if not os.path.exists(CACHE_FOLDER):
    os.makedirs(CACHE_FOLDER)
if not os.path.exists(CACHE_FOLDER_IMAGES):
    os.makedirs(CACHE_FOLDER_IMAGES)



def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)



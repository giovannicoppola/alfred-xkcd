from config import log, COMICSMAX, checkUpdate

import json
log ("checking for updates")
checkUpdate(COMICSMAX)
log ("done 👍")
	

result= {"items": [{
    "title": "Done!" ,
    "subtitle": "ready to search xkcd now",
    "arg": "",
    "icon": {

            "path": "icons/done.png"
        }
    }]}
print (json.dumps(result))


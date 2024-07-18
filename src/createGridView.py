#!/usr/bin/env python3


import json
import os



myJSON = {
    "cache": {
        "seconds": 21600,
        "loosereload": True
    },
    "items": [
        {
            "title": "Eyes and Horns",
            "subtitle": "Experimental \ud800\udd01 6 minutes \ud800\udd01 Chaerin Im",
            "icon": {
                "path": "~/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/com.vitorgalvao.alfred.shortfilms/images/Eyes-and-horns-Chaerin-Im-01.jpg"
            },
            "mods": {
                "alt": {
                    "subtitle": "Inspired by Picasso\u2019s \u2018Vollard Suite\u2019, the transformation of the over masculine Minotaur leads to the destruction of boundaries of sexes."
                }
            },
            "quicklookurl": "https://www.shortoftheweek.com/2024/07/17/eyes-and-horns/",
            "match": "Eyes and Horns Experimental",
            "arg": "https://player.vimeo.com/video/985689913"
        },
        {
            "title": "Nanitic",
            "subtitle": "Drama \ud800\udd01 14 minutes \ud800\udd01 Carol Nguyen",
            "icon": {
                "path": "~/Library/Caches/com.runningwithcrayons.Alfred/Workflow Data/com.vitorgalvao.alfred.shortfilms/images/Nanitic-Carol-Nguyen-03.jpg"
            },
            "mods": {
                "alt": {
                    "subtitle": "9 year-old Trang starts to shift out of oblivion as her aunt Ut tends to Grandma, who lies in her deathbed in the living room. How can a single body occupy so much space? What will happen when Grandma is gone?"
                }
            },
            "quicklookurl": "https://www.shortoftheweek.com/2024/07/16/nanitic/",
            "match": "Nanitic Drama",
            "arg": "https://player.vimeo.com/video/981226911"
        }
    ]
}


# myJSON = {
#   "variables": {
#     "fruitxx": "banana",
#     "vegetable": "carrot"
#   },
#   #"rerun": 0.5,
#   "response": f"{MYSTRING['myText']}\n Fruits are the seed-bearing structures in flowering plants.",
#   "footer": f"{MYSTRING['myValue']}, Anatomy of fruits and vegetables",
#   "behaviour": {
#     "response": "append",
#     "scroll": "end",
#     "inputfield": "select"
#   }
# }


print (json.dumps(myJSON)) 
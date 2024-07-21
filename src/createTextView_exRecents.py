#!/usr/bin/env python3


import json
import os
from config import log,  MY_DATABASE
import sqlite3

import re
import sys

from time import time
MYPATH = sys.argv[1]
main_start_time = time()


def extract_number(file_path):
		# Regular expression to find the number before ".png"
		match = re.search(r'/(\d+)\.png$', file_path)
		if match:
				return match.group(1)
		else:
				return None





def fetchOne(myNum):
		
	db = sqlite3.connect(MY_DATABASE)
	db.row_factory = sqlite3.Row
	cursor = db.cursor()
	
	query = f"SELECT * FROM xkcd WHERE NUM = {myNum}"
	cursor.execute(query)
	r = cursor.fetchone()
	
	
	comicDate = f"{r['year']}-{r['month']}-{r['day']}"

	myJSON = {
	"variables": {
		"comicPath": MYPATH
	
	},
	#"rerun": 0.5,
	"response": f"# {r['title']} \n![]({MYPATH}) \n{r['alt']}",

	"footer": f"{comicDate}",
	"behaviour": {
		"response": "append",
		"scroll": "end",
		"inputfield": "select"
	}
}
	print (json.dumps(myJSON)) 




def main():
	# Extract the number
	number = extract_number(MYPATH)
	log(f"number: {number}")
	fetchOne(number)
	
	main_timeElapsed = time() - main_start_time
	log(f"\nscript duration (textView recent): {round (main_timeElapsed,3)} seconds")

if __name__ == "__main__":
		main()
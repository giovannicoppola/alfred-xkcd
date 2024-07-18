# Sunny ☀️   🌡️+79°F (feels +82°F, 65%) 🌬️↘6mph 🌔&m Wed Jul 17 06:21:21 2024
# W29Q3 – 199 ➡️ 166 – 67 ❇️ 297


"""
A script to build an xkcd database by using the json interface
current count as of today: 2,958
"""

import requests
from time import time, sleep
import sqlite3
import json
import sys




def create_XKCD_DB(myData):
	conn = sqlite3.connect('xkcd.sqlite')
	c = conn.cursor()
	
	sql_drop = "DROP TABLE IF EXISTS xkcd"
	sql_create = """CREATE TABLE xkcd (
		ID INTEGER PRIMARY KEY AUTOINCREMENT,        
		 
		month INT,
		num INT,
		link TEXT,
		
		year INTEGER,
		news TEXT,
		safe_title TEXT,

		transcript TEXT,
		alt TEXT,
		img TEXT,
		
		title TEXT,
		day INT
		
		)
		"""
	
	c.execute(sql_drop)
	c.execute(sql_create)
	
	for myComic in myData:
		
		c.execute('INSERT INTO xkcd (month, num, link, year, news, safe_title, transcript, alt, img, title, day) VALUES (?,?,?,   ?,?,?,   ?,?,?, ?,?)', 
			(myComic['month'], 
			myComic['num'],
			myComic['link'],
			
			myComic['year'],
			myComic['news'],
			myComic['safe_title'],

			myComic['transcript'],
			myComic['alt'],
			myComic['img'],
	
			myComic['title'],
			myComic['day']
		))
	

	
	conn.commit()
	conn.close()

def insert_xkcd_data():
	conn = sqlite3.connect('xkcd.sqlite')
	c = conn.cursor()
	for xkcd in xkcd_list:
		c.execute('''INSERT INTO XKCD (TITLE, IMG, ALT, LINK)
					 VALUES (?, ?, ?, ?)''', (xkcd['title'], xkcd['img'], xkcd['alt'], xkcd['link']))
	conn.commit()
	conn.close()
    


def getJSONdata(start, end):
        

    currentURL = 'https://xkcd.com/info.0.json'
    baseURL = f"https://xkcd.com/xxxx/info.0.json"

    toDo = start-end 
    xkcd_list = []
    myCounter = 0
    failedURLs = []
    for i in range(start, end, -1):
        # Wait 
        sleep(0.2)
        url = f"https://xkcd.com/{i}/info.0.json"
        myCounter += 1
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            xkcd_list.append(json_data)
            print(f"Retrieved data for {json_data['title']}: {myCounter}/{toDo} ({myCounter/toDo*100:.0f}%)")

        else:
            print(f"Failed to retrieve data: {response.status_code}")
            failedURLs.append(url)

    # save the list to a json file
    with open('xkcd.json', 'w') as f:
        f.write(json.dumps(xkcd_list, indent=2))
    
    #write the failed URLs to a file
    with open('failedURLs.txt', 'w') as f:
        for url in failedURLs:
            f.write(url + '\n')


	


# readJSONdata
def readJSONdata():
	with open('xkcd.json', 'r') as f:
		xkcd_list = json.load(f)
	return xkcd_list

      


def main():
	main_start_time = time()
	# getJSONdata (2958,0)
	myData = readJSONdata()
	
	create_XKCD_DB(myData)
	main_timeElapsed = time() - main_start_time
	print (f"\nscript duration: {round (main_timeElapsed,3)} seconds")




if __name__ == "__main__":
    main()



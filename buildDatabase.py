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


def create_XKCD_DB():
    conn = sqlite3.connect('xkcd.sqlite')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS XKCD
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 TITLE TEXT,
                 IMG TEXT,
                 ALT TEXT,
                 LINK TEXT)''')
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

def refreshReadwise_Reader_Database (rebuildDays=0):
	# Record the start time
	start_time = datetime.datetime.now()
	
	
	full_data = []
	next_page_cursor = None
	updated_after=None
	location=None
	
	# Later, if you want to get new documents updated after some date, do this:
	updated_after = docs_after_date = datetime.datetime.now() - datetime.timedelta(days=10)  # use your own stored date
	

	while True:
		params = {}
		if next_page_cursor:
			params['pageCursor'] = next_page_cursor
		
		if updated_after:
			params['updatedAfter'] = docs_after_date.isoformat()
			log (f"using isoformat {docs_after_date.isoformat()}")
		if location:
			params['location'] = location
    
		log ("Making Reader API request with params " + str(params) + "...")
		
		try:
			response = requests.get(
				url="https://readwise.io/api/v3/list/",
				params=params,
				headers={"Authorization": f"Token {TOKEN}"}, verify=False
			)
			response.raise_for_status()  # Raise an error for HTTP status codes >= 400
			full_data.extend(response.json()['results'])
			next_page_cursor = response.json().get('nextPageCursor')
		except requests.exceptions.RequestException as e:
			log(f"Error: {e}")
		
		if not next_page_cursor:
			break
	
	db=sqlite3.connect(MY_READER_DATABASE)	
	sql_drop = "DROP TABLE IF EXISTS reader" 
	sql_create = """CREATE TABLE reader (
						
			reader_id TEXT,
			readwise_url TEXT,
			source_url TEXT,
			
			title TEXT,
			author TEXT,
			source TEXT,
			category TEXT,
			location TEXT,
			
			reader_tags TEXT,
			siteName TEXT,
			wordCount INT,	
			createdDate TEXT,	
			updatedDate TEXT,	

			notes TEXT,
			publishedDate TEXT,	
			summary TEXT,
			
			image_url TEXT,
			parent_id TEXT,
			readingProgress REAL
			)
			"""
	c = db.cursor()   
	c.execute(sql_drop)
	c.execute(sql_create)
		
			
	for myBook in full_data:
				
		c.execute('INSERT INTO reader VALUES (?,?,?,   ?,?,?,?,?,  ?,?,?,?,?,  ?,?,?, ?,?,?)', 
			(myBook['id'], 
			myBook['url'],
			myBook['source_url'],
			
			myBook['title'],
			myBook['author'],
			myBook['source'],
			myBook['category'],
			myBook['location'],


			str(myBook['tags']),
			myBook['site_name'],
			myBook['word_count'],
			myBook['created_at'],
			myBook['updated_at'],


			myBook['notes'],
			myBook['published_date'],
			myBook['summary'],
			
			myBook['image_url'],
			myBook['parent_id'],
			myBook['reading_progress'],
			
		
		))

		
		# quickLookPath = f"{IMAGE_H_FOLDER}{myHigh['id']}.jpg"
		# if not os.path.exists(quickLookPath):
		# 	createImage(myHigh['text'],myBook['author'],myBook['title'],myHigh['id'])

	
	
	db.commit()
	# Record the end time
	end_time = datetime.datetime.now()

	# Calculate the time difference
	elapsed_time = end_time - start_time
	log (f"elapsed time: {elapsed_time}")
	"""
	#retrieving all the images
	select_statement = "SELECT user_book_id, cover_image_url FROM highlights"
	
	c.execute(select_statement)

	rs = c.fetchall()
	
	for rec in rs:
		if rec[1]:
			ICON_PATH = f'{IMAGE_FOLDER}{rec[0]}.jpg'
			if not os.path.exists(ICON_PATH):
				log ("retrieving image" + ICON_PATH)
				try:
					urllib.request.urlretrieve(rec[1], ICON_PATH)
				except urllib.error.URLError as e:
				    # If an exception occurs, print an error message and delete the file if it exists
					log(f"Failed to download file: {e.reason}")
					ICON_PATH = f'{IMAGE_FOLDER}{rec[0]}.jpg'
					src = 'icons/supplementals.png'
					shutil.copy(src, ICON_PATH)

		else:
			ICON_PATH = f'{IMAGE_FOLDER}{rec[0]}.jpg'
			src = 'icons/supplementals.png'
			shutil.copy(src, ICON_PATH)

	"""
	
	db.close()


def main():
      main_start_time = time()
      getJSONdata (2958,0)
      main_timeElapsed = time() - main_start_time
      print (f"\nscript duration: {round (main_timeElapsed,3)} seconds")




if __name__ == "__main__":
    main()



#!/usr/bin/env python3

import sqlite3
from config import MY_DATABASE, log, CACHE_FOLDER_FAVS, fetchComicsPath
import sys
import os

num = sys.argv[1]




def toggle_is_favorite(db_path, num_value):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    

    # Retrieve the current value of is_favorite
    cursor.execute("SELECT is_favorite, img, num FROM xkcd WHERE num = ?", (num_value,))
    current_value = cursor.fetchone()
    
    
    # Check if the record was found
    if current_value is None:
        log(f"No record found with num = {num_value}")
        return
    
    if current_value[0] == 1:
        os.remove(f"{CACHE_FOLDER_FAVS}{current_value[2]}.png")
        exitMessage = "Removed from favorites 🫤"  
    else:
        fetchComicsPath(current_value[2],current_value[1],'favs')
        
        exitMessage = "Added to favorites ⭐️"
    
        

    # Toggle the value of is_favorite
    new_value = not bool(current_value[0])

    # Update the value in the database
    cursor.execute("UPDATE xkcd SET is_favorite = ? WHERE num = ?", (new_value, num_value))
    conn.commit()

    # Close the connection
    conn.close()

    log(f"Toggled is_favorite to {new_value} for record with num = {num_value}")
    return exitMessage


# Call the function to toggle is_favorite
exitMessage = toggle_is_favorite(MY_DATABASE, num)
print (exitMessage)

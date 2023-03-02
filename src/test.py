import sqlite3
import pandas as pd

# fetch the links from the database and save them in pandas dataframe
conn = sqlite3.connect('data/podcast.db')
c = conn.cursor()
c.execute("SELECT * FROM PODCAST_DETAILS")
links = c.fetchall()
conn.close()

df = pd.DataFrame(links, columns=['id', 'title', 'description', 'transcript', 'link'])
print(df['title'])

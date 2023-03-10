import sqlite3

# create a local database
conn = sqlite3.connect("data/podcast.db")
c = conn.cursor()

# tables
c.execute(
    """CREATE TABLE PODCAST_LINKS
                (id integer primary key, link text)"""
)

c.execute(
    """CREATE TABLE PODCAST_DETAILS
                (id integer primary key, title text, description text, transcript text, link text)"""
)

conn.commit()
conn.close()

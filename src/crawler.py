import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import tqdm


def get_links(url):
    """scraps the links for each episode from a Analytics Power Hour page

    Args:
        url (string): url of the page

    Returns:
        list: list of links
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", class_="cl-element-title__anchor")
    return links


def get_info(url):
    """scraps the title, description and transcript of a podcast episode

    Args:
        url (string): url of the podcast page

    Returns:
        list: list of title, description and transcript
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # title
    title = soup.find(
        "h1",
        class_="el-5057316460e77b3c5e9fe ss-element gusta-post-title show-show ani-fade",
    ).text

    # description
    des_divs = soup.find_all("div", class_="wpb_text_column wpb_content_element")
    try:
        description = des_divs[3].find("p").text
    except:
        description = des_divs[4].find("p").text

    # transcript
    transcript_p = soup.find("div", class_="vc_toggle_content").find_all("p")
    transcript = list()
    for p in transcript_p:
        # keep only p tags that starts like that [ or with a number
        if (
            p.text.startswith("[")
            or p.text.startswith("0")
            or p.text.startswith("1")
            or p.text.startswith("2")
        ):
            transcript.append(p.text)
    flat_list = [item for sublist in transcript for item in sublist]
    transcript = "".join(flat_list)
    return title, description, transcript


def get_all_links():
    """gets all the links from all the pages and saves them in the database"""
    links = []
    for i in range(1, 12):
        if i == 1:
            url = "https://analyticshour.io/all-podcast-episodes/"
        else:
            url = "https://analyticshour.io/all-podcast-episodes/?sf_paged=" + str(i)
        time.sleep(2)
        links += get_links(url)

    # if the link has "bonus" in it, it is a bonus episode and we don't want it
    links = [link for link in links if "bonus" not in link["href"]]
    # add the links to the database to the PODCAST_LINKS table, where the id is the index of the link in the list
    conn = sqlite3.connect("data/podcast.db")
    c = conn.cursor()
    for i, link in enumerate(links):
        c.execute("INSERT INTO PODCAST_LINKS VALUES (?, ?)", (i, link["href"]))
    conn.commit()
    conn.close()


def get_all_info():
    """gets all the info from all the links and saves them in the database"""
    # get all the links from the database
    conn = sqlite3.connect("data/podcast.db")
    c = conn.cursor()
    c.execute("SELECT * FROM PODCAST_LINKS")
    links = c.fetchall()
    conn.close()

    # get all the info from the links
    for link in tqdm.tqdm(links):
        try:
            print(link)
            title, description, transcript = get_info(link[1])
            time.sleep(2)
            conn = sqlite3.connect("data/podcast.db")
            c = conn.cursor()
            c.execute(
                "INSERT INTO PODCAST_DETAILS VALUES (?, ?, ?, ?, ?)",
                (link[0], title, description, transcript, link[1]),
            )
            conn.commit()
            conn.close()
        except:
            print("The URL has another structure")


def main():
    get_all_links()
    time.sleep(30)
    get_all_info()


if __name__ == "__main__":
    main()

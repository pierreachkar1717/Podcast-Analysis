import sqlite3
import pandas as pd
import re
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# fetch the data from the database
conn = sqlite3.connect("data/podcast.db")
c = conn.cursor()
c.execute("SELECT * FROM PODCAST_DETAILS")
data = c.fetchall()
conn.close()

df = pd.DataFrame(data, columns=["id", "title", "description", "transcript", "link"])
stop_words = set(stopwords.words("english"))


def preprocess_transcript(text):
    """Preprocess the text by first converting to lowercase and then removing timestamps, [music] and stop words as well as tokenizing the text into sentences.

    Args:
        text (str): The text to preprocess

    Returns:
        str: The preprocessed text

    """
    # Convert the text to lowercase
    text = text.lower()

    # Remove timestamps
    text = re.sub(r"\b(\d{1,2}:)?\d{1,2}:\d{2}\.\d\b", "", text)
    text = re.sub(r"\b(\d{1,2}:)?\d{1,2}:\d{2}\b", "", text)
    text = re.sub(r"\b\d{1,2}:\d{2}:\d{2}\b", "", text)

    # Remove [music]
    text = re.sub(r"\[music\]", "", text)

    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Remove stop words from the sentences
    filtered_sentences = []
    for sentence in sentences:
        words = sentence.split()
        filtered_words = [word for word in words if word not in stop_words]
        filtered_sentence = " ".join(filtered_words)
        filtered_sentences.append(filtered_sentence)

    return filtered_sentences


def divide_transcript(transcript):
    """Divide the transcript into chuncks, where each chunck has 500 tokens.

    Args:
        transcript (list): The transcript to divide into chuncks

    Returns:
        list: A list of chuncks, where each chunck is a list of sentences
    """
    chuncks = []
    chunck = []
    chunck_length = 0
    for sentence in transcript:
        sentence_length = len(sentence.split())
        if chunck_length + sentence_length <= 500:
            chunck.append(sentence)
            chunck_length += sentence_length
        else:
            chuncks.append(chunck)
            chunck = [sentence]
            chunck_length = sentence_length
    chuncks.append(chunck)

    # Remove empty chuncks
    chuncks = [chunck for chunck in chuncks if chunck != []]

    # concatenate the content of each chunck into a single string
    chuncks = [" ".join(chunck) for chunck in chuncks]

    return chuncks


# Apply the preprocessing and dividing function to the transcript column
df["filtered_transcript"] = df["transcript"].apply(preprocess_transcript)
df["transcript_chuncks"] = df["filtered_transcript"].apply(divide_transcript)

print(df["transcript_chuncks"][0][0])

# save the dataframe to a pickle file
#df.to_pickle('data/podcast_preprocessed.pkl')

import sqlite3
import pandas as pd
import re
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# fetch the data from the database 
conn = sqlite3.connect('data/podcast.db')
c = conn.cursor()
c.execute("SELECT * FROM PODCAST_DETAILS")
data = c.fetchall()
conn.close()

df = pd.DataFrame(data, columns=['id', 'title', 'description', 'transcript', 'link'])
stop_words = set(stopwords.words('english'))

def preprocess_transcript(text):
    """ Preprocess the text by first converting to lowercase and then removing timestamps, [music] and stop words as well as tokenizing the text into sentences.

    Args:
        text (str): The text to preprocess
    
    Returns:
        str: The preprocessed text
    
    """
    # Convert the text to lowercase
    text = text.lower()

    # Remove timestamps
    text = re.sub(r'\b(\d{1,2}:)?\d{1,2}:\d{2}\.\d\b', '', text)
    text = re.sub(r'\b(\d{1,2}:)?\d{1,2}:\d{2}\b', '', text)
    text = re.sub(r'\b\d{1,2}:\d{2}:\d{2}\b', '', text)

    # Remove [music]
    text = re.sub(r'\[music\]', '', text)
    
    
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)
    
    # Remove stop words from the sentences
    filtered_sentences = []
    for sentence in sentences:
        words = sentence.split()
        filtered_words = [word for word in words if word not in stop_words]
        filtered_sentence = ' '.join(filtered_words)
        filtered_sentences.append(filtered_sentence)
    
    # Join the filtered sentences back into a single string
    filtered_text = ' '.join(filtered_sentences)
    
    return filtered_text

def divide_transcript(text):
    """ Divide the transcript into parts of max 4000 tokens
    
    Args:
        transcript (str): The transcript to divide
    
    Returns:
        list: A list containing the divided parts of the transcript
    """
    # Tokenize the transcript into words
    words = text.split()
    
    # Divide the transcript into parts of max 4000 tokens
    parts = []
    part = ''
    for word in words:
        if len(part) + len(word) < 4000:
            part += word + ' '
        else:
            parts.append(part)
            part = word + ' '
    parts.append(part)
    
    return parts


# Apply the preprocessing and dividing function to the transcript column
df['filtered_transcript'] = df['transcript'].apply(preprocess_transcript)
df['transcript_parts'] = df['filtered_transcript'].apply(divide_transcript)

# save the dataframe to a pickle file
df.to_pickle('data/podcast_preprocessed.pkl')
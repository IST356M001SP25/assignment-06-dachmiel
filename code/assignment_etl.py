import streamlit as st
import pandas as pd
import requests
import json 
if __name__ == "__main__":
    import sys
    sys.path.append('code')
    from apicalls import get_google_place_details, get_azure_sentiment, get_azure_named_entity_recognition
else:
    from code.apicalls import get_google_place_details, get_azure_sentiment, get_azure_named_entity_recognition

PLACE_IDS_SOURCE_FILE = "code/solutions/cache/place_ids.csv"
CACHE_REVIEWS_FILE = "code/solutions/cache/reviews.csv"
CACHE_SENTIMENT_FILE = "code/solutions/cache/reviews_sentiment_by_sentence.csv"
CACHE_ENTITIES_FILE = "code/solutions/cache/reviews_sentiment_by_sentence_with_entities.csv"


def reviews_step(place_ids: str|pd.DataFrame) -> pd.DataFrame:
    '''
      1. place_ids --> reviews_step --> reviews: place_id, name (of place), author_name, rating, text 
    '''
    # if string, then its a filename so load into dataframe
    if isinstance(place_ids, str):
        place_ids_df = pd.read_csv(place_ids)
    else:
        place_ids_df = place_ids

    # get google place details for each place_id
    google_places = []
    for index, row in place_ids_df.iterrows():
        place = get_google_place_details(row['Google Place ID'])
        google_places.append(place['result'])

    # construct dataframe at the reviews level, include place_id, name from parent level
    reviews_df = pd.json_normalize(google_places, record_path="reviews", meta=["place_id", 'name'])

    # pair down to the columns we want
    reviews_df = reviews_df[['place_id', 'name',  'author_name', 'rating', 'text']]

    # save to cache, return dataframe
    reviews_df.to_csv(CACHE_REVIEWS_FILE, index=False, header=True)
    return reviews_df

def sentiment_step(reviews: str|pd.DataFrame) -> pd.DataFrame:
    '''
      2. reviews --> sentiment_step --> review_sentiment_by_sentence
    '''
    if isinstance(reviews, str):
        reviews_df = pd.read_csv(reviews)
    else:
        reviews_df = reviews
    # get sentiment for each review
    sentiment_df = []
    for index, row in reviews_df.iterrows():
        # get sentiment for each sentence
        sentences = row['text'].split('.')
        for sentence in sentences:
            if len(sentence) > 0:
                sentiment = get_azure_sentiment(sentence)
                sentiment_df.append({
                    'place_id': row['place_id'],
                    'name': row['name'],
                    'author_name': row['author_name'],
                    'rating': row['rating'],
                    'sentence_text': sentence,
                    'sentence_sentiment': sentiment['results']['documents'][0]['sentiment'],
                    'confidenceScores.positive': sentiment['results']['documents'][0]['confidenceScores']['positive'],
                    'confidenceScores.neutral': sentiment['results']['documents'][0]['confidenceScores']['neutral'],
                    'confidenceScores.negative': sentiment['results']['documents'][0]['confidenceScores']['negative']
                })
    # convert to dataframe
    sentiment_df = pd.DataFrame(sentiment_df)
    # save to cache, return dataframe
    sentiment_df.to_csv(CACHE_SENTIMENT_FILE, index=False, header=True)
    return sentiment_df

def entity_extraction_step(sentiment: str|pd.DataFrame) -> pd.DataFrame:
    '''
      3. review_sentiment_by_sentence --> entity_extraction_step --> review_sentiment_entities_by_sentence
    '''
    if isinstance(sentiment, str):
        sentiment_df = pd.read_csv(sentiment)
    else:
        sentiment_df = sentiment
    # get entities for each sentence
    entity_df = []
    for index, row in sentiment_df.iterrows():
        # get entities for each sentence
        entities = get_azure_named_entity_recognition(row['sentence_text'])
        for entity in entities['results']['documents'][0]['entities']:
            entity_df.append({
                'place_id': row['place_id'],
                'name': row['name'],
                'author_name': row['author_name'],
                'rating': row['rating'],
                'sentence_text': row['sentence_text'],
                'sentence_sentiment': row['sentence_sentiment'],
                'confidenceScores.positive': row['confidenceScores.positive'],
                'confidenceScores.neutral': row['confidenceScores.neutral'],
                'confidenceScores.negative': row['confidenceScores.negative'],
                'entity_text': entity['text'],
                'entity_category': entity['category'],
                'entity_subcategory': entity['subcategory'],
                'confidenceScores.entity': entity['confidenceScore']
            })
    # convert to dataframe
    entity_df = pd.DataFrame(entity_df)
    # save to cache, return dataframe
    entity_df.to_csv(CACHE_ENTITIES_FILE, index=False, header=True)
    return entity_df

if __name__ == '__main__':
    # helpful for debugging as you can view your dataframes and json outputs
    import streamlit as st 
    st.write("What do you want to debug?")
    reviews_step(PLACE_IDS_SOURCE_FILE)
    sentiment_step(CACHE_REVIEWS_FILE)
    entities_df = entity_extraction_step(CACHE_SENTIMENT_FILE)
    st.write(entities_df)
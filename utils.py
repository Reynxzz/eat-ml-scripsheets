import pandas as pd
import requests
from sklearn.feature_extraction.text import CountVectorizer

base_url = "https://3k3l6hn8-5000.asse.devtunnels.ms"
CAT_SCRAPED_OUTPUT_DIR = 'data/all_scraped_category.csv'
DETAIL_SCRAPED_OUTPUT_DIR = 'data/all_scraped_category.csv'
GET_DATABASE_URL = f'{base_url}/api/scraper'
SEND_PRODUCT_URL = f'{base_url}/api/scraper/product'
SCRAPER_SETTING_URL = f'{base_url}/api/scraper/setting'
SEND_KEYWORD_URL = f'{base_url}/api/scraper/keyword'

def load_data_from_csv(path):
  df = pd.read_csv(path)
  return df

def load_data_from_db(url, key, idx_range):
    full_df = pd.DataFrame()
    for idx in range(0, idx_range):
        json_data = {
            "key": f'{key}_{idx}'
        }
        response = requests.get(url, json=json_data)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            full_df = full_df.append(df, ignore_index=True)
        else:
            print(f"Failed to retrieve data for index {idx}")

    return full_df

def df_to_db(df, api_url):
    """
    Send a DataFrame to a database via an API call.

    Parameters:
    df (pd.DataFrame): The DataFrame to be sent.
    api_url (str): The API endpoint URL.
    """
    data_json = df.to_dict(orient='records')
    response = requests.post(api_url, json=data_json)
    
    # Check the response
    if response.status_code == 200:
        print("Data successfully stored!")
    else:
        print(f"Failed to store data. Status code: {response.status_code}, Response: {response.text}")

def classify_task(df, pipeline):
    df['label'] = pipeline.predict(df['title'])
    return df

def extract_keywords(df, text_column):
    """
    Extract keywords, their frequencies, and sum up 'sold' for items containing each keyword.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing the text data and metadata.
    text_column (str): The name of the column containing the text data.
    
    Returns:
    pd.DataFrame: A DataFrame containing keywords, their frequencies, summed 'sold', and label.
    """
    vectorizer = CountVectorizer()
    
    X = vectorizer.fit_transform(df[text_column])
    
    keyword_freq = X.toarray().sum(axis=0)
    
    keywords = vectorizer.get_feature_names_out()
    
    df_output = pd.DataFrame(columns=['keyword', 'frequency', 'sold', 'label'])
    
    for i, keyword in enumerate(keywords):
        mask = df[text_column].str.contains(keyword, case=False, na=False)
        
        total_sold = df.loc[mask, 'sold'].sum()
        
        label = df.loc[mask, 'label'].iloc[0] if not df.loc[mask].empty else None
        
        df_output = df_output.append({
            'keyword': keyword,
            'frequency': keyword_freq[i],
            'sold': total_sold,
            'label': label
        }, ignore_index=True)
    
    return df_output
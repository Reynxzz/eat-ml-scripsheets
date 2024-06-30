import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

# Load data
df = pd.read_csv('data/all_scraped_category_classified.csv')

df['timestamp'] = pd.date_range(start='1/1/2024', periods=(df.shape[0]))
df['label'] = np.random.randint(2, size=len(df))

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sidebar for date range and category selection
st.sidebar.header('Filter Options')
date_range = st.sidebar.date_input("Select date range", [])
category = st.sidebar.selectbox("Select category", ['umum', 'potensi ilegal'])

# Filter data based on selection
if date_range:
    start_date, end_date = date_range
    df = df[(df['timestamp'] >= pd.to_datetime(start_date)) & (df['timestamp'] <= pd.to_datetime(end_date))]

if category == 'umum':
    df = df[df['label'] == 0]
else:
    df = df[df['label'] == 1]

# Extract keywords using CountVectorizer
vectorizer = CountVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['title'])
keywords = vectorizer.get_feature_names_out()
keyword_counts = X.toarray().sum(axis=0)

keyword_df = pd.DataFrame({'keyword': keywords, 'count': keyword_counts})
top_keywords = keyword_df.sort_values(by='count', ascending=False).head(10)
# Split layout into three columns
col1, col2, col3 = st.columns(3)

with col1:
    # Display total product scraped
    total_products = df.shape[0]
    st.subheader('Total Products')
    st.header(f":blue[{total_products}]")

    # Display total keywords
    total_keywords = len(keywords)
    st.subheader('Total Keywords')
    st.header(f":blue[{total_keywords}]")

    # Table for top products containing top keywords
    df['truncated_title'] = df['title'].apply(lambda x: x if len(x) <= 30 else x[:47] + '...')

    # Table for top products containing top keywords
    st.subheader('Top Products')
    top_products = df[df['title'].apply(lambda x: any(keyword in x for keyword in top_keywords['keyword'].tolist()))][['truncated_title' , 'title', 'price', 'link']].head(5)

    # Add HTML links
    top_products['link'] = top_products['link'].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>')

    # Display DataFrame with clickable links, hiding the index
    st.write(top_products[['truncated_title', 'price', 'link']].to_html(index=False, escape=False), unsafe_allow_html=True)

with col2:
    pass

with col3:
    # Bar chart for top keywords
    st.header('Top Keywords')
    fig, ax = plt.subplots()
    top_keywords.plot(kind='bar', x='keyword', y='count', ax=ax)
    st.pyplot(fig)
import streamlit as st
import openai
import re
import pandas as pd
import requests
import json
from bs4 import BeautifulSoup

user_api_key = st.sidebar.text_input("OpenAI API key", type="password")
client = openai.OpenAI(api_key=user_api_key)
prompt = """Act as an AI reading learning-assistant in Korean. You will receive an article of Korean news including the title and the content.
            Your role is to read the article, and summarize it in 3 sentences in English and list ten interesting Korean vocabs together with their meaning in english, part of speech and using example.            
            Give the summary in string format, beginning with the topic 'summary'. All must be in [], for example: [Summary: This is the first sentence. This is the second sentence. This is the third sentence.]
            List the vocab in a JSON array, one vocab per line.
            Each vocab must have 4 fileds:
            - "vocab" - the Korean vocab
            - "meaning" - the meaning of the vocab in English
            - "part of speech" - the part of speech of the vocab
            - "example" - an example of the vocab used in a sentence. The example must not include '' or "".
            Don't say anything at first. Wait for the user to say something.
        """
st.title('Korean reading assistant')
st.markdown('Input the url of news from news.naver.com. \n\
            The AI will give you summary and interesting vocabs from the news.')

user_input = st.text_area("Enter news url from naver.com:", "Your url here")

if st.button('Submit'):
    news_info = requests.get(user_input)
    news_info = news_info.text
    soup = BeautifulSoup(news_info,'html.parser')
    article_content = soup.find('article', class_='go_trans _article_content')
    title = soup.title.string
    text_content = article_content.get_text(separator='\n') if article_content else None
    news_info = title + '\n' + text_content


    messages_so_far = [
        {"role": "system", "content": prompt},
        {'role': 'user', 'content': news_info},
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages_so_far
    )
    answer = response.choices[0].message.content
    find_summary = re.findall(r'\[(Summary:.*)\]',answer)
    summary = find_summary[0]
    st.write(summary)
    find_vocab = re.findall(r'{"vocab":.*}',answer)
    vocab = ','.join(find_vocab)
    vocab = '[' + vocab + ']'
    sd = json.loads(vocab)
    answer_df = pd.DataFrame.from_dict(sd)
    st.table(answer_df)
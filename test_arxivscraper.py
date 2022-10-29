import arxivscraper
import requests
import pickle
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

# label gold stardard metrics
# note how date, num-samples, dict, df, etc. was choosen
# alpha version: compare gold stardard metrics vs what reproscreener found

path = './case-studies/arxiv-corpus/mine5/'

Path(path).mkdir(parents=True, exist_ok=True)
Path(path + 'pdf/').mkdir(parents=True, exist_ok=True)
Path(path + 'html/').mkdir(parents=True, exist_ok=True)
Path(path + 'parsed_xml/').mkdir(parents=True, exist_ok=True)

scraper = arxivscraper.Scraper(category='cs',date_from='2022-10-24',date_until='2022-10-25',t=10, filters={'categories':['cs.lg']})
output = scraper.scrape()

cols = ('id', 'title', 'categories', 'abstract', 'doi', 'created', 'updated', 'authors')
df = pd.DataFrame(output, columns=cols)

df['url_pdf'] = 'https://arxiv.org/pdf/' + df['id'] + '.pdf'
df['url_html'] = 'https://arxiv.org/abs/' + df['id']
df['url_source'] = 'https://arxiv.org/e-print/' + df['id']

df.to_csv(path + 'scrape_df.csv')

for index, row in df[:5].iterrows():
    response = requests.get(row['url_pdf'])
    path_pdf = path + 'pdf/' + row['id'] + '.pdf'
    with open(path_pdf, 'wb') as f:
        f.write(response.content)

    response = requests.get(row['url_html'])
    soup = BeautifulSoup(response.content, "html.parser")
    filename = path + 'html/' + row['id'] + '.html'
    with open(filename, "w", encoding='utf-8') as f:
        f.write(str(soup))
    
    print(row['url_html'])
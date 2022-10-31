import arxivscraper
import requests
import tarfile
import pandas as pd
from time import sleep
from pathlib import Path
from bs4 import BeautifulSoup
from grobid_client.grobid_client import GrobidClient

max_articles = 50
folder_name = 'mine'+str(max_articles)+'/'
base_dir = './case-studies/arxiv-corpus/'

path_corpus = base_dir + folder_name
Path(path_corpus).mkdir(parents=True, exist_ok=True)
Path(path_corpus + 'pdf/').mkdir(parents=True, exist_ok=True)
Path(path_corpus + 'html/').mkdir(parents=True, exist_ok=True)
Path(path_corpus + 'parsed_xml/').mkdir(parents=True, exist_ok=True)
Path(path_corpus + 'source/').mkdir(parents=True, exist_ok=True)

def scrape_arxiv(path_corpus, max_articles, initialize=True, date_from='2022-10-24',date_until='2022-10-25'):
    if initialize:
        scraper = arxivscraper.Scraper(category='cs',date_from=date_from,date_until=date_until,t=10, filters={'categories':['cs.lg']})
        output = scraper.scrape()
        cols = ('id', 'title', 'categories', 'abstract', 'doi', 'created', 'updated', 'authors')
        output = pd.DataFrame(output, columns=cols)
        output[:max_articles].to_csv(path_corpus + 'scrape_df_' + str(max_articles)+ '.csv', index_label="index")
        output.to_csv(path_corpus + 'scrape_df_full.csv', index_label="index")
        # output[['id']][:max_articles].to_csv(path_corpus + 'scrape_df_' + str(max_articles) + '_id.csv', index_label="index")

    else:
        output = pd.read_csv(path_corpus + 'scrape_df.csv')
        
    output['url_pdf'] = 'https://arxiv.org/pdf/' + output['id'].apply(str) + '.pdf'
    output['url_html'] = 'https://arxiv.org/abs/' + output['id'].apply(str)
    output['url_source'] = 'https://arxiv.org/e-print/' + output['id'].apply(str)
    return output

df = scrape_arxiv(path_corpus, max_articles, True)
client = GrobidClient(config_path="./grobid_client_python/config.json")

for index, row in df[:max_articles].iterrows():
    response = requests.get(row['url_pdf'])
    path_pdf = path_corpus + 'pdf/' + str(row['id']) + '.pdf'
    with open(path_pdf, 'wb') as f:
        f.write(response.content)

    response = requests.get(row['url_html'])
    soup = BeautifulSoup(response.content, "html.parser")
    filename = path_corpus + 'html/' + str(row['id']) + '.html'
    with open(filename, "w", encoding='utf-8') as f:
        f.write(str(soup))
        
    response = requests.get(row['url_source'], stream=True)
    file = tarfile.open(fileobj=response.raw, mode="r|gz")
    file.extractall(path_corpus + 'source/' + str(row['id']) + '/')
    file.close()
    
    print(row['url_html'])
    sleep(1)
    
    client.process("processFulltextDocument", path_corpus + "pdf/", output=path_corpus + "parsed_xml/" , n=20)
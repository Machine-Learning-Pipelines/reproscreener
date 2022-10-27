import arxiv, logging
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path

logging.basicConfig(level=logging.INFO)

path = './case-studies/arxiv-corpus/mine50/'
Path(path + 'pdf/').mkdir(parents=True, exist_ok=True)
Path(path + 'html/').mkdir(parents=True, exist_ok=True)

# client_delay = arxiv.Client(
#   page_size = 100,
#   delay_seconds = 3,
#   num_retries = 3
# )

search = arxiv.Search(
  query = "cat:cs",
  max_results = 4,
  sort_by = arxiv.SortCriterion.SubmittedDate,
  sort_order = arxiv.SortOrder.Descending
)

print(search)

for paper in search.results( ):
    id = paper.get_short_id()
    print(id)

    url = 'https://arxiv.org/abs/' + id
    print(url)

    paper.download_pdf(dirpath = path + 'pdf/')

    # paper.download_pdf(filename = id+".pdf", dirpath="./case-studies/arxiv-corpus/mine/")
    # paper = next(arxiv.Search(id_list=["1605.08386v1"]).results())
    # paper.download_pdf(dirpath="./mydir", filename="downloaded-paper.pdf")

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # print(content)
    filename = path + 'html/' + id + '.html'
    with open(filename, "w", encoding='utf-8') as file:
        file.write(str(soup))
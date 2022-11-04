from pathlib import Path
from bs4 import BeautifulSoup
from pandas import read_csv, DataFrame
import keywords

max_articles=50
folder_name = 'mine'+str(max_articles)+'/'
base_dir = './case-studies/arxiv-corpus/'

path_corpus = base_dir+folder_name
manual_eval =  read_csv(path_corpus + '../manual_eval.csv')
manual_eval = manual_eval.drop(columns='index')

# TODO gunder var read function
gunderson_vars = ["id","problem","objective","research_method","research_questions","pseudocode","training_data","validation_data","test_data","results","hypothesis","prediction","method_source_code","hardware_specifications","software_dependencies","experiment_setup","experiment_source_code","affiliation"]

repro_eval = read_csv(path_corpus + 'scrape_df_' + str(max_articles)+ '.csv', dtype=object)
repro_eval = repro_eval[['id']]
repro_eval = repro_eval.reindex(gunderson_vars, axis=1) 

path_corpus = base_dir + folder_name
Path(path_corpus + 'output/').mkdir(parents=True, exist_ok=True)

if Path(path_corpus + 'scrape_df_'+str(max_articles)+'.csv').is_file():
    df = read_csv(path_corpus + 'scrape_df_'+str(max_articles)+'.csv', dtype=object)
else:
    print("Cannot find corpus dataframe")

for index, row in df[:2].iterrows():
    path_xml = path_corpus + 'parsed_xml/' + str(row['id']) + '.tei.xml'
    soup = keywords.read_tei(path_xml)
    print(soup.title.getText())

    affiliation = keywords.find_affiliation(soup)
    repro_eval.affiliation.iloc[index] = affiliation

    found_vars = keywords.find_vars(soup)

    for i in repro_eval.columns.drop(['id', 'affiliation']):
        if i in found_vars:
            # repro_eval[i][index] = 1
            repro_eval.loc[:, (i, index)] = 1
        else:
            repro_eval.loc[:, (i, index)] = 0

    # print(repro_eval.iloc[0][2:])
    df_compare = DataFrame([manual_eval.iloc[index][1:].values, repro_eval.iloc[index][1:].values],
                           columns=gunderson_vars[1:], 
                           index=['manual_eval','reproscreener_eval'])
    print(df_compare.T)
    
repro_eval.to_csv(path_corpus + 'output/reproscreener_eval.csv', index_label="index")
    
    
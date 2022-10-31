import re
from pathlib import Path
from bs4 import BeautifulSoup
from flashtext import KeywordProcessor
from pandas import read_csv, DataFrame
import exrex

max_articles=50
folder_name = 'mine'+str(max_articles)+'/'
base_dir = './case-studies/arxiv-corpus/'

path_corpus = base_dir + folder_name
Path(path_corpus + 'output/').mkdir(parents=True, exist_ok=True)

def read_tei(tei_file):
    with open(tei_file, 'r') as tei:
        soup = BeautifulSoup(tei, features='xml')
        return soup

if Path(path_corpus + 'scrape_df_'+str(max_articles)+'.csv').is_file():
    df = read_csv(path_corpus + 'scrape_df_'+str(max_articles)+'.csv', dtype=object)
else:
    print("Cannot find corpus dataframe")
    
manual_eval =  read_csv(path_corpus + '../manual_eval.csv')
gunderson_vars = ["id","problem","objective","research_method","research_questions","pseudocode","training_data","validation_data","test_data","results","hypothesis","prediction","method_source_code","hardware_specifications","software_dependencies","experiment_setup","experiment_source_code","affiliation"]

repro_eval = read_csv(path_corpus + 'scrape_df_' + str(max_articles)+ '.csv', dtype=object)
repro_eval = repro_eval[['id']]
repro_eval = repro_eval.reindex(gunderson_vars, axis=1) 

keys_problem = list(exrex.generate('((((P|p)roblem) ((S|s)tatement)))|((((R|r)esearch) ((P|p)roblem)))|((P|p)roblems?)'))
keys_objective = list(exrex.generate('((((O|o)bjective)))|((((G|g)oal)|((((R|r)esearch) ((O|o)bjective))))|((((R|r)esearch) ((G|g)oal))))'))
keys_research_method = list(exrex.generate('((R|r)esearch (M|m)ethods?)|'\
    '(M|m)ethods?'))
keys_research_questions = list(exrex.generate('((((R|r)esearch)))|((((Q|q)uestions?)|'\
    '((((R|r)esearch) ((O|o)bjective))))|'\
    '((((R|r)esearch) ((G|g)oal))))'))
keys_pseudocode = list(exrex.generate('((P|p)seudo-?code)|(Algorithm [1-9])'))
keys_training_data = list(exrex.generate('(T|t)raining (D|d)ata'))
keys_validation_data = list(exrex.generate('(V|v)alidation (D|d)ata'))
keys_test_data = list(exrex.generate('(T|t)est (D|d)ata'))
keys_experiment_setup = list(exrex.generate('(E|e)xperimental( |-)(S|s)etup|'\
    '((H|h)yper( |-)(P|p)arameters)'))
keys_hypothesis = list(exrex.generate('(H|h)ypothes(i|e)s'))
keys_prediction = list(exrex.generate('(P|p)redictions?'))
keys_hardware_specifications = list(exrex.generate('(H|h)ardware (S|s)pecification(s)'))
keys_software_dependencies = list(exrex.generate('(S|s)oftware (D|d)ependencies'))
keys_affiliation = list(exrex.generate('edu'))
keys_method_source_code = list(exrex.generate('(G|g)it( )?(H|h)ub|'\
    '(B|b)it(B|b)ucket|'\
    '(G|g)it( )?(L|l)ab'))

keyword_dict = {
    "problem": keys_problem,
    "objective": keys_objective,
    "research_method": keys_research_method,
    "research_questions": keys_research_questions,
    "pseudocode": keys_pseudocode,
    
    "training_data": keys_training_data,
    "validation_data": keys_validation_data,
    "test_data": keys_test_data,
    
    "hypothesis": keys_hypothesis,
    "prediction": keys_prediction,
    "method_source_code": keys_method_source_code,
    "hardware_specifications": keys_hardware_specifications,
    "software_dependencies": keys_software_dependencies,
    "experiment_setup": keys_experiment_setup,
    
    "affiliation": keys_affiliation,
}

for index, row in df.iterrows():
    path_xml = path_corpus + 'parsed_xml/' + str(row['id']) + '.tei.xml'
    soup = read_tei(path_xml)
    print(soup.title.getText())

    paras = [t.getText(separator=' ', strip=True) for t in soup.find_all('p')]
    emails = [t.getText(separator=' ', strip=True) for t in soup.find_all('email')]
    
    keyword_processor = KeywordProcessor(case_sensitive=True)
    keyword_processor.add_keywords_from_dict(keyword_dict)

    all_found_paras = []
    edu_ind_emails = [0,0]

    for i in range(len(paras)):
        all_found_paras.append(keyword_processor.extract_keywords(paras[i], span_info=True))    
    non_empty_found_paras = [x for x in all_found_paras if x != []]
    
    for i in range(len(emails)):
        edu = keyword_processor.extract_keywords(emails[i], span_info=True)
        if len(edu)>0:
            edu_ind_emails[0]+=1
        elif len(edu)==0:
            edu_ind_emails[1]+=1
    
    if edu_ind_emails[0]>0 and edu_ind_emails[1]>0: # both
        affiliation = 2
    elif edu_ind_emails[0]==0 and edu_ind_emails[1]>0: # industry
        affiliation = 1
    elif edu_ind_emails[0]>0 and edu_ind_emails[1]==0: # academia
        affiliation = 0
    
    found_vars = set()
    for i in non_empty_found_paras:
        for j in i:
            found_vars.add(j[0])

    for i in repro_eval.columns[1:]:
        if i in found_vars:
            repro_eval[i][index] = 1
            # repro_eval.loc[:, (i)]
        else:
            repro_eval[i][index] = 0
    repro_eval[i][index] = affiliation
    
    # print(repro_eval.iloc[0][2:])
    df_compare = DataFrame([manual_eval.iloc[index][2:].values, repro_eval.iloc[index][1:].values],
                           columns=gunderson_vars[1:], 
                           index=['manual_eval','reproscreener_eval'])
    print(df_compare.T)
repro_eval.to_csv(path_corpus + 'output/reproscreener_eval.csv', index_label="index")
    
    
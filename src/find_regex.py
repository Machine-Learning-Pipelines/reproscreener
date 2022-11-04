from pathlib import Path
from pandas import read_csv, concat
import keywords

def init_environment(num_articles=50, folder_name_base='mine', base_dir='./case-studies/arxiv-corpus/', compare_manual=False):
    # Initialize paths
    folder_name = folder_name_base + str(num_articles) + '/'
    path_corpus = base_dir + folder_name
    Path(path_corpus + 'output/').mkdir(parents=True, exist_ok=True)

    gunderson_vars = ["problem", "objective", "research_method", "research_questions", "pseudocode", "training_data", "validation_data", "test_data", "results", "hypothesis", "prediction", "method_source_code", "hardware_specifications", "software_dependencies", "experiment_setup", "experiment_source_code", "affiliation"]
    
    repro_eval = init_repro_eval(path_corpus, num_articles, gunderson_vars)
    found_vars = calculate_repro_eval_scores(path_corpus, repro_eval)[['id', 'found_vars', 'affiliation']]
    repro_eval_filled = set_repro_eval_scores(concat([repro_eval, found_vars],
                                                     axis=0,
                                                     join='inner'), gunderson_vars)
    print(repro_eval_filled)

def init_repro_eval(path_corpus, num_articles, variables):
    # Create an empty repro_eval dataframe with provided @variables
    repro_eval = read_csv(path_corpus + 'scrape_df_' + 
                          str(num_articles) + '.csv', dtype=object)
    repro_eval = repro_eval[['id']]
    repro_eval = repro_eval.reindex(['id', *variables], axis=1)
    return repro_eval

def calculate_repro_eval_scores(path_corpus, df):
    # TODO increase PYDEVD_WARN_EVALUATION_TIMEOUT to 15-30s
    print("Reading files...")
    df['soup'] = df['id'].apply(lambda x: keywords.read_tei(path_corpus + 'parsed_xml/' + x + '.tei.xml'))
    df['title'] = df['soup'].apply(lambda x: x.title.getText())
    print("Finding variables in files...")
    df['found_vars'] = df['soup'].apply(lambda x: keywords.find_vars(x))
    df['affiliation'] = df['soup'].apply(lambda x: keywords.find_affiliation(x))
    return df[['id', 'title', 'found_vars', 'affiliation']]

def set_repro_eval_scores(df, variables):
    for col in df.columns.drop(['id', 'affiliation', 'found_vars']):
        df['found_vars_array'] = df['found_vars'].apply(lambda x: calc_found_vars_array(x, variables.remove('id')))
    return df
        # if col in df['found_vars']:
        #     repro_eval.at[index, col] = 1
        # else:
        #     repro_eval.at[index, col] = 0


# test1 = {'pseudocode', 'objective', 'research_questions'}
# gunderson_vars = ["id", "problem", "objective", "research_method", "research_questions", "pseudocode", "training_data", "validation_data", "test_data", "results", "hypothesis", "prediction", "method_source_code", "hardware_specifications", "software_dependencies", "experiment_setup", "experiment_source_code", "affiliation"]

init_environment()

def calc_found_vars_array(found_vars, variables):
    vars_array = [0] * len(variables)
    for i, var in enumerate(variables):
        vars_array[i] = 1 if var in found_vars else 0
    return vars_array

# calc_found_vars_array(test1, gunderson_vars.remove('id'))
# init_environment()
#     if compare_manual:
#         manual_eval =  read_csv(path_corpus + '../manual_eval.csv')
#         manual_eval = manual_eval.drop(columns='index')
#         df_compare = DataFrame(
#             [manual_eval.iloc[index][1:].values, repro_eval.iloc[index][1:].values],
#             columns=gunderson_vars[1:],
#             index=['manual_eval', 'reproscreener_eval'])
#         print(df_compare.T)

    # repro_eval.to_csv(path_corpus + 'output/repro_eval.csv', index_label="index")
    # return(repro_eval)
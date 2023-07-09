import torch
import os
from transformers import BertTokenizer, BertModel, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

do_lower_case = True
model_name = "allenai/scibert_scivocab_uncased"
model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
tokenizer = BertTokenizer.from_pretrained(model_name, do_lower_case=do_lower_case)


def embed_text(text):
    input_ids = torch.tensor(tokenizer.encode(text)).unsqueeze(0)
    outputs = model(input_ids)
    last_hidden_states = outputs[0]
    return last_hidden_states.mean(1)


def get_similarity(em, em2):
    return cosine_similarity(em.detach().numpy(), em2.detach().numpy())[0][0]


def evaluate_abstract(abstract, metrics):
    results = []
    for metric, description in metrics.items():
        max_score = 0
        matched_sentence = ""
        for sentence in abstract.split("."):
            score = get_similarity(embed_text(sentence), embed_text(description))
            if score > max_score:
                max_score = score
                matched_sentence = sentence
        if max_score < 0.5:
            matched_sentence = ""
        results.append({"Evaluation metric": metric, "Matched sentence/phrase": matched_sentence, "Score": max_score})
    return pd.DataFrame(results)


metrics = {
    "Problem": "The problem the research seeks to solve",
    "Objective": "The objective of the research",
    "Research method": "The research method used",
    "Research questions": "The research question(s) asked",
    "Pseudocode": "Method described using pseudo code",
    "Dataset": "Is the dataset made available or shared",
    "Hypothesis": "Hypotheses that the authors make prior to conducting the experiment",
    "Prediction": "The predicted results by the authors",
    "Method source code": "Is the code for the research open source and shared?",
    "Software dependencies": "Software packages/dependencies used to run the code",
    "Experiment setup": "Is the experimental setup described?",
}

abstract_path = "case-studies/arxiv-corpus/gold_standard/abstracts/1606.04671.txt"

with open(abstract_path, "r") as file:
    abstract = file.read()

table = evaluate_abstract(abstract, metrics)
print(table)

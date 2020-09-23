# mdl_similarities.py

# Load models and embeddings

import pandas as pd
import numpy as np
import string
import json
import re

from gensim.models import Doc2Vec
from gensim.corpora import Dictionary
from sklearn.metrics.pairwise import cosine_similarity

import pickle

def _initialize():

	model = Doc2Vec.load('models/resto_d2v_model.mdl')
	vocab = Dictionary.load('models/resto_vocab.pkl')

	with open('models/resto_d2v_embeddings.pkl', 'rb') as f:
		embed_resto = pickle.load(f)

	with open('models/resto_restaurants.pkl', 'rb') as f:
		resto = pickle.load(f)
	# resto = pd.read_csv('data/business_extract_filter_clean1.csv', index_col=0)
	return model, embed_resto, resto, vocab

def _get_ents(entities, vocab):
    ents = []
    
    for ent in entities:
        if ent in vocab.token2id:
            ents.append(ent)
        
        ents.extend([e.strip(string.punctuation).lower() 
                     for e in ent.split() 
                     if e.strip(string.punctuation).lower() in vocab.token2id])
    
    ents = list(set(ents))
    return ents

def similar_resto(terms, top_n=10, 
	get_fields=['name', 'address', 'hours', 'categories']):

	model, embed_resto, resto, vocab = _initialize()

	# categories = ', '.join([x.lower() for x in resto['categories']])
	# categories = list(set(categories.split(', ')))
	# categories = [x for x in categories if x!='others']

	terms = [x.lower() for x in terms]
	
	# user_cat = [x for x in terms if x in categories]

	user = _get_ents(terms, vocab)
	addn = []

	for term in user:
		addn.extend([x for (x,y) in model.wv.most_similar(term, topn=3)])

	user.extend(addn)
	user = list(set(user))

	if len(user)==0:
		return(None)

	embed_user = model.infer_vector(user)
	embed_resto['user_query'] = embed_user
	embed_all = pd.DataFrame.from_dict(embed_resto, orient='index')

	cosine_sim = cosine_similarity(embed_all)[-1][:-1]
	df_cosine_sim = pd.Series(cosine_sim, index=list(embed_resto.keys())[:-1])
	df_cosine_sim.sort_values(ascending=False, inplace=True)

	# filter by matching terms
	# patterns = '('+')|('.join(user)+')'
	# reg = re.compile(patterns, re.IGNORECASE)
	# print(patterns)

	# resto_filtered = list(resto['terms'].apply(lambda x: reg.search(x)!=None).index)
	# df_cosine_sim1 = df_cosine_sim.loc[resto_filtered]
	# print(df_cosine_sim[:top_n], df_cosine_sim[:top_n].index)
	return resto.loc[df_cosine_sim[:top_n].index,get_fields]

def load_resto():
	with open('models/resto_restaurants.pkl', 'rb') as f:
		resto = pickle.load(f)
	# resto = pd.read_csv('data/business_extract_filter_clean1.csv', index_col=0)
	return resto
# For debugging
# print(similar_resto(['salmon sashimi', 'Japanese']))
# print(similar_resto(['salmon sashimi']))
# print(similar_resto(['Japanese']))
# print(similar_resto(['pho']))
# print(similar_resto(['Vietnamese']))
# print(similar_resto(['Western']))
# print(similar_resto(['kimbab', 'Korean']))
# print(similar_resto(['ramen']))
# print(similar_resto(['ramen bowl']))

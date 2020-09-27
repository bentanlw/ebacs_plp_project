# mdl_recognition.py

# Load word embeddings
import pandas as pd
import pickle

import spacy, random
from tqdm import tqdm
from spacy.util import minibatch, compounding

def BuildNer():
    
	# get training data
	with open('data/train_data_ner_add.pkl', 'rb') as f:
		df = pickle.load(f)

	# create a language class from pretrain spaCy
	model = spacy.load('en_core_web_sm', disable=['ner'])
	model.vocab.vectors.name = 'spacy_pretrained_vectors'

	# add ner pipeline to model
	ner = model.create_pipe('ner')
	model.add_pipe(ner, last=True)

	# disable pipelines
	other_pipes = [pipe for pipe in model.pipe_names if pipe!='ner']
	disabled_pipes = model.disable_pipes(*other_pipes)

	# add labels to ner pipeline
	for _, annotations in df:
		for ent in annotations.get("entities"):
			ner.add_label(ent[2])

	# initialize random weights
	model.begin_training()

	for i in tqdm(range(6)):

		random.shuffle(df)
		losses = {}

		# batch up the examples using spaCy's minibatch
		batches = minibatch(df, size=compounding(32.0, 256.0, 2.0))

		for batch in batches:
			texts, annotations = zip(*batch)
			model.update(
			texts,       # batch of texts
			annotations, # batch of annotations
			drop=0.3,    # dropout - make it harder to memorise data
			losses=losses,
			)

		print('Iteration {:03d} completed. Losses: {:>8.4f}'\
			.format(i+1, losses['ner']))

	disabled_pipes.restore()

	model.to_disk('models/resto_entity_recognition')

	return None

def PredictNer(text):

	model = spacy.load('models/resto_entity_recognition')
	prediction = model(text)

	labels = set([ent.label_ for ent in prediction.ents])

	prediction1 = {label : [ent.text for ent in prediction.ents if ent.label_==label] 
	for label in labels}

	# prediction1 = {ent.label_ : ent.text for ent in prediction.ents}
	prediction1['text'] = [prediction.text]
	
	return prediction1
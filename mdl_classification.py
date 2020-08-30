# mdl_classification.py

# Load word embeddings
import pickle
import numpy as np

with open('embeddings.pkl', 'rb') as f:
	embeddings = pickle.load(f)

embeddings['DUMMY'] = np.zeros(100, dtype=np.float32)
embedding_matrix = np.array([em for em in embeddings.values()])

# Build dictionary
from gensim.corpora import Dictionary
dictionary = Dictionary([list(embeddings.keys())])

DUMMY_ID = dictionary.token2id['DUMMY']

# Shallow CNN classifier
from keras import layers
from keras.models import Sequential, Model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, Conv1D, MaxPooling1D, GlobalMaxPooling1D, Dense

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.utils import class_weight

# Load pretrained model
from keras.models import load_model
# MODEL = load_model('models/resto_classification_cnn.h5')

# with open('models/labels.pkl', 'rb') as f:
# 	LABELS = pickle.load(f)

import spacy
nlp = spacy.load('en_core_web_sm', disable=['tagger','ner'])

import pandas as pd

def Train(intents):

	x_train, x_test, y_train, y_test, class_weights = PrepareData(intents)
	TrainCnn(x_train, x_test, y_train, y_test, class_weights)

	return None

def PrepareData(intents):

	global LABELS

	# clean text
	df = np.array([(pattern, intent[0]) for intent in intents.items() for pattern in intent[1].split(';')])
	df = pd.DataFrame(df)
	df.columns = ['text', 'label']

	# perform train-test split
	x_train, x_test, y_train, y_test = train_test_split(df['text'], df['label'], test_size=0.3, random_state=0)
	split_index = (y_train.index.values, y_test.index.values)

	y_labels = y_test

	# tokenise text
	x_train = [[dictionary.token2id.get(tok.text.lower(), DUMMY_ID) for tok in nlp(x)] for x in x_train]
	x_test = [[dictionary.token2id.get(tok.text.lower(), DUMMY_ID) for tok in nlp(x)] for x in x_test]

	# pad the sentences
	x_train = pad_sequences(x_train, padding='post', maxlen=512)
	x_test = pad_sequences(x_test, padding='post', maxlen=512)

	# create class weight dictionary
	class_weights = class_weight.compute_class_weight('balanced', np.unique(y_train), y_train)
	class_weights = dict(enumerate(class_weights))

	# one-hot encoding for y
	def EncodeY(y):

		# integer encode
		label_encoder = LabelEncoder()
		integer_encoded = label_encoder.fit_transform(y)

		# binary encode
		onehot_encoder = OneHotEncoder(sparse=False)
		integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)
		onehot_encoded = onehot_encoder.fit_transform(integer_encoded)

		return onehot_encoded

	y_train = EncodeY(y_train)
	y_test = EncodeY(y_test)

	y_encoded = pd.Series([np.argmax(y) for y in y_test])
	y_encoded = [(k,v) for (k,v) in zip(y_encoded,y_labels)]
	y_encoded = list(set(y_encoded))
	LABELS = {k:v for (k,v) in y_encoded}

	return x_train, x_test, y_train, y_test, class_weights

def TrainCnn(x_train, x_test, y_train, y_test, class_weights):

	maxlen     = 256
	vocab_size = embedding_matrix.shape[0]
	embed_dim  = embedding_matrix.shape[1]
	input_len  = x_train.shape[1]
	output_len = len(class_weights)
	embed_wgt  = embedding_matrix

	model = Sequential()
	model.add(Embedding(input_dim=vocab_size,  		# this is the vocab size
                        output_dim=embed_dim, 		# this is the embedding
                        input_length=input_len,		# this is the seq length
                        weights=[embedding_matrix],	# this is the pre-trained
                        trainable=False))			# this disables updates

	model.add(Conv1D(32, 2, activation='relu'))
	model.add(GlobalMaxPooling1D())
	model.add(Dense(output_len, activation='softmax'))

	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])

	model.summary()

	#train the model
	hist = model.fit(x_train, y_train, class_weight=class_weights, 
		epochs=50, batch_size=16, verbose=True, 
		validation_data=(x_test, y_test)).history

	print('')

	loss, accuracy = model.evaluate(x_train, y_train, verbose=True)
	print('Training Accuracy: {:.4f}'.format(accuracy))

	loss, accuracy = model.evaluate(x_test, y_test, verbose=False)
	print('Testing Accuracy:  {:.4f}'.format(accuracy))

	model.save('models/resto_classification_cnn.h5')

	with open('models/labels.pkl', 'wb') as f:
		pickle.dump(LABELS, f)

	# plot_history(hist)

	return None

# model_cnn = TrainCnn()

def PrepareData2(text):

	text = [[dictionary.token2id.get(tok.text.lower(), DUMMY_ID) for tok in nlp(text)]]
	text = pad_sequences(text, padding='post', maxlen=512)

	return text

def PredictClass(text):
	model = load_model(r'models\resto_classification_cnn.h5')
	with open('models/labels.pkl', 'rb') as f:
		labels = pickle.load(f)

	input_text = PrepareData2(text)
	prediction = model.predict(input_text)

	if max(prediction[0])<(1/len(labels))*1.4:
		label = 'unclassified'
	else:
		label = labels[np.argmax(prediction[0])]

	print('Predicted class is:  {}'.format(label.upper()))
	print('Class probabilities: {}'.format(np.round(prediction[0],2)))
	
	return prediction, label
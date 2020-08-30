from flask import Flask, render_template
from flask import redirect, url_for
from flask import request, session
from flask import flash

from threading import Timer
import webbrowser
import yelp_functions
import json
from mdl_classification import Train, PredictClass

app = Flask(__name__)
app.secret_key = 'elym' # to access session
# app.permanent_session_lifetime = timedelta(minutes=5)

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///intents.sqlite3' # name of the table referenced
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # optional

db = SQLAlchemy(app)

class intents(db.Model):
	_id = db.Column('id', db.Integer, primary_key=True)
	intent = db.Column(db.String(64))
	patterns = db.Column(db.String(2048))

	def __init__(self, intent, patterns):
		self.intent = intent
		self.patterns = patterns

def text_to_json(text):
	text = text.split(';')
	text = {'text': text}


@app.route('/') # decorator to turn a python function to Flask view
@app.route('/home/')
def home():
    return(render_template('chatbot.html'))

@app.route('/get')
def get_bot_response():
	userText = request.args.get('msg')
	return yelp_functions.bot_response(userText)

@app.route('/intent_classification/', methods=['POST','GET'])
def intent_classification():
	if request.method == 'POST':
		
		intent = request.form['intent'].lower() # form variable name
		intent = intent.strip('; ')
		intent = ' '.join(intent.split())

		pattern = request.form['pattern'].lower() # form variable name
		pattern = pattern.strip('; ')
		pattern = ' '.join(pattern.split())

		query = request.form['query'].lower() # form variable name
		query = query.strip('; ')
		query = ' '.join(query.split())

		intent_found = intents.query.filter_by(intent=intent).first()
		
		if (request.form['submit']=='db_get'):

			if intent_found:
				return(render_template('intent_classification.html', 
					intent=intent_found.intent, pattern=intent_found.patterns, 
					status='Intent found.'))
			else:
				return(render_template('intent_classification.html', 
					intent=intent, pattern='', 
					status='Intent not found.'))
		
		if (request.form['submit']=='db_post'):

			if (intent==''):

				return(render_template('intent_classification.html', 
					intent=intent, pattern=pattern,
					status='Missing intent.'))

			if (pattern==''):

				return(render_template('intent_classification.html', 
					intent=intent, pattern=pattern,
					status='Missing patterns.'))

			if intent_found:
				# delete any existing record
				db.session.delete(intent_found)
				db.session.commit()

			# create new record
			record = intents(intent, pattern)
			db.session.add(record)
			db.session.commit()

			# check new record
			record = intents.query.filter_by(intent=intent).first()

			# backup records
			intent_found = intents.query.all()
			intent_found = {intent.intent: intent.patterns for intent in intent_found}
			with open('intents_backup.txt', 'w') as f:
				json.dump(intent_found, f, indent=2)

			return(render_template('intent_classification.html', 
				intent=record.intent, pattern=record.patterns,
				status='Intent posted to databse.'))
		
		if (request.form['submit']=='db_delete'):

			if (intent==''):

				return(render_template('intent_classification.html', 
					intent=intent, pattern=pattern,
					status='Missing intent.'))

			if intent_found:
				# delete any existing record
				db.session.delete(intent_found)
				db.session.commit()

			# check new record
			record = intents.query.filter_by(intent=intent).first()

			return(render_template('intent_classification.html', 
				intent='', pattern='',
				status='Intent deleted from database.'))
		
		if (request.form['submit']=='mdl_train'):

			intent_found = intents.query.all()
			# intent_found = [(intent.intent, intent.patterns) for intent in intent_found]
			# intent_found = [(intent.intent) for intent in intent_found]
			# intent_found = " ".join(intent_found)
			intent_found = {intent.intent: intent.patterns for intent in intent_found}

			Train(intent_found)
			intent_list = ', '.join(list(intent_found.keys()))
			# print(intent_found)
			# intent_found = 'WELLZ'

			return(render_template('intent_classification.html', 
				intent='', pattern='',
				status='Model trained. Intents: '+intent_list))
		
		if (request.form['submit']=='mdl_test'):

			if (query==''):

				return(render_template('intent_classification.html', 
					intent=intent, pattern=pattern,
					status='Missing user query.'))
			predict = PredictClass(query)
			return(render_template('intent_classification.html', 
				intent='', pattern='',
				status='Check prediction.',
				query = query,
				predict=predict))

	return(render_template('intent_classification.html', status=''))

@app.route('/entity_recognition/', methods=['POST','GET'])
def entity_recognition():
    return(render_template('entity_recognition.html'))

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__=='__main__':
    db.create_all()
    Timer(1,open_browser).start()
    app.run(debug=False) # set to False when deploying
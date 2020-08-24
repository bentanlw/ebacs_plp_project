# app.py

from flask import Flask,render_template,request
import webbrowser
from threading import Timer
import yelp_functions

app = Flask(__name__)

@app.route('/')
def test():
    return render_template("animated_chat_window.html") #to send con
    # return render_template("index.html") #to send con

@app.route("/get")
def get_bot_response():
     userText = request.args.get("msg") #get data from input,we write js  to index.html
    #  return yelp_functions.find_restaurant(userText)
     return yelp_functions.bot_response(userText)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run()
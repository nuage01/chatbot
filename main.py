from flask import Flask, render_template, request, jsonify
import os
from google import google
from test_search import bot_request

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

@app.route("/")
def hello():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])
def ask():
	message = str(request.form['msg'])
	while True:
		try:
			search_results = bot_request(message)
		except:
			search_results = "j'ai pas de réponses"
		return jsonify({'status':'OK','answer':search_results})
		# search_results

if __name__ == "__main__":
    app.run(debug=True)
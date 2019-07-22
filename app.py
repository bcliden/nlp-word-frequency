import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from collections import Counter
from bs4 import BeautifulSoup

# nltk setup
nltk.data.path.insert(
    0, os.path.dirname(os.path.abspath(__file__)) + "/nltk_data"
)  # add path to /nltk-data in root
from nltk.corpus import stopwords

stops = stopwords.words("english")
# from stop_words import stops


app = Flask(__name__)
app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

from models import *


@app.route("/", methods=["GET", "POST"])
def hello():
    errors = []
    results = {}
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form["url"]
            r = requests.get(url)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
        if r:
            # text processing
            raw = BeautifulSoup(r.text, "html.parser").get_text()
            nltk.data.path.append("./nltk_data/")  # set the path
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)
            # remove punctuation, count raw words
            nonPunct = re.compile(".*[A-Za-z].*")
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)
            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)
            # save top 25 results
            results = sorted(
                no_stop_words_count.items(), key=operator.itemgetter(1), reverse=True
            )[:25]
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count,
                )
                db.session.add(result)
                db.session.commit()
            except Exception as e:
                errors.append("unable to add item to database.")
                errors.append(e)
    return render_template("index.html", errors=errors, results=results)


if __name__ == "__main__":
    app.run()


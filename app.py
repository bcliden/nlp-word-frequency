import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import Counter, OrderedDict
from bs4 import BeautifulSoup
from rq import Queue
from rq.job import Job
from worker import conn

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

q = Queue(connection=conn)

from models import *


def count_and_save_words(url):
    # get url that the user has entered
    errors = []
    try:
        r = requests.get(url)
    except:
        errors.append("Unable to get URL. Please make sure it's valid and try again.")
        return {"error": errors}
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

    try:
        result = Result(
            url=url, result_all=raw_word_count, result_no_stop_words=no_stop_words_count
        )
        db.session.add(result)
        db.session.commit()
        return result.id
    except Exception as e:
        errors.append("unable to add item to database.")
        errors.append(e)
        return {"error": errors}


@app.route("/", methods=["GET", "POST"])
def hello():
    results = {}
    if request.method == "POST":
        url = request.form["url"]
        if "http://" not in url[:7]:
            url = "http://" + url
        job = q.enqueue_call(func=count_and_save_words, args=(url,), result_ttl=5000)
        print(job.get_id())
    return render_template("index.html", results=results)


@app.route("/results/<job_key>", methods=["GET"])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_no_stop_words.items(), key=lambda kv: kv[1], reverse=True
        )[:25]

        # sortedResults = OrderedDict(results)
        return jsonify(dict(results))
    else:
        return "Nay!", 202


if __name__ == "__main__":
    app.run()


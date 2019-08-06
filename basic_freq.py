from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import json
import sys
import os
import re
import requests
from collections import Counter


def main():

    if len(sys.argv) <= 1:
        sys.exit("no url supplied")

    url = sys.argv[1]

    if "http://" not in url[:7] and "https://" not in url[:8]:
        url = "http://" + url

    # nltk setup
    nltk.data.path.insert(
        0, os.path.dirname(os.path.abspath(__file__)) + "/nltk_data"
    )  # add path to /nltk-data in root

    stops = stopwords.words("english")

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

    response = json.dumps(
        {
            "url": url,
            "results_all": raw_word_count,
            "results_no_stops": no_stop_words_count,
        },
        ensure_ascii=False,
    )

    sys.stdout.write(response)
    sys.exit(0)


if __name__ == "__main__":
    main()


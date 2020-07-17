from pathlib import Path
import nltk

# Setup files and directories


def setup_dirs(dirs: list):
    for dir in dirs:
        if not Path.exists(dir):
            dir.mkdir(parents=True, exist_ok=True)


# Setup required NLTK corpus data

"""
Cribbed from: https://raw.githubusercontent.com/codelucas/newspaper/master/download_corpora.py
Downloads the necessary NLTK models and corpora required to support
all of newspaper's features.  Currently ~151mb.  Modify for your own needs.
"""


def download_nltk_corpora(destination: Path):
    REQUIRED_CORPORA = [
        'brown',  # Required for FastNPExtractor
        'punkt',  # Required for WordTokenizer
        'maxent_treebank_pos_tagger',  # Required for NLTKTagger
        'movie_reviews',  # Required for NaiveBayesAnalyzer
        'wordnet',  # Required for lemmatization and Wordnet
        'stopwords'
    ]
    for each in REQUIRED_CORPORA:
        print(f'Downloading {each}')
        nltk.download(each, download_dir=destination.as_posix())

"""
The .append() method (called elsewhere - in app.py) tells nltk to look in the custom download directory - that is, a subfolder in the working directory, instead of in system-wide configuration - for the corpus. Note that this seems to be the only approach that works - envs described in the 
official documentation ('NLTK_DATA') does not appear to work.  See offical documentation at: https://www.nltk.org/data.html and a relevant Stack Overflow thread at: https://stackoverflow.com/questions/44857382/change-nltk-download-path-directory-from-default-ntlk-data.
"""
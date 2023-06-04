##### IMPORTS
import numpy as np
import pandas as pd
import nltk
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import ShuffleSplit
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import os
import warnings
import seaborn as sns
import re
import string
from termcolor import colored
from nltk import word_tokenize
import string
from nltk import pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import WhitespaceTokenizer
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score

warnings.filterwarnings('ignore')
from matplotlib.pyplot import *

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from sklearn.model_selection import train_test_split

from sklearn import preprocessing

from sklearn.metrics import classification_report, accuracy_score
from sklearn.metrics import confusion_matrix

from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfTransformer



##### GLOBALS VARIABLES
seed = 12345
cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=seed)
encoder = preprocessing.LabelEncoder()


##### FUNCTIONS

def get_wordnet_pos(pos_tag):
    if pos_tag.startswith('J'):
        return wordnet.ADJ
    elif pos_tag.startswith('V'):
        return wordnet.VERB
    elif pos_tag.startswith('N'):
        return wordnet.NOUN
    elif pos_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def preprocess(text):

    text = text.lower()
    text = [t for t in text.split(" ") if len(t) > 1]
    text = [word for word in text if not any(c.isdigit() for c in word)]
    text = [word.strip(string.punctuation) for word in text]
    stop = stopwords.words('english')
    text = [x for x in text if x not in stop]
    text = [t for t in text if len(t) > 0]
    pos_tags = pos_tag(text)
    text = [WordNetLemmatizer().lemmatize(t[0], get_wordnet_pos(t[1])) for t in pos_tags]

    text = " ".join(text)
    return (text)

def split_train_holdout_test(encoder, df, verbose=True):
  train = df[df["label"] != "None"]
  test = df[df["label"] == "None"]

  train["encoded_label"] = encoder.fit_transform(train.label.values)

  train_cv, train_holdout, train_cv_label, train_holdout_label = train_test_split(train, train.encoded_label, test_size=0.33, random_state=seed)

  if(verbose):
    print("\nTrain dataset (Full)")
    print(train.shape)
    print("Train dataset cols")
    print(list(train.columns))

    print("\nTrain CV dataset (subset)")
    print(train_cv.shape)
    print("Train Holdout dataset (subset)")
    print(train_holdout.shape)

    print("\nTest dataset")
    print(test.shape)
    print("Test dataset cols")
    print(list(test.columns))

  return encoder, train, test, train_cv, train_holdout, train_cv_label, train_holdout_label

def runModel(encoder, train_vector, train_label, holdout_vector, holdout_label, type, name):
  global cv
  global seed

  ##### Classifier types
  if (type == "svc"):
    classifier = SVC()
    grid = [
      {'C': [1, 10, 50, 100], 'kernel': ['linear']},
      {'C': [10, 100, 500, 1000], 'gamma': [0.0001], 'kernel': ['rbf']},
    ]
  if (type == "nb"):
    classifier = MultinomialNB()
    grid = {}
  if (type == "maxEnt"):
      classifier = LogisticRegression()
      grid = {'penalty': ['l1','l2'], 'C': [0.001,0.01,0.1,1,10,100,1000]}

  # Model
  print(colored(name, 'red'))

  model = GridSearchCV(estimator=classifier, cv=cv,  param_grid=grid)
  print(colored(model.fit(train_vector, train_label), "yellow"))

  # Score
  print(colored("\nCV-scores", 'blue'))
  means = model.cv_results_['mean_test_score']
  stds = model.cv_results_['std_test_score']
  for mean, std, params in sorted(zip(means, stds, model.cv_results_['params']), key=lambda x: -x[0]):
      print("Accuracy: %0.3f (+/-%0.03f) for params: %r" % (mean, std * 2, params))
  print()


  print(colored("\nBest Estimator Params", 'blue'))
  print(colored(model.best_estimator_, "yellow"))

  # Predictions
  print(colored("\nPredictions:", 'blue'))
  model_train_pred = encoder.inverse_transform( model.predict(holdout_vector) )
  print(model_train_pred)

  # Confusion Matrix
  cm = confusion_matrix(holdout_label, model_train_pred)

  # Transform to df
  cm_df = pd.DataFrame(cm,
                      index = ['FAKE','REAL'],
                      columns = ['FAKE','REAL'])


  plt.figure(figsize=(5.5,4))
  sns.heatmap(cm_df, annot=True, fmt='g')
  plt.ylabel('True label')
  plt.xlabel('Predicted label')
  plt.show()

  # Accuracy
  acc = accuracy_score(holdout_label, model_train_pred)
  print(colored("\nAccuracy:", 'blue'))
  print(colored(acc, 'green'))
  return [name, model, acc]


def pos_tag_words(text):
    pos_text = nltk.pos_tag(nltk.word_tokenize(text))
    return " ".join([pos + "-" + word for word, pos in pos_text])
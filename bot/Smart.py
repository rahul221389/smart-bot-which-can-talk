# Importing the useful libraries.

import nltk
from nltk.stem.lancaster import LancasterStemmer

nltk.download('punkt')
import numpy as np
import tensorflow as tf
import random
import json

import tflearn
import pickle
import os
from bot import Bot


"""*****************************************************************************************************************************************"""


stemmer = LancasterStemmer()  # Creating stemmer object to stream the input data. It is used during the data preprocessing step.

with open("data/json file/intents.json") as f:
    data = json.load(f)

data['intents'][:2]

"""****************************************************************************************************************************"""

# DATA PREPROCESSING STEP.

# Performing try and except so that we do not need to perform data preproccessing again and again.
try:
    with open("data/data.pickle", 'rb') as f:
        words, labels, training, output = pickle.load(f)


except Exception as e:
    words = []
    labels = []
    docs_x, docs_y = [], []
    stemmer = LancasterStemmer()
    for intent in data['intents']:
        for pattern in intent['patterns']:
            wrds = nltk.word_tokenize(
                pattern)  # Performing stremming on the words. Converting words into their root word like play for playing, played, plays etc.
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent['tag'])

        if intent['tag'] not in labels:
            labels.append(intent['tag'])

    # Performing stremming on the words. Converting words into their root word like play for playing, played, plays etc.
    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    # Next 20 lines are to do OneHotEncoding.
    training, output = [], []
    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)
    with open("data/data.pickle", 'wb') as f:
        pickle.dump((words, labels, training, output), f)

"""**********************************************************************************************************************************"""

# Training and creating our model.


tf.reset_default_graph()
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
""" 1). First train the model and save it then comment the below two lines and uncomment the model.load() and run the code.

"""
model.load("data/model.tflearn")
# model.fit(training, output, n_epoch=100, batch_size=8, show_metric=True)  # Increase the n_epoch for more accuracy.
# model.save("data/model.tflearn")

"""********************************************************************************************************************************************************"""


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return np.array(bag)


"""***********************************************************************************************************************************************"""



def chat(query):

    results = model.predict([bag_of_words(query, words)])  # results will give the probabilities.
    results_index = np.argmax(results)
    tag = labels[results_index]

    for tg in data["intents"]:
        if tg['tag'] == tag:
            responses = tg['responses']

    Bot.speak(random.choice(responses))
    #print("Bot:\t", random.choice(responses))  # Bot is randomly choosing one response from responses list.




"""***********************************************************************************************************************************************************"""


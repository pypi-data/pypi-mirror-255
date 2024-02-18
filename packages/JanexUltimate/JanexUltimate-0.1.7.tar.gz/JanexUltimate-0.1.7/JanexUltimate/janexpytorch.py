import torch
import torch.nn as nn
import os

from JanexUltimate.janexpython import *

import numpy as np
import nltk
import nltk
from nltk.corpus import wordnet
from nltk.tag import pos_tag

from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()

import numpy as np
import random
import json

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

if torch.cuda.is_available():
    map_location=torch.device('cuda')
else:
    map_location=torch.device('cpu')

def bag_of_words(tokenized_sentence, words):
    # stem each word
    sentence_words = [stem(word) for word in tokenized_sentence]
    # initialize bag with 0 for each word
    bag = np.zeros(len(words), dtype=np.float32)
    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1

    return bag

class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(NeuralNet, self).__init__()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.l2 = nn.Linear(hidden_size, hidden_size)
        self.l3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()

    def forward(self, x):
        out = self.l1(x)
        out = self.relu(out)
        out = self.l2(out)
        out = self.relu(out)
        out = self.l3(out)
        # no activation and no softmax at the end
        return out

class ChatDataset(Dataset):

    def __init__(self, X_train, y_train):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train

    # support indexing such that dataset[i] can be used to get i-th sample
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]

    # we can call len(dataset) to return the size
    def __len__(self):
        return self.n_samples

class JanexPT:
    def __init__(self, intents_file_path):
        self.FILE = "data.pth"
        self.Classifier = IntentClassifier()
        self.Classifier.set_intentsfp(intents_file_path)
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')
        self.intents = self.Classifier.load_intents()
        self.device = torch.device('cpu')
        self.accuracy = None

    def set_device(self, device):
        self.device = torch.device(device)

    def pattern_compare(self, input_string):
        try:
            self.data = torch.load(self.FILE, map_location=map_location)
        except:
            self.trainpt()
            self.data = torch.load(self.FILE, map_location=map_location)
        self.input_size = self.data["input_size"]
        self.hidden_size = self.data["hidden_size"]
        self.output_size = self.data["output_size"]
        self.all_words = self.data['all_words']
        self.tags = self.data['tags']
        self.model_state = self.data["model_state"]
        self.model = NeuralNet(self.input_size, self.hidden_size, self.output_size).to(self.device)
        self.intents = self.Classifier.load_intents()
        self.model.load_state_dict(self.model_state)
        self.model.eval()
        sentence = input_string

        sentence = tokenize(sentence)

        X = bag_of_words(sentence, self.all_words)
        X = X.reshape(1, X.shape[0])
        X = torch.from_numpy(X).to(self.device)

        output = self.model(X)
        _, predicted = torch.max(output, dim=1)

        tag = self.tags[predicted.item()]

        probs = torch.softmax(output, dim=1)
        prob = probs[0][predicted.item()]

        self.accuracy = prob.item()

        for intent in self.intents['intents']:
            if tag == intent["tag"]:
                self.intent = intent
                return intent

    def ResponseGenerator(self, response):
        synonyms = []

        response_list = self.IntentMatcher.tokenize(response)

        for token in response_list:
            token = str(token)
            for syn in wordnet.synsets(token):
                for lemma in syn.lemmas():
                    synonyms.append(lemma.name())

        synonyms = list(set(synonyms))

        synonyms = [s for s in synonyms if s != token]

        new_response = " ".join(synonyms)

        return new_response

    def get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # Default to Noun

    def generate_response_with_synonyms(self, response, strength):
        response_list = self.IntentMatcher.tokenize(response)
        tagged_response = pos_tag(response_list)
        new_response = []
        prestrength = 0

        for word, tag in tagged_response:
            if prestrength > strength:
                break
            og_word = word
            synsets = wordnet.synsets(word, pos=self.get_wordnet_pos(tag))
            if synsets:
                synonyms = synsets[0].lemmas()  # Use the first synonym
                new_word = synonyms[0].name() if synonyms else word
                if og_word.istitle():
                    new_word = new_word.capitalize()
            else:
                new_word = word
                if og_word.istitle():
                    new_word = new_word.capitalize()

            index = response.find(og_word)

            response = response[:index] + new_word + response[index+len(og_word):]

            prestrength = prestrength + 1

        response = self.IntentMatcher.ResponseGenerator(response)

        return response

    def trainpt(self):
        try:
            open("train.py", "r")
            os.system(f"curl -o data.pth https://raw.githubusercontent.com/Cipher58/intents-file/main/data.pth -#")
        except:
            print("Janex-PyTorch: Train program not detected, downloading the program and the pre-trained model from Github.")
            os.system(f"curl -o train.py https://raw.githubusercontent.com/Cipher58/Janex-PyTorch/main/Stock/train.py -#")
            os.system(f"curl -o data.pth https://raw.githubusercontent.com/Cipher58/intents-file/main/data.pth -#")

    def modify_data_path(self, new_path):
        self.FILE = new_path

# Training Program


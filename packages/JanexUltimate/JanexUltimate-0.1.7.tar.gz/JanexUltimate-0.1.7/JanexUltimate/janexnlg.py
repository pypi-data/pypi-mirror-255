import json
import numpy as np
import spacy
import torch
import torch.nn as nn
import torch.optim as optim
from JanexUltimate.janexpython import *
import os

class SimpleRNN(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(SimpleRNN, self).__init__()
        self.rnn = nn.RNN(input_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        out, _ = self.rnn(x)
        return out

def decompress(janex_model):
    with open(f"{janex_model}", "rb") as bin_file:
        json_data = bin_file.read()
        loaded_data = json.loads(json_data.decode('utf-8'))
        return loaded_data

class NLG:
    def __init__(self, spacy_model, janex_model):
        self.nlp = spacy.load(spacy_model)
        self.trends_dictionary = decompress(janex_model)
        self.max_tokens = 20
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.rnn_model = SimpleRNN(300, 128, len(self.trends_dictionary))

    def set_device(self, device_type):
        self.device = torch.device(device_type)

    def get_word_vector(self, word):
        return self.nlp(word).vector

    def predict_next_word(self, input_word):
        context_window_size = 3
        context_vectors = np.array([self.get_word_vector(word) for word in self.inputs.split()[-context_window_size:]])

        context_vectors = np.resize(context_vectors, 300)
        # Assuming you have already prepared context_vectors as input
        context_tensor = torch.Tensor(context_vectors).unsqueeze(0)  # Add batch dimension

        output = self.rnn_model(context_tensor)
        _, predicted_idx = torch.max(output, 1)
        best_next_word = list(self.trends_dictionary.keys())[predicted_idx.item()]

        if best_next_word and output[0, predicted_idx.item()] > 0.1:
            return best_next_word

    def generate_sentence(self, input):
        sentence = ""

        for _ in range(self.max_tokens):
            self.inputs = input
            input = sentence[:-1]
            next_word = self.predict_next_word(input)
            sentence = f"{sentence} {next_word}"

        return sentence

import json
import spacy

import os

class NLGTraining:
    def __init__(self):
        self.directory = None
        self.nlp = None

    def set_directory(self, directory):
        self.directory = directory

    def set_spacy_model(self, model):
        self.nlp = spacy.load("en_core_web_md")

    def extract_data_from_file(self, file_path):
        with open(file_path, 'r') as file:
            data = file.read()
            return data

    def cycle_through_files(self):

        TotalData = ""

        for root, dirs, files in os.walk(self.directory):
            for file_name in files:
                if file_name.endswith(".txt"):
                    file_path = os.path.join(root, file_name)
                    data = self.extract_data_from_file(file_path)
                    TotalData += data

        return TotalData

    def train_data(self):
        trends_dictionary = {}

        if self.directory is None:
            print("JanexNLG Error! You need to set the directory in which your .txt files are contained.")
            print("")
            print("Use NLGTraining.set_directory('directory')")
            return 404
        if self.nlp is None:
            print("JanexNLG Error! You need to set your desired spacy model. Please select from en_core_web_sm, en_core_web_md or en_core_web_lg!")
            print("")
            print("Use NLGTraining.set_spacy_model('your_desired_model')")
            return 404

        data = self.cycle_through_files()

        tokens = tokenize(data)
        totalsum = len(tokens)

        for i, token in enumerate(tokens):
            progress = i / totalsum * 100
            print(f"Processing token number {i} of {totalsum} ({progress:.2f}% complete)")
            if token not in trends_dictionary:
                # Get the previous and next tokens if they exist
                prev_token = tokens[i - 1] if i > 0 else None
                next_token = tokens[i + 1] if i < len(tokens) - 1 else None

                # Create a list to store the word before and word after
                context_words = []
                if prev_token:
                    context_words.append(prev_token)
                if next_token:
                    context_words.append(next_token)

                # Compute the vector arrays for context words using spaCy
                context_vectors = []
                for word in context_words:
                    word_doc = self.nlp(word)
                    context_vectors.append(word_doc.vector.tolist())

                # Append the context words and their vectors to the dictionary
                trends_dictionary[token] = {
                    "context_words": context_words,
                    "context_vectors": context_vectors
                }
            else:
                prev_token = tokens[i - 1] if i > 0 else None
                next_token = tokens[i + 1] if i < len(tokens) - 1 else None

                # If the token already exists, add the previous and next words
                if prev_token:
                    trends_dictionary[token]["context_words"].append(prev_token)
                if next_token:
                    trends_dictionary[token]["context_words"].append(next_token)

        # Save the trends_dictionary to a JSON file with the desired structure
        output_dictionary = {}
        for token, context_info in trends_dictionary.items():
            output_dictionary[token] = context_info

        with open("custom_janexnlg_model.bin", "wb") as bin_file:
            json_data = json.dumps(output_dictionary).encode('utf-8')
            bin_file.write(json_data)

    def finetune_model(self, model_name):
        with open(model_name, "rb") as bin_file:
            json_data = bin_file.read()
            trends_dictionary = json.loads(json_data.decode('utf-8'))

        if self.directory is None:
            print("JanexNLG Error! You need to set the directory in which your .txt files are contained.")
            print("")
            print("Use NLGTraining.set_directory('directory')")
            return 404
        if self.nlp is None:
            print("JanexNLG Error! You need to set your desired spacy model. Please select from en_core_web_sm, en_core_web_md or en_core_web_lg!")
            print("")
            print("Use NLGTraining.set_spacy_model('your_desired_model')")
            return 404

        data = self.cycle_through_files()

        tokens = tokenize(data)
        totalsum = len(tokens)

        for i, token in enumerate(tokens):
            progress = i / totalsum * 100
            print(f"Processing token number {i} of {totalsum} ({progress:.2f}% complete)")
            if token not in trends_dictionary:
                # Get the previous and next tokens if they exist
                prev_token = tokens[i - 1] if i > 0 else None
                next_token = tokens[i + 1] if i < len(tokens) - 1 else None

                # Create a list to store the word before and word after
                context_words = []
                if prev_token:
                    context_words.append(prev_token)
                if next_token:
                    context_words.append(next_token)

                # Compute the vector arrays for context words using spaCy
                context_vectors = []
                for word in context_words:
                    word_doc = self.nlp(word)
                    context_vectors.append(word_doc.vector.tolist())

                # Append the context words and their vectors to the dictionary
                trends_dictionary[token] = {
                    "context_words": context_words,
                    "context_vectors": context_vectors
                }
            else:
                prev_token = tokens[i - 1] if i > 0 else None
                next_token = tokens[i + 1] if i < len(tokens) - 1 else None

                # If the token already exists, add the previous and next words
                if prev_token:
                    trends_dictionary[token]["context_words"].append(prev_token)
                if next_token:
                    trends_dictionary[token]["context_words"].append(next_token)

        # Save the trends_dictionary to a JSON file with the desired structure
        output_dictionary = {}
        for token, context_info in trends_dictionary.items():
            output_dictionary[token] = context_info

        with open("custom_janexnlg_model.bin", "wb") as bin_file:
            json_data = json.dumps(output_dictionary).encode('utf-8')
            bin_file.write(json_data)
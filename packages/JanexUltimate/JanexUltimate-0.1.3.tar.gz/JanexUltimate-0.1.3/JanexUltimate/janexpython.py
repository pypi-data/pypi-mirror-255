# Word Manipulation Toolkit

def tokenize(input_string):
    input_string = str(input_string)

    new_string = ""
    deletion = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

    input_string = input_string.lower()

    for x in input_string:
        if x not in deletion:
            new_string += x

    words = []

    processed_string = new_string
    words = processed_string.split(" ")

    return words

def stem(input_word):
    suffixes = ["ing", "ly", "ed", "es", "'s", "er", "est", "y", "ily", "able", "ful", "ness", "less", "ment", "ive", "ize", "ous"]
    for suffix in suffixes:
        if input_word.endswith(suffix):
            input_word = input_word[:-len(suffix)]
            break
    return input_word


# Vector Toolkit

import numpy as np

def string_vectorize(input_string):
    ascii_values = [ord(char) for char in input_string]  # Get ASCII values for each character
    ascii_vectors = np.array(ascii_values)              # Convert the list to a numpy array
    return ascii_vectors

def reshape_array_dimensions(array, dimensions):
    target_dim = dimensions
    vector1 = np.resize(array, target_dim)
    return vector1

def calculate_cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm_vector1 = np.linalg.norm(vector1)
    norm_vector2 = np.linalg.norm(vector2)

    if norm_vector1 == 0 or norm_vector2 == 0:
        return 0  # Handle zero division case

    similarity = dot_product / (norm_vector1 * norm_vector2)
    return similarity

# Intent Classifier Toolkit

class IntentClassifier:
    def __init__(self):
        self.intents_file_path = None
        self.thesaurus_file_path = None
        self.vectors_file_path = None

    def set_vectorsfp(self, vectors_file_path):
        self.vectors_file_path = vectors_file_path
        print(f"Janex: Pre-trained vector file path set to {vectors_file_path}")

    def set_intentsfp(self, intents_file_path):
        self.intents_file_path = intents_file_path

    def set_dimensions(self, dimensions):
        self.dimensions = dimensions

    def load_intents(self):
        with open(self.intents_file_path, "r") as json_file:
            data = json.load(json_file)
            return data

    def load_vectors(self):
        with open(self.vectors_file_path, "r") as json_file:
            data = json.load(json_file)
            return data

    def train_vectors(self):
        vectors = {}

        intents = self.load_intents()

        for intent_class in intents["intents"]:
            for pattern in intent_class["patterns"]:
                if pattern is not None:
                    pattern_tokens = tokenize(pattern)
                    for token in pattern_tokens:
                        token_vectors = string_vectorize(token)
                        token_vectors = reshape_array_dimensions(token_vectors, self.dimensions)
                        token_vectors = token_vectors.tolist()
                        vectors[token] = token_vectors
            for response in intent_class["responses"]:
                if response is not None:
                    response_tokens = tokenize(response)
                    for token in response_tokens:
                        token_vectors = string_vectorize(token)
                        token_vectors = reshape_array_dimensions(token_vectors, self.dimensions)
                        vectors[token] = token_vectors.tolist()

        with open(self.vectors_file_path, "w") as vectors_file:
            json.dump(vectors, vectors_file)

    def classify(self, input_string):
        predefined_vectors = self.load_vectors()
        intents = self.load_intents()

        input_tokens = tokenize(input_string)
        vectors_to_classify = []
        highest_similarity = 0

        for token in input_tokens:
            if token in predefined_vectors:
                token_vectors = predefined_vectors[token]
            else:
                token_vectors = string_vectorize(token)

            token_vectors = reshape_array_dimensions(token_vectors, self.dimensions)
            vectors_to_classify.append(token_vectors)

        for intent_class in intents["intents"]:
            intent_vectors_to_classify = []
            for pattern in intent_class["patterns"]:
                pattern_tokens = tokenize(pattern)
                for token in pattern_tokens:
                    if token in predefined_vectors:
                        pattern_token_vectors = predefined_vectors[token]
                        intent_vectors_to_classify.append(pattern_token_vectors)

            vectors_to_classify = reshape_array_dimensions(vectors_to_classify, self.dimensions)
            intent_vectors_to_classify = reshape_array_dimensions(intent_vectors_to_classify, self.dimensions)

            similarity = calculate_cosine_similarity(vectors_to_classify, intent_vectors_to_classify)

            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_class = intent_class

        if most_similar_class:
            return most_similar_class
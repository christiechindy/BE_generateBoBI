import torch
import torchtext
import torch.nn.functional as F
import re
import numpy as np
import nltk
from nltk.corpus import stopwords

glove_file = "C:\\Users\\LENOVO\\Downloads\\glove.840B.300d\\glove.840B.300d.txt"
glove = torchtext.vocab.Vectors(glove_file)

stop_words = stopwords.words("english")

def cos_sim(w1, w2):
    return float(torch.cosine_similarity(glove[w1].unsqueeze(0),
                                   glove[w2].unsqueeze(0)))

def eucli_dist(w1, w2):
    return float(torch.norm(glove[w2] - glove[w1]))

def count(w1, w2):
    cossim = cos_sim(w1, w2)
    euclid = eucli_dist(w1, w2)
    print(f"{w1} & {w2}\nCos = {cossim}\nEucl = {euclid}")

def print_closest_words_eucl(vec, n=5):
    dists = torch.norm(glove.vectors - vec, dim=1) # compute distances to all words
    lst = sorted(enumerate(dists.numpy()), key=lambda x: x[1]) # sort by distance
    for idx, difference in lst[1:n+1]:
        print(glove.itos[idx], difference)

def print_closest_words_cossim(vec, n=5):
    # Compute cosine similarity between input vector and all word vectors
    sims = F.cosine_similarity(glove.vectors, vec.unsqueeze(0), dim=1)
    
    # Sort by similarity (descending order)
    lst = sorted(enumerate(sims.numpy()), key=lambda x: x[1], reverse=True)
    
    # Print the closest words
    for idx, similarity in lst[:n]:
        print(glove.itos[idx], similarity)

def toTokens(text):
    tokens = re.findall(r"\b(\w+)\b", text)
    # for i in range(len(tokens)):
    #     if tokens[i] in stop_words:
    #         del tokens[i]
    for t in tokens[:]: 
        if t in stop_words:
            tokens.remove(t)
    return tokens

def count_vectors_average(sentence):
    word_list = toTokens(sentence)
    vector_list = [glove[word] for word in word_list]

    vector_list_np = [vector.numpy() for vector in vector_list]

    average_vector_np = np.mean(vector_list_np, axis=0)
    return torch.tensor(average_vector_np)

def average_first(text1, text2):
    ave1 = count_vectors_average(text1)
    ave2 = count_vectors_average(text2)

    dist_cos = float(torch.cosine_similarity(ave1.unsqueeze(0), ave2.unsqueeze(0)))
    dist_eucl = float(torch.norm(ave2 - ave1))
    return dist_cos, dist_eucl

def count_CosAvF(text1, text2):
    ave1 = count_vectors_average(text1)
    ave2 = count_vectors_average(text2)
    
    dist_cos = float(torch.cosine_similarity(ave1.unsqueeze(0), ave2.unsqueeze(0)))
    return dist_cos

def each_then_average(text1, text2):
    tokens1 = toTokens(text1)
    tokens2 = toTokens(text2)
    dists_cossim = []
    dists_eucl = []
    for i in range(len(tokens1)):
        for j in range(len(tokens2)):
            dists_eucl.append(eucli_dist(tokens1[i], tokens2[j]))
            dists_cossim.append(cos_sim(tokens1[i], tokens2[j]))

    np_eucl = np.array(dists_eucl)
    np_cossim = np.array(dists_cossim)

    ave_eucl = np.mean(np_eucl)
    ave_cossim = np.mean(np_cossim)

    return ave_cossim, ave_eucl

# return tokens which doesnt have embeddings
def checkIfHasEmbeddings(tokens):
    doesntHaveEmbeddings = []
    for token in tokens: 
        tokenVec = glove[token]
        if (tokenVec == torch.zeros_like(tokenVec)).all():
            doesntHaveEmbeddings.append(token)

    return doesntHaveEmbeddings
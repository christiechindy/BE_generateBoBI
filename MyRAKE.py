import unicodedata
import regex as re
# from segtok.segmenter import split_single
# import nltk
# from nltk import pos_tag
# from nltk.tokenize import word_tokenize
import spacy

spacy_model = spacy.load("en_core_web_md")

def is_symbol_or_greek(char):
    # category = unicodedata.category(char)
    name =  unicodedata.name(char)
    return ('GREEK' in name) or ('SIGN' in name) or ('INCREMENT' in name) or ('REPLACEMENT CHAR' in name)

def countCapitalLetters(string):
    return len(re.findall(r"[A-Z]", string))

# return an integer telling how much punctuations (other than hyphen and a pair of parentheses) in that string
def countPuncts(stringg):
    count = 0
    adaBukaKurung = 0
    ygDalamKurung = ""

    if bool(re.search(r"[-+]", stringg)):
        if len(stringg) <= 5:
            return 3
        if bool(re.search(r'[^A-Za-z \-]', stringg)) and (len(stringg) <= 7):
            return 3
        
    if bool(re.search(r'f\(x', stringg, re.IGNORECASE)):
        return 3

    for i,char in enumerate(stringg):
        if adaBukaKurung > 0:
            ygDalamKurung += char

        if (char == "(" or (char == ")" and adaBukaKurung<1)):
            count += 3
            if char == "(":
                adaBukaKurung += 1
        elif char == ")" and adaBukaKurung>0:
            count -= 3
            adaBukaKurung -= 1
        elif (not char.isalpha()) and (not char.isdigit()) and (not char.isspace()) and (char != "-") or (is_symbol_or_greek(char)):
            count += 1
    
    if (re.search(r'\(.*\)', stringg) and len(ygDalamKurung) < 4 and countCapitalLetters(ygDalamKurung) < 2):
        return 3
    
    return count

# return a dictionary 
# key    (string) : word
# value  (number) : amount of time that word appears in the text
def countWordFreq(text):
    words = re.findall(r'\b\w+\b', text.lower())
    wordFreq = {}
    for w in words:
        if w in wordFreq:
            wordFreq[w] += 1
        else:
            wordFreq[w] = 1
    return wordFreq


# return list of words 
def splitEachWord(text):
    return re.findall(r'\b\w+\b', text.lower())


# '.' and ',' is also got into the list
def splitEachWord_(text):
    return re.findall(r'\b\w+\b|[.,]', text)


# return list of candidate keyphrase
# split by: stopwords | [.,] | words which length <= 3
# we use splitEachWord_ here because the [.]/[,] will also separate / split the text
def splitTextByStopwords_scratch(text, stopwords):
    words = splitEachWord_(text)
    # print("words", words)
    chunks = []
    tmp = []
    for w in words:
        if (w.lower() in stopwords) or w[-1]=="." or len(w)<3: 
            if tmp==[]:
                continue
            addToChunk = " ".join(tmp)
            chunks.append(addToChunk)
            tmp = []
        else:
            tmp.append(w)
    if tmp!=[]:
        addToChunk = " ".join(tmp)
        chunks.append(addToChunk)
    
    return chunks


# Download the averaged perceptron tagger resource
# nltk.download('averaged_perceptron_tagger')

# tdk boleh avoid JJ klo di nltk
tags_to_avoid = ["DT", "RB", "VBZ", "CC", "CD", "EX", "IN", "LS", "MD", "PDT", "POS", "PRP", "VB", "VBD", "VBG", "VBN", "VBP", "WDT", "WP", "WP$", "WRB", "PRP$"]

spacy_tags_to_avoid = ["CC", "CD", "DT", "EX", "IN", "JJR", "MD", "PDT", "POS", "PRP", "PRP$", "RB", "RBR", "RBS", "RP", "TO", "UH", "VBZ", "VBN", "VBD", "VBG", "WDT", "WP", "WP$", "WRB", "ADD", "BES", "HVS", "VBP", "JJS", "SYM", ",", "."]

# equivalent to splitTextByStopwords_scratch
def splitTextByTAG_scratch(text):
    doc = spacy_model(text) # printed like a string, but not of string type -> the length is equal to the number of tagged
    chunks = []
    tmp = ""
    i = 0

    while i < len(doc):
        the_word = doc[i].text
        the_tag = doc[i].tag_
        is_stopwords = doc[i].is_stop

        nextChar = doc[i+1].text if i!=len(doc)-1 else ""

        # if the previous character is -
        if i!=0 and doc[i-1].text=="-":
            if "-" in tmp: 
                tmp += the_word + ("-" if nextChar=="-" else " ")
                if nextChar == "-":
                    i += 2
                else:
                    i += 1
                continue
            else:
                i += 1
                continue

        # if the next character is -
        if i != len(doc)-1:
            if nextChar == "-":
                if (the_tag not in spacy_tags_to_avoid):
                    tmp += the_word + "-"
                    i += 2
                    continue

        if (
            (the_tag in spacy_tags_to_avoid) 
            or (is_stopwords) 
            or (len(the_word)==1) 
            or (((len(the_word)==2) or (len(the_word)==3)) and not the_word.isupper()) 
            or ("." in the_word) 
            or not (the_word[0].isalpha() or the_word[0].isdigit())
        ):
            if len(tmp) <= 3: # cands shouldnt be less than 3 characters
                tmp = ""
            else:
                chunks.append(tmp.strip())
                tmp = ""
        else:
            tmp += (the_word + " ")
        i += 1
    
    if tmp != "":
        chunks.append(tmp.strip())

    # make sure tidak ada keyError saat generate cooccurence matrix
    # filter chunks that has too many punctuations
    # filter chunks yang punya �
    will_be_in_wordfreqs = splitEachWord(text)
    for c in chunks[:]:
        if (bool(re.search(r"[�^∥|⋆→¯×;=+∆τ]", c))): 
            chunks.remove(c)
            continue

        jumlahPunc = countPuncts(c)
        if (jumlahPunc > 1) or ((jumlahPunc == 1) and (len(c) <= 5)):
            chunks.remove(c)
            continue

        chunk_tmp = splitEachWord(c)
        for eachword in chunk_tmp:
            if eachword not in will_be_in_wordfreqs:
                chunks.remove(c)
                break

    return chunks


# return list of unique word of candidate keyphrases returned from splitTextByStopwords_scratch or splitTextByTAG_scratch
def getUniqueKeywordFromCandidates(cands):
    # cands is returned from splitTextByStopwords_scratch
    uniKeyword = []
    for i in range(len(cands)):
        words = splitEachWord(cands[i])
        for w in words:
            if w not in uniKeyword:
                uniKeyword.append(w)
    
    return uniKeyword


# return list of lists of number
def generateCoOccurenceMatrix(uniqueKeywordFromCandidates, cands, text):
    n = len(uniqueKeywordFromCandidates)
    matrix = [[-7 for _ in range(n)] for _ in range(n)]
    wordFreqs = countWordFreq(text)
    # isi dlu yang diagonal
    for i in range(n):
        matrix[i][i] = wordFreqs[uniqueKeywordFromCandidates[i]]
    # print(matrix)

    for i in range(n):
        for j in range(n):
            if (i == j):
                continue
            elif matrix[j][i] != -7:
                matrix[i][j] = matrix[j][i]
            else:
                tmp = 0
                for k in range(len(cands)):
                    if uniqueKeywordFromCandidates[i].lower() in splitEachWord(cands[k]) and uniqueKeywordFromCandidates[j].lower() in splitEachWord(cands[k]):
                        tmp += 1
                matrix[i][j] = tmp

    return matrix


# return a dictionary of 
# key    (string) : word
# value  (number) : degree score of that word
def countDegreeScore(uniqueKeywordFromCandidates, coOccurenceMatrix):
    word_degreeScore = {}
    for i in range(len(uniqueKeywordFromCandidates)):
        degree_of_word = sum(coOccurenceMatrix[i])
        word_frequency = coOccurenceMatrix[i][i]
        degree_score = degree_of_word / word_frequency
        word_degreeScore[uniqueKeywordFromCandidates[i]] = degree_score
    return word_degreeScore


def sum_ascii(string):
    return sum(ord(char) for char in string)


def removeDuplicationInCands(cands): # also remove keyphrase with more than 5 words
    nonDuplCands = []

    for cand in cands:
        if len(splitEachWord(cand)) >= 5:
            continue 

        if cand.lower() not in [ndpl.lower() for ndpl in nonDuplCands]:
            idx__ = next((j for j, ndpls in enumerate(nonDuplCands) if splitEachWord(cand) == splitEachWord(ndpls)), None)
            if idx__ is None:
                nonDuplCands.append(cand)
            else: #klo sdh ada di nonDuplCands
                if "-" in cand: 
                    nonDuplCands[idx__] = cand 
                # klo "-" in nonDuplCands[idx__] brti cckmi, jgnmi gntiki

        else: # kalau sdh ada mi di nonDuplCands
            idx = next((i for i, ndpl in enumerate(nonDuplCands) if ndpl.lower() == cand.lower()), None)
            # cek! kalau lebih kapital ki, gnti dgn yg ini
            if (sum_ascii(cand) < sum_ascii(nonDuplCands[idx])):
                nonDuplCands[idx] = cand
                continue

    return nonDuplCands


# return a dictionary
# key   (string) : candidate keyphrase (non duplicate one)  
# value (number) : total degree score of each word in the phrase
def generateFinalScore(nonDuplCands, degreeScore):
    finalScores = {}
    # print(f"nonDuplCands = {nonDuplCands}\ndegreeScore = {degreeScore}")
    for i in range(len(nonDuplCands)):
        words = splitEachWord(nonDuplCands[i])
        score = 0
        for w in words:
            score += degreeScore[w.lower()]
        finalScores[nonDuplCands[i]] = score
    return finalScores


# connect all of the functions
# variant : using stopwords to split
def all_useSW(text, stopwords):
    cands = splitTextByStopwords_scratch(text, stopwords)
    uniqueKeywordFromCandidates = getUniqueKeywordFromCandidates(splitTextByStopwords_scratch(text, stopwords))
    coOccurenceMatrix = generateCoOccurenceMatrix(uniqueKeywordFromCandidates, cands, text)
    finalScores = generateFinalScore(removeDuplicationInCands(cands),
                              countDegreeScore(uniqueKeywordFromCandidates, coOccurenceMatrix))
    return dict(sorted(finalScores.items(), key=lambda item: item[1], reverse=True))


# connect all of the functions
# variant : using tag to split
def all(text):
    cands = splitTextByTAG_scratch(text)
    uniqueKeywordFromCandidates = getUniqueKeywordFromCandidates(splitTextByTAG_scratch(text))
    coOccurenceMatrix = generateCoOccurenceMatrix(uniqueKeywordFromCandidates, cands, text)
    finalScores = generateFinalScore(removeDuplicationInCands(cands),
                              countDegreeScore(uniqueKeywordFromCandidates, coOccurenceMatrix))
    sortedRake = dict(sorted(finalScores.items(), key=lambda item: item[1], reverse=True))
    copy_sortedRake = sortedRake.copy()
    for idx in copy_sortedRake:
        if copy_sortedRake[idx] == 0:
            del sortedRake[idx]
    return sortedRake
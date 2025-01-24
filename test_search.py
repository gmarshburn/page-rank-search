import pytest
from index import *
from file_io import *
import xml.etree.ElementTree as et
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


def test_parsing_and_tokenizing():
    '''
    tests the parsing and tokenizing of a page's text
    ''' 
    n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
    text = "[[intentionality|intentional]] object, both in the sense of history as [[tradition]] and sense"
    parsed_words_list = re.findall(n_regex, text.lower())

    assert parsed_words_list == ['[[intentionality|intentional]]', 'object', 'both', 'in', 'the', 'sense', \
                                'of', 'history', 'as', '[[tradition]]', 'and', 'sense']
    
def test_stop_words():
    '''
    tests the stopping and stemming of words in the parsed and tokenized list of text
    '''
    nltk.download('stopwords')
    STOP_WORDS = set(stopwords.words('english'))
    no_stop_list = []
    parsed_words_list = ['[[intentionality|intentional]]', 'object', 'both', 'in', 'the', 'sense', \
                        'of', 'history', 'as', '[[tradition]]', 'and', 'sense']

    for word in parsed_words_list:
        if word not in STOP_WORDS:
            no_stop_list.append(word)
    
    assert "epistemology" not in STOP_WORDS
    assert "in" in STOP_WORDS
    assert no_stop_list == ['[[intentionality|intentional]]', 'object', 'sense', 'history', '[[tradition]]', 'sense']

def test_stemming():
    nltk_test = PorterStemmer()
    corpus = []
    no_stop_list = ['[[intentionality|intentional]]', 'object', 'sense', 'history', '[[tradition]]', 'sense']
    link_list = ['[[intentionality|intentional]]', '[[tradition]]']
    link_no_pipe_list = ['[[tradition]]']
    links_to_set = set()

    if len(no_stop_list) != 0:
        for word in no_stop_list:
            if word in link_list: # stems words that are links
                if word in link_no_pipe_list: # if the link has no pipe in it
                    changed_word = word[2:-2]
                    links_to_set.add(changed_word)
                    stemmed = nltk_test.stem(changed_word)
                    corpus.append(stemmed)
                else: # if the link has a pipe in it
                    changed_word = word[2:-2]
                    first_half = changed_word.split("|")[0]
                    second_half = changed_word.split("|")[1]
                    links_to_set.add(first_half)
                    if ' ' in second_half: # if the text part of the link with a pipe has a space in it
                        no_space_regex = '''[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
                        no_space_list = re.findall(no_space_regex, second_half)
                        for word in no_space_list:
                            stemmed = nltk_test.stem(second_half)
                            corpus.append(stemmed)
                    else: # if the text part of the link with a pipe is only one word
                        stemmed = nltk_test.stem(second_half)
                        corpus.append(stemmed)
            else: # stems other normal words
                stemmed_word = nltk_test.stem(word)
                corpus.append(stemmed_word)
    assert corpus == ['intent', 'object', 'sens', 'histori', 'tradit', 'sens']

def test_tf():
    corpus = ['in', 'object', 'sens', 'histori', 'tradit', 'tradit', 'object']
    words_to_frequency = {}

    for word in corpus:
        if word in words_to_frequency:
            words_to_frequency[word] += 1
        else:
            words_to_frequency[word] = 1
    
    frequency = list(words_to_frequency.keys())
    frequency.sort(key = lambda x : words_to_frequency[x], reverse = True)
    
    assert words_to_frequency == {'histori': 1, 'in': 1, 'object': 2, 'sens': 1, 'tradit': 2}
    assert frequency[0] == 'object'
    assert words_to_frequency['object']/words_to_frequency[frequency[0]] == 1
    assert words_to_frequency['histori']/words_to_frequency[frequency[0]] == 1/2

def test_idf():
    words_to_ids = {'histori': {10 : 1}, 'in': {20: 1}, 'object': {30: 1, 60: 1}, 'sens': {40: 1}, 'tradit': {50: 1, 70: 1}}
    id_to_titles = {10: 'a', 20: 'b', 30: 'c', 40: 'd', 50: 'e', 60: 'f', 70: 'g'}
    
    idf1 = math.log((len(id_to_titles)/len(words_to_ids['object'])), 10)
    idf2 = math.log((len(id_to_titles)/len(words_to_ids['in'])), 10)
    
    assert idf1 == 0.5440680443502756
    assert idf2 == 0.8450980400142567

def test_distance():
    id_to_titles = {10: 'a', 20: 'b', 30: 'c', 40: 'd', 50: 'e', 60: 'f', 70: 'g'}
    ids_to_rank_prime = {}
    id_to_rank = {}

    for id in id_to_titles:
        id_to_rank[id] = 0
        ids_to_rank_prime[id] = 1/(len(id_to_titles))
            
    distances = 0
    for id in id_to_titles:
        distances += (ids_to_rank_prime[id] - id_to_rank[id]) ** 2
    final_distance = math.sqrt(distances)

    assert final_distance == 0.3779644730092272

def test_weight():
    id_to_titles = {10: 'a', 20: 'b', 30: 'c', 40: 'd', 50: 'e', 60: 'f', 70: 'g'}
    ids_to_other_pages = {10: {100, 1000, 1100}, 20: {200, 2000}, 30: {300, 3000}, 40: {400}, 50: {}, 60: {600, 6000, 6600}, 70: {70}}
    total_weights = []
    n = len(id_to_titles)
    for k in ids_to_other_pages:
        nk = len(ids_to_other_pages[k])
        if nk == 0:
            weight = 0.15/n + (0.85*(1/(n - 1)))
            for x in range(n - 1):
                total_weights.append(weight)
        else:
            for j in ids_to_other_pages[k]:
                if nk == 1:
                    if k == j:
                        weight = 0.15/n + (0.85*(1/(n - 1)))
                    else:
                        weight = 0.15/n + (0.85*(1/(nk)))
                else:
                    if j in ids_to_other_pages[k]:
                        weight = 0.15/n + (0.85*(1/nk))
                    else:
                        weight = 0.15/n
                total_weights.append(weight)
    
    assert total_weights == [0.30476190476190473, 0.30476190476190473, 0.30476190476190473, # id 10
                            0.4464285714285714, 0.4464285714285714, # id 20
                            0.4464285714285714, 0.4464285714285714, # id 30
                            0.8714285714285714, # id 40
                            0.1630952380952381, 0.1630952380952381, 0.1630952380952381, 0.1630952380952381, 0.1630952380952381, 0.1630952380952381, # id 50
                            0.30476190476190473, 0.30476190476190473, 0.30476190476190473, # id 60
                            0.1630952380952381] # id 70

def test_idf_tf():
    i = Indexer("wikis/test_tf_idf.xml", "titles.txt", "documents.txt", "words.txt")
    assert i.word_to_relevance == {'1': {1: 0.15904041823988746},
                                '2': {2: 0.15904041823988746},
                                '3': {3: 0.15904041823988746},
                                'ate': {2: 0.15904041823988746},
                                'bit': {1: 0.11739417270378749, 3: 0.11739417270378749},
                                'chees': {2: 0.17609125905568124, 3: 0.17609125905568124},
                                'dog': {1: 0.11739417270378749, 2: 0.11739417270378749},
                                'man': {1: 0.15904041823988746},
                                'page': {1: 0.0, 2: 0.0, 3: 0.0}}

def test_pagerank1():
    i = Indexer("wikis/PageRankExample1.xml", "titles.txt", "documents.txt", "words.txt")
    assert i.id_to_rank == {1: 0.4326427188659158, 2: 0.23402394780075067, 3: 0.33333333333333326}
    assert i.word_to_relevance == {'a': {1: 0.23856062735983122},
                                'b': {1: 0.17609125905568124, 2: 0.17609125905568124},
                                'c': {1: 0.17609125905568124, 3: 0.17609125905568124},
                                'f': {3: 0.23856062735983122}}

def test_pagerank2():
    i = Indexer("wikis/PageRankExample2.xml", "titles.txt", "documents.txt", "words.txt")
    assert i.id_to_rank == {1: 0.20184346250214996,
                            2: 0.03749999999999998,
                            3: 0.37396603749279056,
                            4: 0.3866905000050588}
    assert i.word_to_relevance == {'ash': {1: 0.20068666377598746, 4: 0.20068666377598746},
                                'bash': {2: 0.20068666377598746},
                                'cash': {1: 0.12493873660829993, 3: 0.12493873660829993, 4: 0.12493873660829993},
                                'dash': {2: 0.12493873660829993, 3: 0.12493873660829993, 4: 0.12493873660829993}}

def test_pagerank3():
    i = Indexer("wikis/PageRankExample3.xml", "titles.txt", "documents.txt", "words.txt")
    assert i.id_to_rank ==  {1: 0.05242784862611451,
          2: 0.05242784862611451,
          3: 0.4475721513738852,
          4: 0.44757215137388523}
    assert i.word_to_relevance == {'amber': {1: 0.3010299956639812},
          'bash': {2: 0.6020599913279624},
          'cash': {3: 0.3010299956639812, 4: 0.3010299956639812},
          'dash': {3: 0.3010299956639812, 4: 0.3010299956639812},
          'fake': {1: 0.3010299956639812}}

def test_pagerank4():
    i = Indexer("wikis/PageRankExample4.xml", "titles.txt", "documents.txt", "words.txt")
    assert i.id_to_rank == {1: 0.0375, 2: 0.0375, 3: 0.46249999999999997, 4: 0.4624999999999999}
    assert i.word_to_relevance == {'ash': {1: 0.10034333188799373},
                                'bash': {2: 0.10034333188799373},
                                'cash': {1: 0.12493873660829993, 3: 0.12493873660829993, 4: 0.12493873660829993},
                                'dash': {2: 0.062469368304149966, 3: 0.062469368304149966, 4: 0.062469368304149966}}

# def test_small_wiki():
#     i = Indexer("wikis/SmallWiki.xml", "titles.txt", "documents.txt", "words.txt")
#     assert i.id_to_rank == {}


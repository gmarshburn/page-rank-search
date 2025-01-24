import math
import file_io
import xml.etree.ElementTree as et
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import sys

'''
indexes the xml that will be searched through for quicker querying
'''
class Indexer:
    def __init__(self, xml_path: str, titles_path: str, docs_path: str, words_path: str):
        '''
        initialization method for the indexer class
        initializes dictionaries to keep track of data and writes this data to the 
        file in which they are stored
        parameters: the file paths for the xml to parse and the three document to which 
        the evaluated data will be written and stored
        '''

        # creates the data structures to store information about the entire xml
        self.id_to_title = {}
        self.word_to_relevance = {}
        self.id_to_rank = {}
        self.id_to_other_pages = {}
        self.id_to_corpus = {}
        self.word_to_frequency = {}
        self.word_to_ids = {}
        self.title_to_id = {}

        self.parse_xml(xml_path)

        # writes the calculated data about the xml to files so the data will 
        # be retained throughout querying and the querier can access it
        file_io.write_title_file(titles_path, self.id_to_title)
        file_io.write_docs_file(docs_path, self.id_to_rank)
        file_io.write_words_file(words_path, self.word_to_relevance)

    def parse_xml(self, xml_path: str):
        '''
        parses the xml to be searched through for easier querying. 
        runs through each page and each word on each page to 
        calculate each word's relevance and each page's pagerank
        parameter: the file path of the xml to be parsed
        '''
        print("parsing")
        # sets up the xml for parsing, the stop words library, and the word stemmer
        root = et.parse(xml_path).getroot()
        element_tree = root.findall("page")
        nltk.download('stopwords')
        STOP_WORDS = set(stopwords.words('english'))
        nltk_test = PorterStemmer()

        # defines regexes for parsing through the text of each page
        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        link_regex = '''\[\[[^\[]+?\]\]'''
        link_no_pipe_regex = '''\[\[[^\[|]+?\]\]'''

        # loops through each page in the xml
        for page in element_tree:
            id = int(page.find('id').text)
            title = page.find('title').text.lower().strip()
            self.id_to_title[id] = title
            self.title_to_id[title] = id
            text = page.find('text').text.lower().strip()

            # creates lists to keep track of the types of links and the corpus
            parsed_words_list = re.findall(n_regex, title) + re.findall(n_regex, text)
            link_list = re.findall(link_regex, title) + re.findall(link_regex, text)
            link_no_pipe_list = re.findall(link_no_pipe_regex, title) + re.findall(link_no_pipe_regex, text)
            corpus = []
            links_to_set = set()

            # checks that none of the words in word list is an empty string and 
            # loops through the parsed words list to stem and stop them
            if len(parsed_words_list) != 0:
                for word in parsed_words_list:
                    if word in link_list: # stems and stops words that are links
                        self.parse_links(word, link_no_pipe_list, corpus, nltk_test, links_to_set, STOP_WORDS)
                    else: # stems and stops other normal words
                        if word not in STOP_WORDS:
                            stemmed_word = nltk_test.stem(word)
                            corpus.append(stemmed_word)
            
                # adds to the dictinoary that keeps track of to which other pages a page links
                corpus = [word for word in corpus if word != ""]
                self.id_to_corpus[id] = corpus
                self.id_to_other_pages[id] = links_to_set.copy()
                links_to_set.clear()

                # updates the frequency of each word in the xml for each page
                self.update_frequency(corpus, id)
            # clears the data structures that store information for each page 
            # so the same structure can be reused instead of creating a new 
            # one for each page and taking up extra space
            parsed_words_list.clear()
            link_list.clear()
            link_no_pipe_list.clear()
            corpus.clear()
            links_to_set.clear()

        # finds the the number of occurrences of the most frequently occurring term in
        frequency = list(self.word_to_frequency.keys())
        frequency.sort(key = lambda x : self.word_to_frequency[x], reverse = True)

        # calls functions to calculate relevance and pagerank
        self.calculate_relevance(frequency[0])

        # clears the data structures that store information for the xml so 
        # they don't take up extra space after their data has been used
        self.word_to_frequency.clear()
        self.word_to_ids.clear()
        self.id_to_corpus.clear()

        #filter all the titles that are not in the wiki
        for id in self.id_to_other_pages:
            self.id_to_other_pages[id] = set([title for title in self.id_to_other_pages[id] if title in self.title_to_id])

        self.calculate_page_rank()

        self.id_to_other_pages.clear()
    
    def check_link(self, link):
        if link in self.title_to_id:
            return True
        return False

    def parse_links(self, word, link_no_pipe_list, corpus, nltk_test, links_to_set, STOP_WORDS):
        '''
        parses links by separating links from meta links and stemming and stopping each
        adds the correct distinct word back into the corpus of an page and the correct 
        distinct word to the links_to_set within the id_to_other_pages dictionary to 
        track which pages link to which other pages
        parameters: the word (in this case link) to be considered, the list of links 
        that contain no pipes (and are therefore not meta links), the corpus of words 
        for the page, the nltk variable, the set to which the stemmed and 
        stopped links will be added, and the built-in list of stop words
        '''
        if word in link_no_pipe_list: # if the link has no pipe in it
            changed_word = word[2:-2]
            links_to_set.add(changed_word)
            if ' ' in changed_word:
                no_space_regex = '''[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
                no_space_list = re.findall(no_space_regex, changed_word)
                for word in no_space_list:
                    if word not in STOP_WORDS:
                        stemmed = nltk_test.stem(word)
                        corpus.append(stemmed)
            else:
                if changed_word not in STOP_WORDS:
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
                    if word not in STOP_WORDS:
                        stemmed = nltk_test.stem(word)
                        corpus.append(stemmed)
            else: # if the text part of the link with a pipe is only one word
                if second_half not in STOP_WORDS:
                    stemmed = nltk_test.stem(second_half)
                    corpus.append(stemmed)
    
    def update_frequency(self, corpus, id):
        '''
        updates the frequency of words in each corpus to represent 
        the number of times each word appears in an xml
        parameters: the corpus for each page and the id of the page that was just parsed
        '''
        for word in corpus:
            if word not in self.word_to_frequency:
                self.word_to_frequency[word] = 1
            else:
                self.word_to_frequency[word] += 1
            
            if word not in self.word_to_ids:
                self.word_to_ids[word] = {}

            if id not in self.word_to_ids[word]:
                self.word_to_ids[word][id] = 1
            else:
                self.word_to_ids[word][id] += 1


    def calculate_relevance(self, max_frequency):
        print("calculating relevance")
        '''
        calculates the relevance of each word to each document with the term 
        frequency and the inverse document frequency
        parameters: the maximum frequency of all the 
        words
        '''
        for word in self.word_to_frequency:
            tf = self.word_to_frequency[word]/self.word_to_frequency[max_frequency]
            idf = math.log10((len(self.id_to_title)/len(self.word_to_ids[word])))
            for id in self.word_to_ids[word]:
                if word not in self.word_to_relevance:
                    self.word_to_relevance[word] = {}
                self.word_to_relevance[word][id] = tf*idf
    
    def calculate_page_rank(self):
        print("calculating pagerank")
        """
        calculates the page rank authority for each page in the xml using the 
        weight each document gives to another and the distance to determine 
        if the calculated ranks have converged enough to be accurate
        """
        id_to_rank_prev = {}

        for id in self.id_to_title:
            self.id_to_rank[id] = 1/len(self.id_to_title)
            id_to_rank_prev[id] = 0.0
        
        while self.calculate_distance(id_to_rank_prev) > 0.001:
            id_to_rank_prev = self.id_to_rank.copy()
            for j in self.id_to_title:
                self.id_to_rank[j] = 0.0
                for k in self.id_to_title:
                    self.id_to_rank[j] += self.calculate_weight(k, j) * id_to_rank_prev[k]

    def calculate_weight(self, j, k):
        """
        calculates the weight each page gives to another page in 
        an xml based on what pages link to each other 
        parameters: a page and the other page to which the first 
        page may or may not link
        return: the calculated weight that the first parameter 
        gives to the secondcd
        """
        n = len(self.id_to_title)
        nj = len(self.id_to_other_pages[j])
        new_k = self.id_to_title[k].lower()
        
        if nj == 1: #and nj in self.id_to_other_pages:
            popped = self.id_to_other_pages[j].pop()
            if self.id_to_title[j].lower() != popped:
                self.id_to_other_pages[j].add(popped)
        
        nj = len(self.id_to_other_pages[j])

        if self.id_to_title[j].lower() in self.id_to_other_pages[j]:
            nj = nj - 1

        if j == k:
            weight = 0.15/n
        elif new_k in self.id_to_other_pages[j]:
            weight = 0.15/n + (0.85/nj)
        elif self.id_to_other_pages[j] == set():
            weight = 0.15/n + (0.85/(n - 1))
        elif new_k not in self.id_to_other_pages[j]:
            weight = 0.15/n
        return weight
        
    def calculate_distance(self, r_prev):
        '''
        calculates the distance between two calculated page ranks 
        which can be used to determine if the values are close to 
        converging and therefore more accurate
        parameters: the dictionary to store the second-most recently 
        calculated rank
        '''
        distances = 0.0
        for id in self.id_to_title:
            distances += (r_prev[id]-self.id_to_rank[id])**2
        return math.sqrt(distances)

'''
the main method for the indexer class that takes in the file paths entered 
by the user to fill with the data calculated with the contents of the wiki
'''
if __name__ == "__main__":
    try:
        if (len(sys.argv) - 1) == 4:
            Indexer(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print("Invalid input")
    except FileNotFoundError as e:
        print("File paths are invalid")
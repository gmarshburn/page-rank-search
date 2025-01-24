import file_io
import sys
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

class Querier:
    def __init__(self, pagerank, titles_path: str, docs_path: str, words_path: str):
        '''
        initialiazes the querier and reads all the information from the three 
        files created in the indexer to fill in the dictinoaries and runs 
        them against the user's inputted query
        parameters: the file path for the file that stores the titles of each 
        page in the wiki, the file path that stores the words in each page and 
        their associated relevance, and the file path that stores the pagerank 
        calculation for each page in the wiki
        '''
        self.id_to_title = {}
        self.word_to_relevance = {}
        self.id_to_rank = {}

        file_io.read_title_file(titles_path, self.id_to_title)
        file_io.read_docs_file(docs_path, self.id_to_rank)
        file_io.read_words_file(words_path, self.word_to_relevance)
        self.parsed_query = []
        self.pagerank = pagerank

    def query(self, input_query):
        '''
        finds the most relevant pages in the xml 
        in relation to the user inputted query
        parameter: the user inputted query
        '''
        self.parse_query(input_query)

        id_to_relevance = {}

        for word in self.parsed_query:
            if len(self.parsed_query) != 1:
                if word in self.word_to_relevance:
                    self.return_results(id_to_relevance, word)
            else:
                if word in self.word_to_relevance:
                    self.return_results(id_to_relevance, word)
                else:
                    id_to_relevance.clear()
                    self.parsed_query.clear()
                    ("Nothing related to your search. Please enter a different query.")

    def return_results(self, id_to_relevance, word):
        for id in self.id_to_title:
            id_to_relevance[id] = 0
            if id in self.word_to_relevance[word]:
                if self.pagerank:
                    id_to_relevance[id] += self.word_to_relevance[word][id] + self.id_to_rank[id]
                else:
                    id_to_relevance[id] += self.word_to_relevance[word][id]

        total_relevance = list(id_to_relevance.keys())
        total_relevance.sort(key = lambda x : id_to_relevance[x], reverse = True)
        title_relevance = []
        for id in total_relevance:
            title_relevance.append(self.id_to_title[id])
        if len(self.id_to_title) < 10:
            print(title_relevance)
        else:
            print("Top 10 Results: ", title_relevance[0], ", ", title_relevance[1], ", ", title_relevance[2], \
                ", ", title_relevance[3], ", ", title_relevance[4], ", ", title_relevance[5], ", ", \
                title_relevance[6], ", ", title_relevance[7], ", ", title_relevance[8], ", and ", \
                title_relevance[9])
            
        id_to_relevance.clear()
        self.parsed_query.clear()

    def parse_query(self, input_query):
        print("parsing query")
        '''
        tokenizes, stops, and stems the user's inputted query
        parameters: the user's inputted query
        '''
        STOP_WORDS = set(stopwords.words('english'))
        nltk_test = PorterStemmer()

        n_regex = '''\[\[[^\[]+?\]\]|[a-zA-Z0-9]+'[a-zA-Z0-9]+|[a-zA-Z0-9]+'''
        parsed_words_list = re.findall(n_regex, input_query)

        for word in parsed_words_list:
            if word not in STOP_WORDS:
                stemmed_word = nltk_test.stem(word)
                self.parsed_query.append(stemmed_word)

    def repl(self):
        while True:
            S = input("Input a query: ")
            if S == ":quit":
                break
            q.query(S.lower())
        

'''
the main method for the querier class that sets 
up the REPL and prompts the user for input
'''
if __name__ == "__main__":
    try:
        if (len(sys.argv) - 1) == 4:
            if sys.argv[1] == "--pagerank":
                q = Querier(True, sys.argv[2], sys.argv[3], sys.argv[4])
                q.repl()
            else:
                print("Invalid input")
        elif (len(sys.argv) - 1) == 3:
            q = Querier(False, sys.argv[1], sys.argv[2], sys.argv[3])
            print("2")
            q.repl()
        else:
            print("Invalid input")
    except FileNotFoundError as e:
        print("File paths are invalid")
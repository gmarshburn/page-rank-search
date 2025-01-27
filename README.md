# page-rank-search-engine
This project was completed as a partnered project. We worked collaboratively on all aspects of this project, discussing implementations and debugging issues together. I was responsible for more of the parsing, while my partner worked on more parts of the querier, but we both worked together in some form to complete all parts of the project.

# Instruction for use:
Upon running the program for the first time, the user will be prompted to enter the xml file through which they would like the search and the three empty text file to which intermediate information will be written. Once these are inputted, the program will index the xml file, calculating different measures based on the contents of the xml file that will be used to return the most pertinent and reliable information to the user. After the xml file is indexed, the user will be prompted to enter a query on which to base their search through the xml file, as well as whether they want to include pagerank calculations in the determination of their results. This query and the previously calculated data will be used to return the most pertinent and reliable pages of the xml file (either with or without pagerank) to the user.

# Design:
Once the file through which to search and the files to which to write the calculated data are inputted, the indexer runs through each page in the xml file. Then for each page, each word is covered. This large loop is where all of the data gathering and storing occurs for the entire xml file. Using a regex equation, each page is parsed for its text and title, tokenized for only pure text, stopped to remove uninformative words, and stemmed to retain only the root of each word. Information such as the id and title of each page, the pages on which words appear and their frequency, and the pages (if any) to which each page links is stored. After this loop, the relevance of each word in each page in the xml file and the pagerank for each page based on which page link to which other pages are calculated. Relevance calculations utilize each word's frequency and the most frequent word of each page. Pagerank uses the weight that one page gives to another based on the other links in each page (and therefore each page's reliability) to determine which pages are the most reliable. With these two calculations completed and stored along witht he title of each page in the xml file, the user will be prompted to enter a query with which to search through the xml, as well as whether they want to include pagerank calculations in the determination of their results. Once inputted, the query will be tokenized, stopped, and stemmed to be easily comparable to the text of the xml that has also undergone this process. The relevance of each word in the query will then be found by getting the relevance for each word in the query for each dpage in the xml and adding all relevances for each pages together so each page has one relevance score in relation to the entire query. At this point pagerank would also be added to the relevance for each page to the query if the user wants to include it. All pages will then be sorted on this number and the top ten results will be returned to the user. If there are less than ten pages in the xml, all pages will be returned in the order that was determined by the relevance (and possibly pagerank) calculations for the inputted query.

# System tests:
We ran each wiki, including our own xml file, with the following inputs and outputs for pagerank:

Gatsby: input - gatsby, output - ['the great gatsby', 'f. scott fitzgerald', 'nick carraway', 'how to travel to the french riviera', 'music: jazz age']

SmallWiki: input - history, output - Top 10 Results:  rome ,  germany ,  outline of germany ,  united states ,  anachronism ,  parachronism ,  transformation of culture ,  outline of history ,  list of historical classifications , and  index of history articles

SmallWiki: input - comparative literature, output - Top 10 Results:  carthage ,  rome ,  history ,  war ,  united states ,  military history ,  civilian casualty ratio ,  loss exchange ratio ,  philosophy of war , and  anachronism

MediumWiki: input - history, output - Top 10 Results:  pakistan ,  netherlands ,  neolithic ,  hinduism ,  portugal ,  nazi germany ,  planet ,  hong kong ,  norway , and  monarch

BigWiki: input - tennis, output - Top 10 Results:  india ,  london ,  paris ,  pakistan ,  hong kong ,  morocco ,  lead ,  moscow ,  fifa , and  luxembourg

# Unit tests: 
We tested each method in the indexer to make sure each function ran correctly individually. We compared the outputted results to a string htat contained edge cases for words and links to make sure all were being parsed and used for calculation correctly. We also included the emaxples provided to use to ensure our calculation for tf, idf, and pagerank were correct.

# Known bugs and features:
There are no known bugs in our program. We parse the SmallWiki indexes in 5 seconds, the MedWiki in 1:07, the BigWiki in 6:43, and our querier returns correct results.

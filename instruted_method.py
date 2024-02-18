#importing neceassary libraries
import pandas as pd
from pathlib import Path
from nltk.tokenize import word_tokenize,sent_tokenize
import pyphen
import re,nltk
from nltk.corpus import stopwords
import string
import warnings
import requests
from bs4 import BeautifulSoup as bs
#ignoring all warings
warnings.filterwarnings("ignore")

#Reading the excel file for getting URL
df=pd.read_excel("Output Data Structure.xlsx")
#function copied from internet for finding the syllabels
def count_syllables(word):
    dic = pyphen.Pyphen(lang='en_US')
    return len(dic.inserted(word).split('-'))
#for reading all the stops in all text files first i'm trying fetch their path
input_dir=Path.cwd() / 'stop_words'
files=list(input_dir.glob("*.txt*"))
#opening every text file and appending to list
stop_words=[]
for i in files:    
    with open(Path.cwd() / "stop_words" / str(i).split('\\')[8], 'r', encoding='utf-8', errors='ignore') as stopfile:
        stop_word=stopfile.readlines()
        for line in stop_word:
            stop_words.append(line.strip())
#appending all postive word to list
with open('positive-words.txt', 'r') as file:
    data = file.readlines()
    positive_words = [line.strip() for line in data] 
#appending all negative word to list
with open('negative-words.txt', 'r', encoding='utf-8', errors='ignore') as file1:
    data = file1.readlines()
    negative_words = [line.strip() for line in data]

z=0
for i in df['URL']:
  if i=='https://insights.blackcoffer.com/how-neural-networks-can-be-applied-in-various-areas-in-the-future/':
    pass
  else:
    #open in every url in excel file
    urlclient=requests.get(i)
    #beautifying scrapped text
    insights_html=bs(urlclient.text,'html')
    #searching for articles
    paragraphs=insights_html.find_all(  {
      'p': {'class': 'has-text-align-left'},
      'p':{'class':None}})
    #storing the text into files
    file=open(f"{Path.cwd()}\\textfiles\\{i.split('/')[3]}.txt",'a',encoding='utf-8', errors='ignore')
  
    for j in paragraphs:
      file.write(j.text)

    file.close()
    string_list_list = [word_tokenize((tag.text)) for tag in paragraphs]
    #tokenizing the words by using nltk module
    token_words = [sentence for sublist in string_list_list for sentence in sublist]
    #first intializing the empty list for filtered words
    #assiging values for postive score and negative to 0 so that when i iterate i can change them
    filtered_words=[]
    postive_score=0
    negative_score=0
    #for clearing punctuations in tokenized words using build in punctuations of strings
    punct_stopwords = list(string.punctuation)
    for word in token_words:
      #appending the words to filtered words if they are not in stopwords and in string punctuations
      if word not in stop_words and word not in punct_stopwords:
        filtered_words.append(word)
    total_char=0
    #fetching the word count
    len_filter_word = len(filtered_words)
    for word in filtered_words:
      #trying to find the sum of all char in every word
      total_char += len(word)
      if word in positive_words:
        #if the word is postive word im increasing postive score by 1
        postive_score+=1
      elif word in negative_words:
        #if the word is negative word im increasing negative score by 1
        negative_score+=1
    #finding the polarity score
    polarity_score = (postive_score-negative_score)/((postive_score + negative_score)+0.000001)
    #calculating the subjective score
    subjective_score = (postive_score + negative_score)/((len_filter_word)+0.000001)
    token_sent_lists=[sent_tokenize(i.text) for i in paragraphs]
    #tokenizing the sentances in total text scraped
    token_sents = [sentence for sublist in token_sent_lists for sentence in sublist]
    #intializing complex words list and syllables_count to 0 so that i can modify them when iterate throught loop of filtered words
    complex_words=[]
    syllable_counts = 0

    for word in filtered_words:
      if count_syllables(word)>1:
        #by using the pre defined function im trying to find the word is complex or not baes on number of syllebels in it and finding syllabel count same to decrease computation effort
        complex_words.append(word)
        syllable_counts+=count_syllables(word)
      else:
        syllable_counts+=count_syllables(word)
    #claculating the necessary values as mentioned in the ouput data structure file
    len_complex_word=len(complex_words)
    avg_sent_len = float(len_filter_word)/len(token_sents)
    percnt_cmplx_wrds=len_complex_word/len_filter_word
    fog_index=0.4*(avg_sent_len + percnt_cmplx_wrds)
    avg_no_wrds_per_sent = avg_sent_len
    word_count = len_filter_word
    avg_sylabul_per_word = syllable_counts/len_filter_word
    pos_tags = nltk.pos_tag(filtered_words)
    personal_pronouns = [word for word, pos in pos_tags if pos == 'PRP']
    no_of_prp = len(personal_pronouns)
    avg_word_len = total_char/len_filter_word
    #updating the dataframe with obtained values for every URL
    new_values=[df['URL_ID'][z],df['URL'][z],postive_score,negative_score,polarity_score,subjective_score,avg_sent_len,percnt_cmplx_wrds,fog_index,avg_no_wrds_per_sent,len_complex_word,len_filter_word,avg_sylabul_per_word,no_of_prp,avg_word_len] 
    for col, value in zip(df.columns, new_values):
        df[col][z] = value
    #print(postive_score,negative_score,polarity_score,subjective_score,avg_sent_len,percnt_cmplx_wrds,fog_index,avg_no_wrds_per_sent,len_complex_word,len_filter_word,avg_sylabul_per_word,no_of_prp,avg_word_len)
    z+=1
#converting the data frame into excel file
df.to_excel('instructed_method_output.xlsx', index=False) 
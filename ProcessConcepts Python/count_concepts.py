import json
import nltk
from nltk.stem import WordNetLemmatizer 
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('omw-1.4')

"""
Count all IVD concepts in B.Maiers Textkorpus
"""
# extracted ivd concepts
ivd_entries = []
# path to a jsonl file with annotated texts
path_to_annotated = r"C:\\Users\\z003svfy\Desktop\\NLP\Daten\\Textkorpus\\Annotiert\\textkorpus_doccano.jsonl"


lemmatizer = WordNetLemmatizer()
def lemmatize(concept: str):
  """
  tokenize and lemmatize the given NE concept
  and get the result as a tuple(concept, [lemmas])
  """  
  word_list = nltk.word_tokenize(concept)
  lemmatized_output = [lemmatizer.lemmatize(w) for w in word_list]
  return (concept, lemmatized_output)

def find_substring(text: str, start: int, end: int) -> str:
  """
  Find a substring located in the text 
  between start and end index
  """
  substring = ""  
  for x in range(start, end):    
    substring += text[x]  
  return substring 

#start point
with open(path_to_annotated, encoding='utf-8') as f:  
  for line in f:         
    line_dict = json.loads(line)
    #get labels
    labels = line_dict["label"]
    text = line_dict["data"]    
    #find IVD
    for label in labels:
      start = label[0]      
      end = label[1]     
      concept = find_substring(text, start, end)
      #normalize
      (ne, lemmas) = lemmatize(concept)
      #save them in dictionary
      if ne not in ivd_entries:
        print(ne)
        ivd_entries.append(ne)


print(len(ivd_entries))    

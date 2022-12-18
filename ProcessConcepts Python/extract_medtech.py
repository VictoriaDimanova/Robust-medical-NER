from os import listdir
from os.path import isfile, join
import json
import os

"""
Extract all IVD concepts from training data and test data.
These concepts are collected for future validation of the extracted
data through a domain expert.
Count them.
"""
#determine all files with test data
test_data_path = r'D:\Workspace\\gui\storage\\test data'
all_test_data = [os.path.join(path, name) for path, subdirs, files in os.walk(test_data_path) for name in files]
extracted_test_data = {}

#count how many concepts are in files
test_counter = 0
train_counter = 0

#determine all files with training data
mypath = r"D:\Workspace\\ProcessConcepts\\ProcessValidationHtml\\output"
all_files = [os.path.join(path, name) for path, subdirs, files in os.walk(mypath) for name in files]
#print(all_files)

#file with extracted NEs
extracted_result = 'C:\\Users\\z003svfy\Desktop\\extracted_validated_result.json'
#extracted_tests =  'C:\\Users\\z003svfy\Desktop\\extracted_test_data.json'
extracted = {}

#extract test data 
#for td in all_test_data:
#    if td.endswith("all_data.json"):
#        continue
#    test_vals = []
#    with open(td, encoding="utf-8") as file:        
#        js = json.load(file)
        #print(js)
#        for item in js:
#            if "label" not in item:
#                continue
#            labels = item["label"]
#            for lab in labels:
#                concept = lab["text"]
#                test_vals.append(concept)  

                #count concepts in train data 
 #               train_counter += 1                
#        file_name = td.split("\\")[-1]
 #       extracted_test_data[file_name] = test_vals
#print(extracted_test_data)

#write in file
#with open(extracted_tests, 'w') as outfile:
#    json.dump(extracted_test_data, outfile)


#extract training data 
for f in all_files:
    current_vals = []    
    with open(f, encoding="utf-8") as file:        
        js = json.load(file)
        for item in js:
            annot = item["annotations"][0]
            result = annot["result"]
            if result == []:
                continue
            for item in result:
                val = item["value"]
                concept = val["text"]
                current_vals.append(concept)
                #count concepts in test data 
                test_counter += 1  
        file_name = f.split("\\")[-1]
        extracted[file_name] = current_vals

#print("train concepts: ", train_counter )
print("test concepts: ", test_counter )
#write in file
#with open(extracted_result, 'w') as outfile:
 #   json.dump(extracted, outfile)

    

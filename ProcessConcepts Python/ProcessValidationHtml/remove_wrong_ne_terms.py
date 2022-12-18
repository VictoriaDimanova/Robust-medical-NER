'''
TRAINING/TEST DATA PROCESSING
COMMENT NOT NEEDED CODE
Traverse all annotated text corpus data and remove NEs that belong
to categories 3 and 4 after validation 
3: not IVD
4: context needed
'''

import json
import os

#read all NEs of category 3 and 4 from file created by extract_values.py
with open('D:\Workspace\ProcessConcepts\ivd_categories_test.txt', 'r', encoding="utf8") as f:
    data = json.load(f)
    cat3 = data["3"]
    cat4 = data["4"]
    cat3.extend(cat4)
    print(len(cat3))

#make a false IVD-Candidates
stop_words = []
for word in cat3:
    stop_words.append(word.lower().strip())
    if word.strip()[-1] == "s":
        #add singular form
        stop_words.append(word.lower().strip()[:-1])
    else:
        #add plural form
        stop_words.append(word.lower().strip() + "s")
print(stop_words)   

#mypath = r"C:\\Users\\z003svfy\Desktop\\NLP\\completely annotated"
mypath = r"D:\Workspace\\gui\\storage\\test data"
all_files = [os.path.join(path, name) for path, subdirs, files in os.walk(mypath) for name in files]   

#extract training data data 
for td in all_files:  
    print(td)
    if td.endswith("all_data.json"):
        continue 
    with open(td, encoding="utf-8") as file:         
        corrected_file = []       
        js = json.load(file)  
        #TEST DATA
        for item in js:
            if "label" not in item.keys(): 
                corrected_file.append(item)
                continue
            new_item = item
            new_labels = []
            labels = item["label"]            
            for lab in labels:                          
                text = lab["text"]
                if text.strip().lower() not in stop_words:
                    new_labels.append(lab)
                    new_item["label"] = new_labels
            corrected_file.append(new_item)


        #TRAIN DATA      
        #json item
        for item in js: #for train data        
            annots = item["annotations"]   #for train data
            corrected_annots = []   #for train data          
            for annot_item in annots:                                          
                if "result" not in annot_item.keys():
                    corrected_annots.append(annot_item)
                    continue
                new_item = annot_item
                #delete old result
                #del new_item["result"]
                results = annot_item["result"]    
                new_results = []
                for res in results:
                    value = res["value"]                   
                    concept = value["text"]
                   # print(concept)
                    if concept.strip().lower() not in stop_words:
                        new_results.append(res)
                       # print("concept clear")
                #add new result if it exists
                if len(new_results) > 0:
                    new_item["result"] = new_results
                else:
                    new_item["result"] = []

                #add corrected json-item  to json   
                corrected_annots.append(new_item)
            item["annotations"] = corrected_annots
            corrected_file.append(item)
         
        file_name = "D:\Workspace\ProcessConcepts\ProcessValidationHtml\output\cleaned_" + td.split("\\")[-1]
        #file_name = "D:\\Workspace\\gui\\storage\\validated_test_data_" + td.split("\\")[-1]

        #write corrected json
        with open(file_name, 'w') as outfile:
            json.dump(corrected_file, outfile)
    
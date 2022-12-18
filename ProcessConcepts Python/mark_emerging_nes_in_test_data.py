from os import listdir
from os.path import isfile, join
import json
import os
from rapidfuzz import fuzz

"""
Check if recognized NEs in test data are emerging NE,
that is: whether they were noted in medical publications 
before they were entered in official device lists.

#get NEs in each test data text from the extracted_test_data.json.
#check which NEs are to find in device dictionaries created by B.Maier
#if an entry is found in the dictionary, publication date of the medical article with 
#the the enty date for the given concept in the dictionary 
#save info about the emerging NE in the dictionary {"publication Id" : [list of emerging NEs]}
"""


def load_dictionaries():        
    storage = "D:\Workspace\gui\storage\\"     
    voc_510k = json.load(open(storage + "med_tech_510k.json","r",encoding="utf8"))         
    voc_PMA = json.load(open(storage + "med_tech_PMA.json","r",encoding="utf8"))         
    voc_estab_reg = json.load(open(storage + "med_tech_estab_reg.json","r",encoding="utf8"))
    dict_510k_PMA = voc_510k | voc_PMA #merge dictionaries
    return dict_510k_PMA, voc_estab_reg

def load_json(path_to_file):
    """
    load json-file with extracted entities
    """
    with open(path_to_file, encoding="utf-8") as file: 
        return json.load(file)

def finde_fuzzy_device(entity_text, dict_510k_PMA, dict_estab_reg):
    """
    Compute similarity of text tokens and entries
    of PMA and 510k dictionaries
    """
    return_dict = {}
    # Abgelichen mit PMA und 510k
    for key, values in dict_510k_PMA.items():
        ratio = fuzz.token_ratio(entity_text, values[1])
        gemeinsame = len(text_Schnittmenge(entity_text, values[1]))
        # Ratio zwischen 50 und 80: 2 gemeinsame Token genügen
        if ratio > 50:
            #print("ratio > 50: ", entity_text, values[1])
            if ratio > 80 or gemeinsame >= 2:
                return_dict[key] = [values[0], values[1], ratio, values[2]]  
                #print("ratio > 80 and gemeinsame >= 2:  entity_text: ", entity_text, "values[1]: ", values[1])

    # Abgelichen mit Establishment Registration
    for op_nr, key_vals in dict_estab_reg.items():
        for key_val, values in key_vals.items():
            firm_name = values['firm_name']
            date = values['date'].split('/')[2]
            if 'prop_names' in values:
                for prop_name in values['prop_names']:
                    prop_key = op_nr + "#" + str(values['prop_names'].index(prop_name))
                    ratio = fuzz.token_ratio(entity_text, prop_name)
                    gemeinsame = len(text_Schnittmenge(entity_text, prop_name))
                    # Ratio zwischen 50 und 80: 2 gemeinsame Token genügen
                    if ratio > 50:
                        if ratio > 80 or gemeinsame >= 2:
                            #print("ratio > 80 and gemeinsame >= 2:  entity_text: ", entity_text, "VS. values[1]: ", prop_name, "firm_name: ", firm_name)
                            return_dict[prop_key] = [firm_name, prop_name, ratio, date]
    return return_dict  

def text_Schnittmenge(text1, text2):
        """
        Finden von  gemeinsamen Wörtern in zwei Texten
        """
        l1 = text1.lower().split(' ')
        l2 = text2.lower().split(' ')
        return_liste = list((set(l1) & set(l2)))
        return return_liste


emerging_nes = {}
#start point
dict_510k_PMA, voc_estab_reg = load_dictionaries()
paper_years = load_json('D:\Workspace\gui\storage\pmid_year_map.json')
test_nes = load_json('C:\\Users\\z003svfy\Desktop\\extracted_test_data.json')
    #print(js)
for nes_key, nes_items in test_nes.items():
    #extract test data 
    test_vals = []
    if nes_key != "t30011310.json":
        continue
    pubmed_id = nes_key.replace("t", "").replace(".json", "")
    paper_year = paper_years[pubmed_id]
    for item in nes_items:
        fuzzy_device = finde_fuzzy_device(item, dict_510k_PMA, voc_estab_reg)
        if len(fuzzy_device) == 0:
            continue
        entity_erkannt = False
        for key, values in fuzzy_device.items():
            device = fuzzy_device[key][1]            
            applicant = fuzzy_device[key][0].replace(',','')     
           # print("device: ", device, "applicant: ", applicant, "VS item: ", item)       
            jahr = fuzzy_device[key][3]           
            device_applicant = text_Schnittmenge(item.lower(), applicant.lower())                     
            if len(device_applicant) == 0:
                continue                        
            # Entity muss mehr Wörter enthalten, 
            # als gemeinsame mit Herstellername   
            entity_erkannt = True
            if int(jahr) > int(paper_year): 
                print("Datei: ", nes_key)
                print("Hersteller: ", applicant)
                print("Gerät: ", device)
                print("im Text: ", item)
                print("Jahr Vokabulareintrag: ", jahr, "Jahr Publikation: ", paper_year)
                print("-----------")
                test_vals.append(item)
                #print(item, jahr, paper_year)
                break       
    emerging_nes[nes_key] = test_vals
print(emerging_nes)

       
    

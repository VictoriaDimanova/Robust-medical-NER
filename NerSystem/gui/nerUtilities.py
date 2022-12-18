from rapidfuzz import fuzz
from spacy.tokens import Span
from spacy.scorer import Scorer
from spacy.training.example import Example
from spacy.util import filter_spans
import logging

class NerUtilities:
    """
    Utils
    """
    #region init

    def init(self, voc_510k, voc_PMA, voc_estab_reg):       
        self.dict_510k_PMA = voc_510k | voc_PMA
        self.dict_estab_reg = voc_estab_reg  
        self.wrong_concepts = [] 
        self.false_pos = []
        self.false_neg=[]
        self.remove_wrong_concepts = ""    
        self.is_strict_eval = ""      
        self.is_ener = ""  
        Span.set_extension('jahr', default=0)   
        logging.basicConfig(filename='NerSystem.log', format='%(asctime)s %(message)s', filemode='a')    
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
    #endregion init

    #region NER evaluation    
    def __evaluate(self, model, text, annot, year):
        """
        evaluate the model
        """
        scorer = Scorer(model)               
        example = [] 
        pred = self.run_ner(model, text, year) 
            
        if self.is_strict_eval == "false":   
            #adjust boundaries        
            updated_ents = []           
            #find same items in output
            to_change = []
            for ent in pred.ents:     
                is_same_concept = False           
                for item in annot:
                    is_same_concept = self.__is_same_concept(ent.start_char, ent.end_char, item[0], item[1])
                    if is_same_concept == True:
                        change = (ent, item)                        
                        to_change.append(change)                        
                        break                    
                    else:
                        is_same_concept = self.__is_same_concept(item[0], item[1], ent.start_char, ent.end_char)
                        if is_same_concept == True:
                            change = (ent, item)  
                            to_change.append(change)
                            break
                #false positives  
                if is_same_concept == False and ent not in updated_ents:                
                    updated_ents.append(ent)   

            #substitute items with moved boundaries through the 
            # items with boundaries like in the gold standard     
            for change in to_change:
                new_vals = change[1]
                new_ent = pred.char_span(
                    new_vals[0], 
                    new_vals[1], 
                    label = new_vals[2],
                    alignment_mode="contract")  
                if new_ent not in updated_ents:
                    updated_ents.append(new_ent)
            
            #update document entities
            pred.ents = updated_ents 
            print("FOUND: \n", updated_ents)
            print("ANNOT: \n", annot)
                    
        #score results         
        item = Example.from_dict(pred, {"entities":annot})        
        example.append(item)
        scores = scorer.score(example)
        print(scores)       
        return pred, scores

    
    def run_eval(self, json_content, model, year:int):
        """
        find all concepts in the evaluation text 
        using a method when strict boundaries of 
        NEs are ignored e.g culture medium = medium
        return: a list of found concepts, a list of given concepts (gold standard)
        """      
        eval_text = self.__extract_text(json_content)       
        labels = self.__extract_labels(json_content)        
        doc, results =  self.__evaluate(model, eval_text, labels, year)     
        return (doc, results)   

    def __is_same_concept(self, out_start, out_end, st_start, st_end) -> bool:        
        """
        check if the given boundaries of two substrings overlap. 
        If yes: return true, otherwise: false
        """
        if out_start >= st_start and out_start <= st_end: 
            return True
        if out_end >= st_start and out_end <= st_end:
            return True
        if out_start <= st_start and out_end >= st_end:
            return True
        if out_start >= st_start and out_end <= st_end:
            return True
        return False       
    
    def __extract_text(self, json_dict) -> str:
        pubmed_text = ""
        for item in reversed(json_dict):            
            pubmed_text += item["text"]
            pubmed_text += "\n"
        return pubmed_text

    def __extract_labels(self, json_dict):
        """
        extract labels in form (start_index, end_index, (text), label)
        """
        labels = []
        annotation_text = []
        length = 0
        self.logger.debug("Annotations:")
        for item in reversed(json_dict):
            if "label" in item:
                item_labels = item["label"]
                for lab in item_labels:
                    annotation_text.append(lab["text"])                    
                    start = lab["start"] + length
                    end = lab["end"] + length
                    label = lab["labels"][0]
                    next = (start, end, label)
                    labels.append(next)
            length += len(item["text"]) + 1  
        self.logger.debug(annotation_text)
        return labels

    #endregion NER evaluation

    #region NER with transformer
    def run_ner(self, nlp, text:str, year:int):   
        """
        determine NEs in a text
        """      
        content = self.__clean_text(text)
        doc = nlp(content) 

        #NER with the selected transformer model
        if doc == None:
            print("Something went wrong with NER")
            return doc

        #NER with the knowledge source
        if self.remove_wrong_concepts == "true":
            doc = self.sort_out_wrong_concepts(doc)             
        
        if doc == None:
            print("Something went wrong with NER")
            return doc

        #eNER
        if self.is_ener == "true":
            #determine entities year
            self.find_ents_in_dictionaries(doc)
            #determine eNEs
            self.ener(doc, year)

        return doc 
       
    def __clean_text(self, text:str)-> str:
        # characters in texts to remove
        noise = ["\x80", "\x89", "±", "Â", "â", "Î","¤", 
         "\x93", "\x97", "Ã", "\x88", "\x92",
         "", "", "", "", "", "", "", "",
          "", "¶", "³", "®", "º",  "¼", "Î",
          "±", "", "Â", "²", "¤", "¥", "", "" ]
        for char in noise:
            text = text.replace(char, "")
        return text   

    #endregion NER with transformer

    #region NER with knowledge source
    def sort_out_wrong_concepts(self, doc):
        """
        doc: an object created by Spacy, where all recognized entities are saved       
        ---
        get recognized NEs and sort out NEs that contains substrings given in the 
        list of wrong concepts
        """ 
        if doc == None:
            return doc

        updated_ents = [] 
        for ent in doc.ents:
            to_remove = False
            ent_string = ent.text            
            for substring in self.wrong_concepts:                
                if(substring.lower() in ent_string.lower()):
                    to_remove = True
                    break
            if to_remove == False:
                new_ent = Span(ent.doc, ent.start, ent.end, label=ent.label)
                updated_ents.append(new_ent)  
        doc.ents = updated_ents
        return doc

    #### region rule-based NER inherited from B.Maier and adjusted when needed #####  

    #pattern-matching NER   
    def find_ents_in_dictionaries(self, doc):
        """
        Find recognized entities in dictionaries and try to determine entity year of
        production. 
        """
        next_applicant = False
        for index, ent in enumerate(doc.ents):              
            # Falls in der letzten Iteration diese Entity als Applicant erkannt wurde
            if next_applicant: 
                next_applicant = False
                continue
            # Entities müssen aus min. 2 Token bestehen (bessere Precision)
            if len(ent.text.split(' ')) > 1:
                fuzzy_device = self.finde_fuzzy_device(ent.text)
                if len(fuzzy_device) != 0:
                    # Entity Markenname (Fuzzy) enthält Herstellername
                    entity_erkannt = False
                    for key, values in fuzzy_device.items():
                        device = fuzzy_device[key][1]
                        applicant = fuzzy_device[key][0].replace(',','')
                        jahr = fuzzy_device[key][3]
                        device_applicant = self.text_Schnittmenge(ent.text.lower(), applicant.lower())
                        if len(device_applicant) > 0:                            
                            # Entity muss mehr Wörter enthalten, 
                            # als gemeinsame mit Herstellername                           
                            ent._.jahr = jahr                            
                            entity_erkannt = True
                            print(ent)
                            break
                    if entity_erkannt: 
                        continue
                # Entity Markenname (Fuzzy), gefolgt von Entity Herstellername (Fuzzy)            
                if index == (len(doc.ents) - 1): break       

                ent_next = doc.ents[index + 1]
                fuzzy_applicant = self.finde_fuzzy_device(ent_next.text)         
                if len(fuzzy_applicant) != 0:
                    if 0 < (ent_next.start - ent.end) <= 1:
                        for key, values in fuzzy_device.items():
                            key_applicant = key.split('#')[0]
                            if key_applicant in fuzzy_applicant:
                                device = fuzzy_device[key][1]
                                applicant = fuzzy_applicant[key_applicant][0]
                                jahr = fuzzy_device[key][3]
                                ent._.jahr = jahr                                
                                next_applicant = True
                                break    
   
    def finde_fuzzy_device(self, entity_text):
        """
        Compute similarity of text tokens and entries
         of PMA and 510k dictionaries
        """
        return_dict = {}
        # Abgelichen mit PMA und 510k
        for key, values in self.dict_510k_PMA.items():
            ratio = fuzz.token_ratio(entity_text, values[1])
            gemeinsame = len(self.text_Schnittmenge(entity_text, values[1]))
            # Ratio zwischen 50 und 80: 2 gemeinsame Token genügen
            if ratio > 50:
                if ratio > 80 or gemeinsame >= 2:
                    return_dict[key] = [values[0], values[1], ratio, values[2]]  

        # Abgelichen mit Establishment Registration
        for op_nr, key_vals in self.dict_estab_reg.items():
            for key_val, values in key_vals.items():
                firm_name = values['firm_name']
                date = values['date'].split('/')[2]
                if 'prop_names' in values:
                    for prop_name in values['prop_names']:
                        prop_key = op_nr + "#" + str(values['prop_names'].index(prop_name))
                        ratio = fuzz.token_ratio(entity_text, prop_name)
                        gemeinsame = len(self.text_Schnittmenge(entity_text, prop_name))
                        # Ratio zwischen 50 und 80: 2 gemeinsame Token genügen
                        if ratio > 50:
                            if ratio > 80 or gemeinsame >= 2:
                                return_dict[prop_key] = [firm_name, prop_name, ratio, date]
        return return_dict  

    def text_Schnittmenge(self, text1, text2):
        """
        Finden von  gemeinsamen Wörtern in zwei Texten
        """
        l1 = text1.lower().split(' ')
        l2 = text2.lower().split(' ')
        return_liste = list((set(l1) & set(l2)))
        return return_liste
    #endregion NER with knowledge source
    #eNER
    def ener(self, doc, jahr):
        """
        compare an publication year
        with the year of the entity
        and assign a new label to the entity
        if necessary
        """   
        updated_ents = []        
        for entity in doc.ents:
            print(entity)
            print("publication year: " + str(jahr))
            print("entity year: " + str(entity._.jahr))
            if int(jahr) < int(entity._.jahr):
                new_ent = Span(entity.doc, entity.start, entity.end, label="eMedTech")   
            else:
                new_ent = entity
            updated_ents.append(new_ent)
        doc.ents = updated_ents
        


         










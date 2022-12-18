import json
import spacy
import glob
from spacy import displacy
import datetime
import re


class Model:  

    #region read

    def get_all_texts(self, path):
        """
        get all json-files in the given directory
        """
        directory = path.replace("all_data.json", "*.json")
       
        return glob.glob(directory)


    def load_dictionaries(self):        
        storage = self.read_settings("storage")       
        voc_510k = json.load(open(storage + "med_tech_510k.json","r",encoding="utf8"))         
        voc_PMA = json.load(open(storage + "med_tech_PMA.json","r",encoding="utf8"))         
        voc_estab_reg = json.load(open(storage + "med_tech_estab_reg.json","r",encoding="utf8"))
        return voc_510k, voc_PMA, voc_estab_reg

    def load_model(self):
        model_path = self.read_settings("model_path")
        return spacy.load(model_path)  

    def load_content(self, json_file):
        """
        Read a pubmed text from json-file with a test data
        """
        pubmed_text = ""
        with open(json_file, encoding="utf8") as f:
            asDict = json.load(f)       
            return asDict 
     
    def read_settings(self, parameter:str):
        """
        read value of a definite parameter 
        """
        with open("settings.json", encoding="utf8") as f:
            # reading from file
            data = json.load(f)
            if parameter in data:                
                return data[parameter]
            else:
                print("Failed to read parameter.")
                return "error"
    
    def load_wrong_concepts(self):
        """
        load a dictonary of wrong concepts and
        return a list of all values
        """
        with open(".\storage\FilterOut.json", encoding="utf8") as f:
            # reading from file
            dictionary = json.load(f)
            vals = dictionary.values()
            return [item for sublist in vals for item in sublist]
            

    def determine_text_year(self, path:str):
        """
        Load a pmid_year-map and find the publishing year
        of the paper
        """            
        path = path.replace("\\", "/")
        file_name = path.split("/")[-1]
        file_name = re.sub("[^0-9]", "", file_name)
        print(file_name)
        with open(".\storage\pmid_year_map.json", encoding="utf8") as f:
            # reading from file
            data = json.load(f)
            if file_name in data.keys():
                print("filename: " + file_name)
                print(data[file_name])
                return data[file_name]
            else:
                print("file not in pmid_year map")
            return 0
        
    #region write

    def __create_html_header(self, total, med_tech, emed_tech, file_name):
        model_path = self.read_settings("model_path")
        model = model_path.split("\\")[2]
        remove_wrong_concepts = self.read_settings("remove_wrong_concepts")
        strict_eval = self.read_settings("is_strict_eval")
        header = """
        <head><title>NER Evaluation</title></head>
        <h1><b>Evaluation results</b></h1>
            <h3>File name:</h3>
                <h4 style="color:DodgerBlue;"> {} </h4>        
            <h3>Settings: </h3>            
                <h4 style="color:DodgerBlue;"> model [{}], remove wrong concepts [{}], strict evaluation [{}]</h4>
           
            <table style="width:100%">
                <tr>
                    <td></td>
                    <td><b>Precision (How many found items are relevant?)</b></td>
                    <td><b>Recall (How many relevant items are found?)</b></td>
                    <td><b>F1-Score<b></td>
                </tr>
                <tr>
                    <td><b>MedTech</b></td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td><b>Emerging MedTech</b></td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td><b>Total</b></td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            </table>   
        <h3>Tagged text:</h3>

        """.format(
            file_name, model, remove_wrong_concepts, strict_eval, 
            med_tech[0], med_tech[1], med_tech[2], 
            emed_tech[0], emed_tech[1], emed_tech[2], 
            total[0], total[1], total[2]
            )              
        return header


    def write_total_eval_html(self, medtech_scores, emedtech_scores, total_scores, counter):
        """
        medtech_scores: medTech Precision, Recall, F1-Score
        emedtech_scores: e_medTech Precision, Recall, F1-Score
        total_scores: medTech+e_medTech Precision, Recall, F1-Score
        counter: amount of evaluation texts
        ----------------
        write evaluation results for all documents 
        """       
        
        html = self.__create_eval_header(medtech_scores, emedtech_scores, total_scores, counter)    
        file_path = self.read_settings("result_path")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H.%M")
        file_name = "total_evaluation {}.html".format(now)
        #write in html file
        with open(file_path + file_name, "w", encoding="utf8") as f:
            f.write(html) 
        return file_path + file_name    

    def __create_eval_header(self, medtech_results, emedtech_results, total_results, counter):
        """
        create a header for a html file with total results
        """
        model_path = self.read_settings("model_path")
        model = model_path.split("\\")[2]
        remove_wrong_concepts = self.read_settings("remove_wrong_concepts")
        strict_eval = self.read_settings("is_strict_eval")
        
        mt_prec =  medtech_results[0]/counter
        mt_rec = medtech_results[1]/counter
        mt_f1 = 2 * mt_prec * mt_rec / (mt_prec + mt_rec)

        is_ener = self.read_settings("is_ener")
        if is_ener == "true":
            emt_prec =  emedtech_results[0]/counter
            emt_rec = emedtech_results[1]/counter
            emt_f1 = 2 * emt_prec * emt_rec / (emt_prec + emt_rec)
        else:
            emt_prec = "-"
            emt_rec = "-"
            emt_f1 = "-"

        total_prec = total_results[0]/counter
        total_rec = total_results[1]/counter
        total_f1 = 2 * total_prec * total_rec / (total_prec + total_rec)
        header = """
        <head><title>NER Evaluation</title></head>
        <h1><b>Evaluation results</b></h1>            
            <h3>Settings:</h3>
            <h4 style="color:DodgerBlue;"> model [{}], remove wrong concepts [{}], strict evaluation [{}]</h4>
            <table style="width:100%">
                <tr>
                    <td></td>
                    <td><b>Precision (How many found items are relevant?)</b></td>
                    <td><b>Recall (How many relevant items are found?)</b></td>
                    <td><b>F1-Score<b></td>
                </tr>
                <tr>
                    <td><b>MedTech</b></td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td><b>Emerging MedTech</b></td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
                <tr>
                    <td><b>Total</b></td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>
            </table>  
        """.format(
            model, remove_wrong_concepts, strict_eval, 
            mt_prec, mt_rec, mt_f1, 
            emt_prec, emt_rec, emt_f1, 
            total_prec, total_rec, total_f1
            )              
        return header

    def write_eval_html(self, doc, scores, file_name):
        """
        display evaluation result for 1 document
        """
        total = (scores["ents_p"], scores["ents_r"], scores["ents_f"])
        per_type = scores["ents_per_type"]
        med_tech = ("-", "-", "-", "-")
        emed_tech = ("-", "-", "-", "-")
        if per_type != None:
            for key in per_type:
                vals = per_type[key]
                result = (vals["p"], vals["r"], vals["f"], key)
                if key == "MedTech":
                    med_tech = result
                else:
                    emed_tech = result
        file_name = file_name.split("/")[-1]
        header = self.__create_html_header(total, med_tech, emed_tech, file_name)
        colors = {"MedTech":"#ffb703", "eMedTech": "#4ea8de"} 
        options = {"ents":["MedTech", "eMedTech"], "colors": colors}       
        html = displacy.render(doc, style="ent", options=options)
        html = header + html
        file_path = self.read_settings("result_path")
        file_name_complete = self.read_settings("result_eval").format(file_name.replace(".json", ""))
        #write in html file
        with open(file_path + file_name_complete, "w", encoding="utf8") as f:
            f.write(html) 
        return file_path + file_name_complete    

    def write_html(self, doc, file_name): 
        """
        write NER results in html
        return path to html
        """
        colors = {"MedTech":"#ffb703", "eMedTech":"#4ea8de"} 
        options = {"ents":["MedTech", "eMedTech"], "colors": colors}   
        html =  """
                <head><title>NE Recognition</title></head>  
                 <h1><b>NER Results</b></h1>   
                 <h3>File name:</h3>
                 <h4 style="color:DodgerBlue;"> {} </h4>                       
                """.format(file_name)
        html += displacy.render(doc, style="ent", options=options)
        file_path = self.read_settings("result_path")
        file_name = self.read_settings("result_file").format(file_name.replace(".txt", ""))
        #write in html file
        with open(file_path + file_name, "w", encoding="utf8") as f:
            f.write(html)       
        return file_path + file_name



    
    

    
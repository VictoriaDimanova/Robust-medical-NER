"""
create part of html-file for data validation
This html-part contains a list of available in the textcorpus 
IVD concepts. Each concept should be validated as a NE or not NE
"""
import json

# reading the data from the file
extracted_concepts = 'C:\\Users\\z003svfy\Desktop\\extracted_result.json'
extracted_test_concepts = 'C:\\Users\\z003svfy\Desktop\\extracted_test_data.json'

#generate training data rows
with open(extracted_concepts, "r", encoding="utf-8") as f:
    data = f.read() 

# reconstructing the data as a dictionary
js = json.loads(data)
page_counter = 1
row_counter = 0
template = """
<tr>
				<td>{}</td>
				<td id="td{}"><input type="radio" id="{}" name="{}" value="1" checked="" onchange="updateSelectedOption('{}', '{}', '1')"></td>
				<td id="td{}"> <input type="radio" id="{}" name="{}" value="2" onchange="updateSelectedOption('{}', '{}', '2')"></td> 
				<td id="td{}"><input type="radio" id="{}" name="{}" value="3" onchange="updateSelectedOption('{}', '{}', '3')"></td>	
                <td id="td{}"><input type="radio" id="{}" name="{}" value="4" onchange="updateSelectedOption('{}', '{}', '4')"></td>
				<td name="val{}">1</td>					
			</tr>
            """
all_lines = []
concepts_total = []
for item in js:  
    concepts = js[item]
    for concept in concepts:
        #filter out repeated items
        if concept in concepts_total: 
            continue
        print(concept)
        concepts_total.append(concept)
        row_counter += 1   
        if row_counter == 201:
            page_counter += 1
            row_counter = 1
        cell_counter1 = "{}.{}.{}".format(page_counter, row_counter, 1) 
        cell_counter2 = "{}.{}.{}".format(page_counter, row_counter, 2) 
        cell_counter3 = "{}.{}.{}".format(page_counter, row_counter, 3) 
        cell_counter4 = "{}.{}.{}".format(page_counter, row_counter, 4) 
        name_counter = "{}.{}".format(page_counter, row_counter)
        table_row = template.format(
            concept, 
            cell_counter1, cell_counter1, name_counter, name_counter, cell_counter1,
            cell_counter2, cell_counter2, name_counter,name_counter, cell_counter2,
            cell_counter3, cell_counter3, name_counter, name_counter, cell_counter3,
            cell_counter4, cell_counter4, name_counter, name_counter, cell_counter4,
            name_counter
            )
        all_lines.append(table_row)



with open('C:\\Users\\z003svfy\Desktop\\ready.txt', "w", encoding="utf-8") as f:
    for line in all_lines:
        f.write(line + "\n")

#generate test data rows
with open(extracted_test_concepts, "r", encoding="utf-8") as f:
    test_data = f.read() 
js = json.loads(test_data)

test_page = page_counter
test_row_counter = 0

all_lines = []
concepts_total = []
for item in js:  
    concepts = js[item]
    for concept in concepts:
        #filter out repeated items
        if concept in concepts_total: 
            continue
        print(concept)
        concepts_total.append(concept)
        test_row_counter += 1   
        if test_row_counter == 201:
            test_page += 1
            test_row_counter = 1
        cell_counter1 = "{}.{}.{}".format(test_page, test_row_counter, 1) 
        cell_counter2 = "{}.{}.{}".format(test_page, test_row_counter, 2) 
        cell_counter3 = "{}.{}.{}".format(test_page, test_row_counter, 3) 
        cell_counter4 = "{}.{}.{}".format(test_page, test_row_counter, 4) 
        name_counter = "{}.{}".format(test_page, test_row_counter)
        table_row = template.format(
            concept, 
            cell_counter1, cell_counter1, name_counter, name_counter, cell_counter1,
            cell_counter2, cell_counter2, name_counter,name_counter, cell_counter2,
            cell_counter3, cell_counter3, name_counter, name_counter, cell_counter3,
            cell_counter4, cell_counter4, name_counter, name_counter, cell_counter4,
            name_counter
            )
        all_lines.append(table_row)



with open('C:\\Users\\z003svfy\Desktop\\test_ready.txt', "w", encoding="utf-8") as f:
    for line in all_lines:
        f.write(line + "\n")
      
  




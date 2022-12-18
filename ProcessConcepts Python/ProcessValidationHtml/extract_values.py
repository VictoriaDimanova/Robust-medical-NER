from bs4 import BeautifulSoup
import json

"""
Get html with validated data, extract validation info and divide all information according to the category:
1: IVD
2: Relevant
3: Not relevant
4: Context needed
---------------------------------------
IMPORTANT: comment or adjust the code
---------------------------------------
"""

ivd_cats = {}
ivd_cats['1'] = []
ivd_cats['2'] = []
ivd_cats['3'] = []
ivd_cats['4'] = []

validated_test_concepts = [
    r'.\\IVD-CandidatesFrom1To200.html',
    r'.\\IVD-CandidatesFrom201To400.html',
    r'.\\IVD-CandidatesFrom401To600.html',
    r'.\\IVD-CandidatesFrom601To692(1).html'
    ]

for item in validated_test_concepts:
    with open(item, 'r', encoding="utf8") as f:
        test_soup = BeautifulSoup(f, features="html.parser")
        all_rows = test_soup.find_all('tr')
        all_rows.pop(0)
        for tag in all_rows:
            #print(tag)
            content = tag.find_all('td')
            if len(content) == 0:
                continue
            #ivd
            ivd_tag = content[0]
            ivd = ivd_tag.get_text()
            #category
            category_tag = content[5]
            category = category_tag.get_text()   
            ivd_cats[category].append(ivd)


validated_train_concepts = r'.\\IVD-Kandidates(9).html'

with open(validated_train_concepts, 'r', encoding="utf8") as f:  
    soup = BeautifulSoup(f, features="html.parser")
   
    all_rows = soup.find_all('tr')
    all_rows.pop(0)
    for tag in all_rows:
        #print(tag)
        content = tag.find_all('td')
        if len(content) == 0:
            continue
        #ivd
        ivd_tag = content[0]
        ivd = ivd_tag.get_text()
        #category
        category_tag = content[5]
        category = category_tag.get_text()   
        ivd_cats[category].append(ivd)

print("Number of entries per category")
print(1, ":", len(ivd_cats['1']))
print(2, ":", len(ivd_cats['2']))
print(3, ":", len(ivd_cats['3']))
print(4, ":", len(ivd_cats['4']))

with open('ivd_categories_test.txt', 'w') as file:
     file.write(json.dumps(ivd_cats)) 

print("done")     
    
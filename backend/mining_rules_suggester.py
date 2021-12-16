#!/usr/bin/env python
# coding: utf-8

# In[30]:


import pickle
import random
from pprint import pprint
from copy import deepcopy as clone
pickle_in = open("mining_results.pickle","rb")
mining_results = pickle.load(pickle_in)
pickle_in.close()
from data_normalizer import MAPPING_POTENTIAL, undo_normalize
from real_estate_logger import getLogger
logger = getLogger()


# In[20]:


def get_attr_to_suggest(dict_attr_from_graph):
    random.shuffle(mining_results)
    max_num_match_attr = 0
    chosen_key, chosen_val = None, None
    used_attr = None
    used_rules = None
    for dct in mining_results:
        mining_dict = clone(dct)
        is_suitable = False
        current_num_match_attr = 0
        temp_attr = dict()
        mining_keys = list(mining_dict.keys())
        random.shuffle(mining_keys)
        for mining_key in mining_keys:
            mining_val = mining_dict[mining_key]
            if mining_key in dict_attr_from_graph.keys():
                graph_val = dict_attr_from_graph[mining_key]
                if (isinstance(graph_val, list) and mining_val in graph_val) or mining_val==graph_val:
                    temp_attr[mining_key] = mining_val
                    current_num_match_attr +=1
                    is_suitable = True
                mining_dict.pop(mining_key)
        mining_dict_keys = set(mining_dict.keys()).difference(set(dict_attr_from_graph['ignore_attr']))
        if is_suitable and len(mining_dict_keys) > 0 and current_num_match_attr > max_num_match_attr:
            if len(mining_dict_keys)==1 and list(mining_dict_keys)[0]=="potential" and mining_dict["potential"] not in MAPPING_POTENTIAL.keys():
                continue
            while (True):
                chosen_key = random.choice(list(mining_dict_keys))           
                chosen_val = mining_dict[chosen_key]
                if not chosen_key=="potential" or chosen_val in MAPPING_POTENTIAL.keys():
                    break
            max_num_match_attr = current_num_match_attr
            used_attr = temp_attr   
            used_rules = dct
    logger.info('\n     MINING-SUGGESTOR:\nRULES: ' + str(used_rules) + "\nUSED ATTR: " + str(used_attr) + "\nCHOSEN: " + str({chosen_key: chosen_val}))
    return used_rules, used_attr, chosen_key, chosen_val    


# In[21]:


# graph_attr = {'transaction_type': 'thue', 'addr_district':['1', 'tan binh'], 'realestate_type':'nha'}
# get_attr_to_suggest(graph_attr)


# In[22]:


WANT_LIST = ['muốn', 'cần'] 
PRONOUN_LIST = ['bạn', 'anh/chị']

QUESTION = dict()
QUESTION['realestate_type'] = [
    "*pronoun* *want* tìm **realestate_type** có phải không?",
    "*pronoun* *want* *transaction_type* **realestate_type** có phải không?",
]

QUESTION['transaction_type'] = [
    "Có phải *pronoun* *want* **transaction_type** *realestate_type* không?",
    "*pronoun* *want* **transaction_type** có phải không?",
    "*pronoun* *want* **transaction_type** *realestate_type* có phải không?",
]

QUESTION['potential'] = [
    "*pronoun* tìm BĐS để **potential** có phải không?"
    "Có phải *pronoun* *want* tìm *realestate_type* để **potential** không?",
    "Tiềm năng **potential** có phù hợp với nhu cầu của *pronoun* hay không?",
    "Có phải *pronoun* *want* **transaction_type** *realestate_type* để **potential** không?",
    "*pronoun* tìm *realestate_type* *position* để **potential** phải không?",
    "*pronoun* *transaction_type* *realestate_type* *position* để **potential** phải không?",
    "*pronoun* tìm *realestate_type* ở *addr_district* để **potential** phải không?",
    "*pronoun* *transaction_type* *realestate_type* ở *addr_district* để **potential** phải không?",
    "*realestate_type* ở *addr_district* thường dùng để **potential**, *pronoun* có nhu cầu đó không?",
    "Tiềm năng **potential** ở *addr_district* là rất lớn, *pronoun* có nhu cầu này không?",
    "*realestate_type* *position* thường được dùng để **potential**, đây có phải là nhu cầu của *pronoun* không?"
]

QUESTION['position'] = [
    "*pronoun* tìm BĐS ở **position** có phải không?",
    "*pronoun* *want* tìm *realestate_type* ở **position** có phải không?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở **position** có phải không?",
    "Để *potential*, người ta thường chọn *realestate_type* ở **position**. *pronoun* có muốn vị trí này không?",
    "Để *potential* ở *addr_district* người ta thường chọn *realestate_type* **position**. *pronoun* có muốn vị trí này không?",
    "Để *potential* ở *addr_district* người ta thường *transaction_type* *realestate_type* **position**. *pronoun* có muốn vị trí này không?",
    "Ở *addr_district* người ta ưa chuộng *realestate_type* **position**. *pronoun* có muốn vị trí này không?",
    "Ở *addr_district* người ta ưa chuộng *transaction_type* *realestate_type* **position**. *pronoun* có muốn vị trí này không?",
]

QUESTION['addr_district'] = [
    "*pronoun* tìm BĐS ở **addr_district** có phải không?",
    "*pronoun* *want* tìm *realestate_type* ở **addr_district** có phải không?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở **addr_district** có phải không?",
    "Để *potential*, người ta thường chọn *realestate_type* ở **addr_district**. *pronoun* có muốn thêm quận này không?",
    "*potential* là tiềm năng nổi bật của **addr_district**. *pronoun* có muốn thêm quận này không?",
    "*realestate_type* có số lượng nhiều ở **addr_district**. *pronoun* có muốn thêm quận này không?",
    "*realestate_type* *position* có số lượng nhiều ở **addr_district**. *pronoun* có muốn thêm quận này không?",
]


# In[23]:


def beautify(text):
    if len(text) == 0:
        return text
    text = text[0].upper()+text[1:]
    text = '. '.join(i.capitalize() for i in text.split('. '))
    text = text.replace('  ', ' ')
    text = text.replace('  ', ' ')
    return text


# In[28]:


def get_question_mining_statement(pronoun, provided_feature):
    used_rules, used_attr, chosen_key, chosen_val = get_attr_to_suggest(provided_feature)
    if chosen_key is None:
        return None, None, None
    pronoun = PRONOUN_LIST[pronoun%len(PRONOUN_LIST)]
    candidate = list()
    for question in QUESTION[chosen_key]:
        question = question.replace("*pronoun*", pronoun)
        question = question.replace("*want*", WANT_LIST[random.randint(0,len(WANT_LIST)-1)])
        question = question.replace("*"+chosen_key+"*", undo_normalize([chosen_val], chosen_key))
        for key, val in used_attr.items():
            question = question.replace("*"+key+"*", undo_normalize([val], key))
        if question.count("*") == 2:
            candidate.append(question)
    response = beautify(random.choice(candidate))
    logger.info("\n     SUGGEST-RESPONSE:\n" + response)
    return response, chosen_key, chosen_val


# In[29]:


# get_question_mining_statement(1, {'realestate_type': 'nha'})


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


WANT_LIST = ['mu???n', 'c???n'] 
PRONOUN_LIST = ['b???n', 'anh/ch???']

QUESTION = dict()
QUESTION['realestate_type'] = [
    "*pronoun* *want* t??m **realestate_type** c?? ph???i kh??ng?",
    "*pronoun* *want* *transaction_type* **realestate_type** c?? ph???i kh??ng?",
]

QUESTION['transaction_type'] = [
    "C?? ph???i *pronoun* *want* **transaction_type** *realestate_type* kh??ng?",
    "*pronoun* *want* **transaction_type** c?? ph???i kh??ng?",
    "*pronoun* *want* **transaction_type** *realestate_type* c?? ph???i kh??ng?",
]

QUESTION['potential'] = [
    "*pronoun* t??m B??S ????? **potential** c?? ph???i kh??ng?"
    "C?? ph???i *pronoun* *want* t??m *realestate_type* ????? **potential** kh??ng?",
    "Ti???m n??ng **potential** c?? ph?? h???p v???i nhu c???u c???a *pronoun* hay kh??ng?",
    "C?? ph???i *pronoun* *want* **transaction_type** *realestate_type* ????? **potential** kh??ng?",
    "*pronoun* t??m *realestate_type* *position* ????? **potential** ph???i kh??ng?",
    "*pronoun* *transaction_type* *realestate_type* *position* ????? **potential** ph???i kh??ng?",
    "*pronoun* t??m *realestate_type* ??? *addr_district* ????? **potential** ph???i kh??ng?",
    "*pronoun* *transaction_type* *realestate_type* ??? *addr_district* ????? **potential** ph???i kh??ng?",
    "*realestate_type* ??? *addr_district* th?????ng d??ng ????? **potential**, *pronoun* c?? nhu c???u ???? kh??ng?",
    "Ti???m n??ng **potential** ??? *addr_district* l?? r???t l???n, *pronoun* c?? nhu c???u n??y kh??ng?",
    "*realestate_type* *position* th?????ng ???????c d??ng ????? **potential**, ????y c?? ph???i l?? nhu c???u c???a *pronoun* kh??ng?"
]

QUESTION['position'] = [
    "*pronoun* t??m B??S ??? **position** c?? ph???i kh??ng?",
    "*pronoun* *want* t??m *realestate_type* ??? **position** c?? ph???i kh??ng?",
    "*pronoun* *want* *transaction_type* *realestate_type* ??? **position** c?? ph???i kh??ng?",
    "????? *potential*, ng?????i ta th?????ng ch???n *realestate_type* ??? **position**. *pronoun* c?? mu???n v??? tr?? n??y kh??ng?",
    "????? *potential* ??? *addr_district* ng?????i ta th?????ng ch???n *realestate_type* **position**. *pronoun* c?? mu???n v??? tr?? n??y kh??ng?",
    "????? *potential* ??? *addr_district* ng?????i ta th?????ng *transaction_type* *realestate_type* **position**. *pronoun* c?? mu???n v??? tr?? n??y kh??ng?",
    "??? *addr_district* ng?????i ta ??a chu???ng *realestate_type* **position**. *pronoun* c?? mu???n v??? tr?? n??y kh??ng?",
    "??? *addr_district* ng?????i ta ??a chu???ng *transaction_type* *realestate_type* **position**. *pronoun* c?? mu???n v??? tr?? n??y kh??ng?",
]

QUESTION['addr_district'] = [
    "*pronoun* t??m B??S ??? **addr_district** c?? ph???i kh??ng?",
    "*pronoun* *want* t??m *realestate_type* ??? **addr_district** c?? ph???i kh??ng?",
    "*pronoun* *want* *transaction_type* *realestate_type* ??? **addr_district** c?? ph???i kh??ng?",
    "????? *potential*, ng?????i ta th?????ng ch???n *realestate_type* ??? **addr_district**. *pronoun* c?? mu???n th??m qu???n n??y kh??ng?",
    "*potential* l?? ti???m n??ng n???i b???t c???a **addr_district**. *pronoun* c?? mu???n th??m qu???n n??y kh??ng?",
    "*realestate_type* c?? s??? l?????ng nhi???u ??? **addr_district**. *pronoun* c?? mu???n th??m qu???n n??y kh??ng?",
    "*realestate_type* *position* c?? s??? l?????ng nhi???u ??? **addr_district**. *pronoun* c?? mu???n th??m qu???n n??y kh??ng?",
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


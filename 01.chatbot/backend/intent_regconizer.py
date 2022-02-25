#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import json
import itertools
from fuzzywuzzy import process,fuzz
from real_estate_logger import getLogger
logger = getLogger()
from model_api import get_model_api 
extract = get_model_api()
from data_normalizer import normalize
from data_utilities import compound2unicode


# In[2]:


# extract(['1 toi 2 ty'])


# In[3]:


alias = dict()
attention = dict()


# In[4]:


attention['price'] = ['giá', 'tiền']
# price_prefix = ['gia', 'tam gia', 'muc gia', 'khoang gia', 'gia trung binh', 'gia tb', 'tri gia', '']
# price_postfix = ['may', 'may tien', 'bao nhieu', 'bao nhieu tien', 'bn tien', 'bn', 'khoang bao nhieu', 
#                'khoang bao nhieu tien', 'khoang bn', 'khoang bn tien','the nao', 'tn', 'nhu the nao',
#                  'ntn', 'sao', 'ra sao', '?']

# alias['price'] = [ r[0] + ' ' + r[1] for r in itertools.product(price_prefix, price_postfix)]


# In[5]:


attention['area'] = ['diện tích', 'dt', 'rộng', 'm2', 'mét vuông', 'mét 2', 'm 2']
# area_prefix = ['dien tich', 'dt', 'rong', 'dien tich trung binh', 'dien tich tb']
# area_infix = ['may', 'bao nhieu', 'bn', 'khoang bao nhieu', 'khoang bn']
# area_infix2 = ['ra sao', 'the nao', 'tn', 'ntn', 'nhu the nao', 'may', 
#                 'bao nhieu', 'bn', 'khoang bao nhieu', 'khoang bn', '?']
# area_postfix = ['met vuong', 'met 2', 'm2', 'm 2', '', '?']

# area_1 = [ r[0] + ' ' + r[1] for r in itertools.product(area_prefix, area_infix2)]
# area_temp = [ r[0] + ' ' + r[1] for r in itertools.product(area_prefix, area_infix)]
# area_2 = [ r[0] + ' ' + r[1] for r in itertools.product(area_temp, area_postfix)]
# alias['area'] = area_1 + area_2


# In[6]:


attention['potential'] = ['tiềm năng', 'khả năng', 'triển vọng', 'phù hợp', 'thuận lợi', 'thuận tiện','mục đích', 'dùng', 'làm gì', 'để']
# potential_prefix = ['tiem nang', 'kha nang', 'trien vong', 'phu hop', 'thuan loi', 'thuan tien', 'dung', 'co the'
#                     ,'muc dich', 'md', 'lam', 'de lam', 'cho viec', 'cho md', 'cho muc dich']
# potential_postfix = ['the nao', 'nhu the nao', 'ntn', 'tn' ,'dc gi', 'duoc gi', 'gi', '?']

# alias['potential'] = [ r[0] + ' ' + r[1] for r in itertools.product(potential_prefix, potential_postfix)]


# In[7]:


attention['location'] = ['ở đâu', 'tại đâu', 'khu vực', 'địa điểm', 'vị trí', 'chỗ']
# prefix_location = ['tai',  'nam o', 'nam tai', 'thuoc', 'gan', ]
# infix_location = ['dau', 'khu vuc', 'vi tri', 'dia diem', 'cho']
# postfix_location = ['', 'nao','?']

# location_1 = [ r[0] + ' ' + r[1] for r in itertools.product(prefix_location, infix_location)]
# alias['location'] = [ r[0] + ' ' + r[1] for r in itertools.product(location_1, postfix_location)]


# In[8]:


attention['addr_district'] = ['quận', 'q']
# prefix_district = ['tai', 'o', 'nam o', 'nam tai', 'thuoc', 'gan', ]
# infix_district = ['quan', 'q']
# postfix_district = ['', 'nao','?']

# district_1 = [ r[0] + ' ' + r[1] for r in itertools.product(prefix_district, infix_district)]
# alias['addr_district'] = [ r[0] + ' ' + r[1] for r in itertools.product(district_1, postfix_district)]


# In[9]:


# with open('intent_alias_data2.json', 'w') as fp:
#     json.dump(alias, fp)


# In[10]:


with open('intent_alias_data_vn.json', 'r', encoding="utf-8") as fp:
    alias = json.load(fp)
    fp.close()


# In[11]:


def harmony(a, b, c=None):
    if c is None:
        if a == 0 or b == 0:
            return 0
        return 2*a*b/(a+b)
    else:
        if a == 0 or b == 0 or c == 0:
            return 0
        return 3*a*b*c/(a*c + a*b + b*c)

#Nếu hơn nhiều quá (threshold) thì chọn luôn, không thì phải hỏi lại 
def score_similarity(text, key):
    a1 = process.extract(text, alias[key])
    a2 = process.extract(text, attention[key], scorer=fuzz.token_set_ratio)          
#     print('a1', a1, 'a2', a2)
    score_list = list()
    for i in range(len(a1)):
        score = 0;
        score_a1 = a1[i][1];
#         score_a3 = fuzz.ratio(text, a1[i][0])
        for j in range(len(a2)):
            score_a2 = a2[j][1]
            score = max(score, harmony(score_a1, score_a2))
        score_list.append((a1[i][0], score))
    return score_list
            


# In[20]:


DEFINED_INTENTS = ['price', 'area', 'potential', 'location','addr_district']
SPECIAL_INTENTS = ['yes', 'hello', 'dont_care']
INTENT_THRESHOLD = 87 #magical number
MIN_NORMAL_LENGTH = 3 #Những normal nào length quá ngắn thì sẽ filter đi vì không có ý nghĩa xác định intent
def get_candidate_intent(list_normal_text):
    logger.info('Input: ' + str(list_normal_text))
    candidate_intent_dict = dict()
    if list_normal_text is None:
        return candidate_special_intent_dict
    for text in list_normal_text:
        text = text.strip()
        if len(text) < MIN_NORMAL_LENGTH:
            continue
        for intent in DEFINED_INTENTS:
            list_score = score_similarity(text, intent)
            list_score.sort(key=lambda tup: tup[1], reverse = True)
#             print('List scoreeee', list_score)
            best = list_score[0]
#             print(best)
            if best[1] > INTENT_THRESHOLD:
                print("Similarity score of [", text,"]: ", best)
                if intent in candidate_intent_dict:
                    candidate_intent_dict[intent].append(text)
                else:
                    candidate_intent_dict[intent] = [text]
    logger.info('Output: ' + str(candidate_intent_dict))
    return candidate_intent_dict

def get_candidate_special_intent(list_normal_text):
    logger.info('Input: ' + str(list_normal_text))
    candidate_special_intent_dict = dict()
    if list_normal_text is None:
        return candidate_special_intent_dict
    for text in list_normal_text:
        text = text.strip()
#         if len(text) < MIN_NORMAL_LENGTH:
#             continue
        for intent in SPECIAL_INTENTS:
            points = process.extract(text, alias[intent], scorer=fuzz.token_set_ratio)
            if points is not None and len(points) > 0 and points[0][1] ==100:
                if intent in candidate_special_intent_dict:
                    candidate_special_intent_dict[intent].append(text)
                else:
                    candidate_special_intent_dict[intent] = [text]
    logger.info('Output: ' + str(candidate_special_intent_dict))
    return candidate_special_intent_dict


# In[21]:


# points = process.extract("có .", alias['yes'], scorer=fuzz.token_set_ratio)
# print(points)


# In[22]:


def extract_and_get_intent(text):
#     try:
        text = compound2unicode(text)
        if text.count(" ") == 0:
            text = text + "."
        text = text.replace("ở đâu", "tại đâu")
        text = text.replace("o dau", "tại đâu")
        text = text.replace("thuê", "muốn thuê")
        text = text.replace("Thuê", "Muốn thuê")
        text = text.replace("có", "đồng ý")
        text = text.replace("Có", "đồng ý")
        logger.info('\nINPUT: ' + text)
        extracted = extract([text])[0]
        extracted_normed = dict()
        extracted_raw = dict()
        for tag in extracted['tags']:
            key = tag['type']
            value_normed = normalize(tag['content'], key)
            value_raw = tag['content'] 
#             logger.info(value_normed)
            if key not in extracted_normed.keys():
                extracted_raw[key] = [value_raw]
                extracted_normed[key] = [value_normed]
            else:
                extracted_raw[key].append(value_raw)
                extracted_normed[key].append(value_normed)
        logger.info('\n     EXTRACTED: ' + str(extracted_normed))
        extracted_normed_keys = extracted_normed.keys() 
        
        if 'normal' in extracted_raw.keys():
            candidate_intent_dict = get_candidate_intent(extracted_raw['normal']) 
            candidate_special_intent_dict = get_candidate_special_intent(extracted_raw['normal']) 
        else:
            return extracted_raw, extracted_normed, {}, {}
   
        for key in DEFINED_INTENTS:
            if key in extracted_normed_keys and key in candidate_intent_dict.keys():
                candidate_intent_dict.pop(key)
#         for key in SPECIAL_INTENTS:
                
        if len(candidate_intent_dict.keys()) == 0:
            if 'transaction_type' in extracted_normed_keys or 'realestate_type' in extracted_normed_keys:
                candidate_intent_dict = {'real_estate':''}

        logger.info('\n     OUTPUT: INTENT:' + str(candidate_intent_dict) + "\nSPECIAL INTENT: " + str(candidate_special_intent_dict))
        return extracted_raw, extracted_normed, candidate_intent_dict, candidate_special_intent_dict
#     except:
#         logger.error('ERROR')
#         return dict(), dict()


# In[24]:


extract_and_get_intent('diện tích chung cư q7')


# In[ ]:





# In[ ]:





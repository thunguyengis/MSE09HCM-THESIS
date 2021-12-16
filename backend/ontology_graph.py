#!/usr/bin/env python
# coding: utf-8

# In[24]:


# TODO: Remember to add mining rules results in conversation manager
# Sau khi cho user xoá bớt attr thì nhớ force show kết quả --- lúc transactiontype là "tìm" query sai\n",
#"khu vực yên tĩnh" bị bắt thành intent location
# lúc fill nhớ check trùng lặp
#diable nhập tn khi bỏ yêu cầu


# In[25]:


import sys
import random
from copy import deepcopy as clone
from data_normalizer import undo_normalize
from conversation_generator import get_greeting_statement , get_not_understand_statement
from real_estate_logger import getLogger
logger = getLogger()


# In[26]:


WHAT_EVER_CONST = 0.5
PRICE_OFFSET_CONST = 0.1
AREA_OFFSET_CONST = 0.1
PROVIDED_KEY_LIST = ['price', 'transaction_type', 'area', 'realestate_type', 'addr_district', 'potential', 'position']

init_priority_score = dict()
init_priority_score['price'] = 111
init_priority_score['transaction_type'] = 100
init_priority_score['area'] = 90
init_priority_score['realestate_type'] = 80
init_priority_score['addr_district'] = 70
init_priority_score['addr_city'] = 60
init_priority_score['potential'] = 50
init_priority_score['location'] = 40
init_priority_score['interior_floor'] = 30
init_priority_score['interior_room'] = 20
init_priority_score['surrounding_characteristics'] = 10
init_priority_score['position'] = 20
init_priority_score['legal'] = 10
init_priority_score['orientation'] = 10
init_priority_score['surrounding_name'] = 10
init_priority_score['surrounding'] = 10
init_priority_score['addr_ward'] = 10
init_priority_score['addr_street'] = 10


# In[14]:


# init_priority_score.keys()


# In[27]:


class LT_Price():
    def __init__(self, priority_score, operator = '~', cmp_type = 'avg', 
                 identifier = '', isIntent = False):
        self.priority_score_dict = priority_score
        self.value = list()
        self.value_raw = list()
        self.operator = operator
        self.cmp_type = cmp_type
        self.identifier = identifier
        self.isIntent = isIntent
    
    def fill(self, new_value_raw, new_value_normed): 
        if not self.check_is_intent():
            for i in range(len(new_value_normed)):
                new_normed_list_type = list(new_value_normed[i])
                if new_normed_list_type not in self.value and new_value_normed[i][0] is not None:
                    self.value_raw.append(new_value_raw[i])
                    self.value.append(new_normed_list_type)
                    self.priority_score_dict['price'] = 0

    def set_is_intent(self, val):
        self.isIntent = val
        self.priority_score_dict['price'] = 0
        
    def check_is_intent(self):
        return self.isIntent
        
    def set_identifier(self, iden):
        self.identifier = iden
    
    def to_json(self):
        return {'value': self.value, 'value_raw': self.value_raw,'identifier':self.identifier, 'isIntent': self.isIntent, 
                'cmp_type':self.cmp_type, 'operator': self.operator}
    
    def has_value(self):
        if len(self.value) == 0:
            return False
        return True


# In[28]:


class LT_Area():
    def __init__(self, priority_score, operator = '~', cmp_type = 'avg', 
                 identifier = '', isIntent = False):
        self.priority_score_dict = priority_score
        self.value = list()
        self.value_raw = list()
        self.operator = operator
        self.cmp_type = cmp_type
        self.identifier = identifier
        self.isIntent = isIntent
    
    def fill(self, new_value_raw, new_value_normed):
        if not self.check_is_intent():
            for i in range(len(new_value_normed)):
                new_normed_list_type = list(new_value_normed[i])
                if new_normed_list_type not in self.value and new_value_normed[i][0] is not None:
                    self.value_raw.append(new_value_raw[i])
                    self.value.append(new_normed_list_type)
                    self.priority_score_dict['area'] = 0
    
    def check_value(self):
        if self.value['high'] is None and self.value['low'] is None:
            return False
        return True

    def set_is_intent(self, val):
        self.isIntent = val
        self.priority_score_dict['area'] = 0
        
    def check_is_intent(self):
            return self.isIntent
        
    def set_identifier(self, iden):
        self.identifier = iden
    
    def to_json(self):
        return {'value': self.value, 'value_raw': self.value_raw,'identifier':self.identifier, 'isIntent': self.isIntent, 
                'cmp_type':self.cmp_type, 'operator': self.operator}
    
    def has_value(self):
        if len(self.value) == 0:
            return False
        return True


# In[29]:


class LT_Potential():
    def __init__(self, priority_score, identifier = '', isIntent = False):
        self.priority_score_dict = priority_score
        self.value = list()
        self.value_raw = list()
        self.identifier = identifier
        self.isIntent = isIntent 
        
    def fill(self, new_value_raw, new_value_normed):
        if not self.check_is_intent():
            for i in range(len(new_value_normed)):
                if new_value_normed[i] not in self.value:
                    self.value.append(new_value_normed[i])
                    self.value_raw.append(new_value_raw[i])
                    self.priority_score_dict['potential'] = 0

    def set_is_intent(self, val):
        self.isIntent = val
        self.priority_score_dict['potential'] = 0
        
    def check_is_intent(self):
            return self.isIntent
        
    def set_identifier(self, iden):
        self.identifier = iden
    
    def to_json(self):
        return {'value': self.value, 'value_raw': self.value_raw, 'identifier':self.identifier, 'isIntent': self.isIntent}
    
    def has_value(self):
        if len(self.value) == 0:
            return False
        return True


# In[30]:


class LT_Location():
    def __init__(self, priority_score, identifier = '', isIntent = False,):
        self.priority_score_dict = priority_score
        self.identifier = identifier
        self.isIntent = isIntent
        self.attributes = dict()
        self.new_node('addr_district')      
        self.new_node('addr_city')
        self.new_node('addr_ward')
        self.new_node('addr_street')
                
    def new_node(self, attr_name):
        self.priority_score_dict[attr_name] = init_priority_score[attr_name]
        if attr_name == "addr_district":
            self.addr_district = LT_District(priority_score = self.priority_score_dict)
        else:
            self.attributes[attr_name] = LT_Graph_Attribute(attr_name = attr_name, priority_score = self.priority_score_dict)

    def fill_attributes(self, key, value_raw, value_normed):
        if not self.check_is_intent():
            if key == "addr_district":
                self.addr_district.fill(value_raw, value_normed)
            else:
                self.attributes[key].fill(value_raw, value_normed)
                
    def set_is_intent(self, val):
        self.isIntent = val
        self.priority_score_dict['location'] = 0
        self.priority_score_dict['addr_district'] = 0
        for key in self.attributes.keys():
            self.priority_score_dict[key] = 0
        
    def check_is_intent(self):
        return self.isIntent
    
    def set_identifier(self, iden):
        self.identifier = iden
    
    def to_json(self):
        location_dict = {'identifier':self.identifier, 'isIntent': self.isIntent}
        location_dict['addr_district'] = self.addr_district.to_json()
        for key, val in self.attributes.items():
            location_dict[key] = val.to_json()
        return location_dict
    
    def has_value(self):
        if len(self.value) == 0:
            return False
        return True


# In[31]:


class LT_District():
    def __init__(self, priority_score, identifier = '', isIntent = False):
        self.priority_score_dict = priority_score
        self.value = list()
        self.value_raw = list()
        self.identifier = identifier
        self.isIntent = isIntent
    
    def fill(self, new_value_raw, new_value_normed):
        if not self.check_is_intent():
            for i in range(len(new_value_normed)):
                if new_value_normed[i] not in self.value:
                    self.value.append(new_value_normed[i])
                    self.value_raw.append(new_value_raw[i])
                    self.priority_score_dict['addr_district'] = 0
                    self.priority_score_dict['location'] = 0
                    self.priority_score_dict['addr_city'] = 0
    
    def set_is_intent(self, val):
        self.isIntent = val
        self.priority_score_dict['addr_district'] = 0
        self.priority_score_dict['location'] = 0
        self.priority_score_dict['addr_city'] = 0
        self.priority_score_dict['addr_ward'] = 0
        self.priority_score_dict['addr_street'] = 0
        
    def check_is_intent(self):
        return self.isIntent
        
    def set_identifier(self, iden):
        self.identifier = iden
    
    def to_json(self):
        return {'value': self.value, 'value_raw': self.value_raw, 'identifier':self.identifier, 'isIntent': self.isIntent}
    
    def has_value(self):
        if len(self.value) == 0:
            return False
        return True


# In[32]:


# Surr_place, type, orientation, legal, positiom, surr_cha, room, floor, transac_type, city, street, ward
class LT_Graph_Attribute():
    def __init__(self, priority_score, attr_name):
        self.priority_score_dict = priority_score
        self.attr_name = attr_name
        self.value = list()
        self.value_raw = list()
    
    def fill(self, new_value_raw, new_value_normed):
        for i in range(len(new_value_normed)):
            if new_value_normed[i] not in self.value:
                self.value.append(new_value_normed[i])
                self.value_raw.append(new_value_raw[i])
                self.priority_score_dict[self.attr_name] = 0

        if "dat" in new_value_normed and self.attr_name == "realestate_type":
            self.priority_score_dict["interior_room"] = 0
            self.priority_score_dict["interior_floor"] = 0
        
    def to_json(self):
        return {'value': self.value, 'value_raw': self.value_raw}
    
    def has_value(self):
        if len(self.value) == 0:
            return False
        return True


# In[37]:


class LT_RealEstate_Graph():
    def __init__(self):
        self.priority_score_dict = dict()
        # Attribute
        self.attributes = dict()
        for attr_name in ['surrounding_name', 'surrounding', 'realestate_type', 'orientation', 'legal', 'position','surrounding_characteristics', 'interior_room','interior_floor', 'transaction_type']:
            self.new_node(attr_name)
        # Entity
        self.new_node("area")
        self.new_node("price")
        self.new_node("potential")
        self.new_node("location")
        # Other
        self.current_intents = set()
        self.intent_confirmed = False
        self.asked_features = []
        self.pronoun_const = random.randint(0,100)
        self.just_asked_feature = None
        self.just_asked_value = None
        self.special_response = None
        self.just_dont_understand = False
    
    def new_node(self, attr_name):
        self.priority_score_dict[attr_name] = init_priority_score[attr_name]
        if attr_name == "area":
            self.area = LT_Area(priority_score = self.priority_score_dict)
        elif attr_name == "price":
            self.price = LT_Price(priority_score = self.priority_score_dict)
        elif attr_name == "potential":
            self.potential = LT_Potential(priority_score = self.priority_score_dict)
        elif attr_name == "location":
            self.location = LT_Location(priority_score = self.priority_score_dict)
        elif attr_name in ["addr_street", "addr_ward", "addr_district"]:
            self.location.new_node(attr_name)
        else:
            self.attributes[attr_name] = LT_Graph_Attribute(attr_name = attr_name, priority_score = self.priority_score_dict)      
        
    def fill(self, extracted_raw, extracted_normed, return_intents, special_intents):
        if not len(extracted_raw.keys()) >= 1 + ("normal" in extracted_raw.keys()):   
            if len(return_intents.keys())==0:
                if len(special_intents.keys())==0 and not self.just_dont_understand:
                    self.special_response = get_not_understand_statement()
                    self.just_dont_understand = True
                    return
                else: 
                    self.just_dont_understand = False
                if "hello" in special_intents.keys() and len(special_intents.keys())==1:
                    self.special_response = get_greeting_statement()
                    return
        self.special_response = None
        if self.just_asked_feature is not None:
            self.asked_features.append(self.just_asked_feature)
            self.priority_score_dict[self.just_asked_feature] *= WHAT_EVER_CONST
        
        if 'dont_care' in special_intents.keys() and self.just_asked_feature:
            self.priority_score_dict[self.just_asked_feature] = 0         
        elif 'yes' in special_intents.keys() and self.just_asked_feature and self.just_asked_value:
            just_asked_value_raw = undo_normalize([self.just_asked_value], self.just_asked_feature)
            if self.just_asked_feature in extracted_raw.keys():
                extracted_raw[self.just_asked_feature].append(just_asked_value_raw)
                extracted_normed[self.just_asked_feature].append(self.just_asked_value)
            else:
                extracted_raw[self.just_asked_feature]= [just_asked_value_raw]
                extracted_normed[self.just_asked_feature]=[self.just_asked_value]
            self.just_asked_value = None
        
        intent_key_set = set(return_intents.keys())
        for intent_name in intent_key_set.difference(self.current_intents):
            self.mark_intent(intent_name, return_intents[intent_name])            
        self.current_intents = self.current_intents.union(return_intents.keys())
        attr_keys = self.attributes.keys()
        
        for key, value_normed in extracted_normed.items():
            value_raw = extracted_raw[key]
            if key in attr_keys:
                self.attributes[key].fill(value_raw, value_normed)
            elif key == 'price':
                self.price.fill(value_raw, value_normed)
            elif key == 'area':
                self.area.fill(value_raw, value_normed)
            elif key == 'potential':
                self.potential.fill(value_raw, value_normed)      
            elif key in ['addr_district','addr_city', 'addr_ward', 'addr_street']:
                self.location.fill_attributes(key, value_raw, value_normed)
            
    def mark_intent(self, intent, identifier):
        self.current_intents.add(intent)      
        if intent == 'area':
            self.area.set_is_intent(True)
            self.area.set_identifier(identifier)
        elif intent == 'potential':
            self.potential.set_is_intent(True)
            self.potential.set_identifier(identifier)
        elif intent == 'price':
            self.price.set_is_intent(True)
            self.price.set_identifier(identifier)
        elif intent == 'location':
            self.location.set_is_intent(True)
            self.location.set_identifier(identifier)
        elif intent == 'addr_district':
            self.location.set_is_intent(True)
            self.location.addr_district.set_is_intent(True)
            self.location.addr_district.set_identifier(identifier)

    def get_query_statement(self):
        query_list = list()
        query_dict = {"$and":query_list}
        
        for key, attr in self.attributes.items():
            if attr.has_value():
                if key in ['interior_floor', 'interior_room']:
                    for val in attr.value:
                        low = val["value"] -1
                        high = val["value"] + 1
                        query_list.append({key:{"$elemMatch":{"type":val["type"], "value":{"$gte": low}}}})
                        query_list.append({key:{"$elemMatch":{"type":val["type"], "value":{"$lte": high}}}})
                elif key in ['transaction_type', 'realestate_type', 'position']:
                    query_list.append({key:{ "$in": attr.value }})
                
#         if self.potential.has_value():
#             query_list.append({'potential':{ "$in": self.potential.value }})           
        if self.location.addr_district.has_value():
            query_list.append({'addr_district':{ "$in": self.location.addr_district.value }})      
#         if self.location.attributes['addr_city'].has_value():
#             query_list.append({'addr_city':{ "$in": self.location.attributes['addr_city'].value }})            
#         if self.location.attributes['addr_ward'].has_value():
#             query_list.append({'addr_ward':{ "$in": self.location.attributes['addr_ward'].value }})           
#         if self.location.attributes['addr_street'].has_value():
#             query_list.append({'addr_street':{ "$in": self.location.attributes['addr_street'].value }})     

        if self.price.has_value():
            price_query_list = list()
            for ele in self.price.value:
                low = ele[0]
                high = ele[1]
                if high is None:
                    high = low + low * PRICE_OFFSET_CONST
                    low = low - low * PRICE_OFFSET_CONST
                price_query_list.append({"$and":[{"price":{"$gte":low}},{"price":{"$lte":high}}]})
            if len(price_query_list) > 0:
                price_or_dict = {"$or":price_query_list}
                query_list.append(price_or_dict)
        
        if self.area.has_value():
            area_query_list = list()
            for ele in self.area.value:
                low = ele[0]
                high = ele[1]
                if high is None:
                    high = low + low * AREA_OFFSET_CONST
                    low = low - low * AREA_OFFSET_CONST
                area_query_list.append({"$and":[{"area":{"$gte":low}},{"area":{"$lte":high}}]})
            if len(area_query_list) > 0:
                area_or_dict = {"$or":area_query_list}
                query_list.append(area_or_dict) 
                
        for intent in self.current_intents:
            if intent =="real_estate":
                continue
            elif intent =="location":
                query_list.append({"addr_district":{"$exists":True, "$ne": None}})
            else:
                query_list.append({intent:{"$exists":True, "$ne": None}})
                
    # Lúc normalize dbs nhớ sửa tên lại
        if len(query_list) == 0:
            return dict()
        return query_dict
    
    def get_provided_dict(self):
        provided_dict = dict()
        provided_dict['pronoun'] = self.pronoun_const
        if self.price.has_value():
            text = undo_normalize(self.price.value, 'price')
            if len(text)>0:
                provided_dict['price'] = text
        if self.area.has_value():
            text = undo_normalize(self.area.value, 'area')    
            if len(text)>0:
                provided_dict['area'] = text
        if self.attributes['transaction_type'].has_value():
            text = undo_normalize(self.attributes['transaction_type'].value, 'transaction_type')
            if len(text)>0:
                provided_dict['transaction_type'] = text
        if self.attributes['realestate_type'].has_value():
            text = undo_normalize(self.attributes['realestate_type'].value, 'realestate_type')
            if len(text)>0:
                provided_dict['realestate_type'] = text
        if self.attributes['position'].has_value():
            text =  undo_normalize(self.attributes['position'].value, 'position')
            if len(text)>0:
                provided_dict['position'] = text
        if self.location.addr_district.has_value():
            text = undo_normalize(self.location.addr_district.value, 'addr_district')
            if len(text)>0:
                provided_dict['addr_district'] = text
        return provided_dict
    
    def get_provided_dict_suggester(self):
        provided_dict = dict()
        for attr in ['transaction_type', 'realestate_type', 'position']:    
            if self.attributes[attr].has_value():
                provided_dict[attr] = self.attributes[attr].value
        
        if self.potential.has_value():
            provided_dict['potential'] = self.potential.value

        if self.location.addr_district.has_value():
            provided_dict['addr_district'] = self.location.addr_district.value
                     
        provided_dict['ignore_attr'] = list()
        for key, val in self.priority_score_dict.items():
            if val==0:
                provided_dict['ignore_attr'].append(key)     
        return self.pronoun_const, provided_dict
        
    def get_next_attr_to_ask(self):
        prob_list = list()
        key_list = list(self.priority_score_dict.keys())
        sum_val = sum(self.priority_score_dict.values())
        if sum_val == 0:
            return None
        for key in key_list:
            val = self.priority_score_dict[key]
            prob_list.append(val / sum_val)
        try:
            idx = random.choice(len(prob_list), 1, p=prob_list)[0]
        except:
            idx = prob_list.index(max(prob_list)) 
#         self.just_asked_feature = key_list[idx]
        return key_list[idx]
    
    def to_json(self):
        graph_dict = dict()
        graph_dict['just_asked_feature'] = self.just_asked_feature
        graph_dict['just_asked_value'] = self.just_asked_value
        graph_dict['price'] = self.price.to_json()
        graph_dict['area'] = self.area.to_json()
        graph_dict['potential'] = self.potential.to_json()
        graph_dict['location'] = self.location.to_json()
        for key, val in self.attributes.items():
            graph_dict[key] = val.to_json()
        graph_dict['priority_score'] = self.priority_score_dict
        graph_dict['current_intents'] = list(self.current_intents)
        graph_dict['intent_confirmed'] = self.intent_confirmed
        graph_dict['asked_features'] = self.asked_features      
        return graph_dict
    
    def get_mentioned_attr(self):
        mentioned_attr = list()
        for key, val in self.priority_score_dict.items():
            if key not in ["addr_district", "addr_street", "addr_city"] and val == 0:
                mentioned_attr.append(key)
        return mentioned_attr

    def get_attr_for_sorting(self):
        attr_for_sorting = list()
        for key, attr in self.attributes.items():
            if key in ['surrounding_characteristics', 'legal', 'orientation', 'surrounding_name', 'surrounding'] and attr.has_value():
                attr_for_sorting.append({'key':key, 'value':attr.value})              
        for key, attr in self.location.attributes.items():
            if attr.has_value():
                attr_for_sorting.append({'key': key, 'value':attr.value})
        if self.potential.has_value() and not self.potential.check_is_intent:
            attr_for_sorting.append({'key': 'potential', 'value':attr.value})
        return attr_for_sorting


# In[ ]:





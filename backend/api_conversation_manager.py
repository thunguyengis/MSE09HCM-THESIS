#!/usr/bin/env python
# coding: utf-8

## In[13]:


#chạy mining nhớ exclude intent
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import time
import random
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
app = Flask(__name__)
CORS(app) 
# Nếu người dùng muốn bán nhà thì câu reply phải khác (kết quả query thì giống)
#Nhớ pop bớt graph ra khi timeout
from pprint import pprint
from ontology_graph import LT_RealEstate_Graph
from intent_regconizer import extract_and_get_intent
from conversation_generator import get_question_response
from mining_rules_suggester import get_question_mining_statement

from data_normalizer import undo_normalize
from real_estate_logger import getLogger
logger = getLogger()
Graph_Container = dict()


## In[14]:


from pymongo import MongoClient
import os
try:
    client = MongoClient(os.getenv("DBSTRING"))
    db = client['real_estate']
    read_collection = db['query_data_normalized']
    rating_collection = db['rating_data_with_saved_conversation']
except:
    logger.info("\n     ERROR IN DATABASE CONNECTION\n")


## In[15]:


def msg(code, mess=None):
    if code == 200 and mess is None:
        return jsonify({"code":200, "value": True})
    else:
        return jsonify({"code": code, "message": mess}), code


## In[16]:


def get_new_id():
    while (True):
        _id = str(random.randint(100000, 999999))
        if _id not in Graph_Container.keys():
            return _id


## In[ ]:


def process_save_POST(data):
    data["timestamp"] = int(round(time.time() * 1000))
    rating_collection.insert_one(data)
    return "saved"


## In[ ]:


NUM_RESULTS_FOR_RETURN = 20
CONCERNED_ATTRIBUTES = ['price', 'area', 'interior_floor', 'interior_room','position', 'legal', 'orientation', 'potential', 'addr_district']

def process_conversation_POST(graph_id, message):
    graph = None
    if graph_id in Graph_Container.keys():
        graph = Graph_Container[graph_id]
    else:
        graph = LT_RealEstate_Graph()
        Graph_Container[graph_id] = graph
        
    extracted_raw, extracted_normed, candicate_intent_dict, candicate_special_intent_dict = extract_and_get_intent(message)   
    graph.fill(extracted_raw, extracted_normed, candicate_intent_dict, candicate_special_intent_dict)


## In[ ]:


def process_conversation_GET(graph_id, filter_dict, force_get_results):  
    graph = Graph_Container[graph_id]   
    query = graph.get_query_statement()
    if query is None:
        return None
    
    print(query,end='\n'*2)
    cursor = read_collection.find(query)
    document_count = read_collection.count_documents(query)
    GET_dict = dict()
    GET_dict["mentioned_attributes"] = graph.get_mentioned_attr()
    GET_dict["document_count"] = document_count
    
    if ready_to_return_results(document_count, graph) or force_get_results:
        GET_dict['has_results'] = True
        GET_dict['concerned_attributes'] = CONCERNED_ATTRIBUTES
        get_results(cursor, graph, GET_dict, filter_dict)
    else:
        GET_dict['has_results'] = False
        if graph.special_response is not None:
            GET_dict['question'] = graph.special_response
            GET_dict["initial_fill"] = False    
        else:
            GET_dict["initial_fill"] = True 
            use_suggestion = True  
            
            if random.randint(0,100) > 50:
                pronoun, provided_feature_suggest = graph.get_provided_dict_suggester()
                suggestion, chosen_key, chosen_val = get_question_mining_statement(pronoun, provided_feature_suggest)
                if suggestion:
                    GET_dict['question'] = suggestion
                    graph.just_asked_feature = chosen_key
                    graph.just_asked_value = chosen_val
                else:
                    use_suggestion = False
            else:
                use_suggestion = False
                
            if not use_suggestion:
                provided_feature = graph.get_provided_dict()
                next_feature_to_ask = graph.get_next_attr_to_ask()
                if next_feature_to_ask is None:
                    GET_dict['has_results'] = True
                    GET_dict['concerned_attributes'] = CONCERNED_ATTRIBUTES
                    get_results(cursor, graph, GET_dict, filter_dict)
                else:
                    GET_dict['feature_to_ask'] = next_feature_to_ask             
                    graph.just_asked_feature = next_feature_to_ask
                    GET_dict['question'] = get_question_response("question", next_feature_to_ask, provided_feature)
    
        if 'question' in GET_dict.keys():
            if GET_dict['question'] is None or GET_dict['question'] == "":
                GET_dict['has_results'] = True
                GET_dict['concerned_attributes'] = CONCERNED_ATTRIBUTES
                get_results(cursor, graph, GET_dict, filter_dict)
                
    if len(GET_dict["mentioned_attributes"]) != 0:
        GET_dict["initial_fill"] = True      
    else:
        GET_dict["initial_fill"] = False
    GET_dict['query'] = query  
    GET_dict['graph'] = graph.to_json() 
    
    return GET_dict


## In[ ]:


import multiprocessing 
import itertools


## In[ ]:


def compute_score(doc, attr_for_sorting):
#     for doc in docs:
    doc['score'] = 0
    for attr_dict in attr_for_sorting:
        key = attr_dict['key']
        vals = attr_dict['value']
        if key in doc.keys():
            for val in vals:
                if val in doc[key]:
                    doc['score'] = doc['score'] - 1
    return doc


## In[ ]:


reserved_document_key = ['tittle', 'url', 'address', 'publish_date']
MAX_NUM_DOC_FOR_SORT = 100

def get_results(cursor, graph, GET_dict, filter_dict):
    result_container = list()
    intent_values_container = dict()
    for intent in graph.current_intents:
        if intent != "real_estate":
            intent_values_container[intent] = {"response": "RESPONSE", "value":list()}
    doc_list = list()
    attr_for_sorting = graph.get_attr_for_sorting()

    for doc in cursor:
        doc['score'] = 0
        for attr_dict in attr_for_sorting:
            key = attr_dict['key']
            vals = attr_dict['value']
            if key in doc.keys():
                for val in vals:
                    if val in doc[key]:
                        doc['score'] = doc['score'] - 1
        doc_list.append(doc)
        if len(doc_list) > MAX_NUM_DOC_FOR_SORT:
            break
            
    doc_list = sorted(doc_list, key=lambda k: k['score']) 

    for doc in doc_list:
        doc.pop("_id")
        doc_keys = list(doc.keys())      
        
        for intent in intent_values_container.keys(): 
            if intent in doc.keys() and doc[intent] is not None:
                intent_values_container[intent]["value"].append(doc[intent])  
            elif intent == "location" and "addr_district" in doc.keys():
                intent_values_container[intent]["value"].append(doc["addr_district"]) 
#         for key in doc_keys:
#             if key not in reserved_document_key and key not in GET_dict['concerned_attributes']:
#                 doc.pop(key)
                
        doc_is_added = False
        if filter_dict is None:
            result_container.append(doc)
            doc_is_added = True     
        else:
            fil_key = filter_dict["filter_key"]
            fil_val = filter_dict["filter_value"]
            if fil_key =="all" or (fil_key in doc.keys() and fil_val in doc[fil_key]):
                result_container.append(doc)
                doc_is_added = True
            
        if doc_is_added:    
            for key in GET_dict['concerned_attributes']:
                if key in doc.keys():
                    value = doc[key]
                    if value is not None:
                        doc[key] = undo_normalize(value, key)
             
        if len(result_container) > NUM_RESULTS_FOR_RETURN:
            break    
            
    GET_dict["result_container"] = result_container
    
    if filter_dict is None:
        for intent in intent_values_container.keys(): 
            if intent in ["price", "area"]:
                value_list = np.array(intent_values_container[intent]["value"]).astype(np.float)
                mean_value = 0
                try:
                    mean_value = int(np.mean(value_list))
                except:
                    mean_value = 100
                if mean_value > 100000:
                    mean_value = (mean_value // 100000)*100000
#                 mean_value = undo_normalize(mean_value, intent)
                intent_values_container[intent]["value"] = mean_value
                
            elif intent in ["location", "potential", "addr_district"]:
                value_list = intent_values_container[intent]["value"]
                value_list = [item for sublist in value_list for item in sublist]
                value_list = sorted(value_list, key=value_list.count,reverse=True)
                value_list = list(set(value_list))[0:3]
#                 value_list = [undo_normalize(i, intent) for i in value_list]
                intent_values_container[intent]["value"] = value_list
            intent_values_container[intent]["response"] = get_question_response("response", intent, graph.get_provided_dict())
        if len(intent_values_container.keys()) > 0:
            GET_dict["intent_values_container"] = intent_values_container


## In[ ]:


NUM_RESULT_THRESHOLD = {"real_estate":20, "price": 50, "area":50, "location": 70, "addr_district": 70, "potential":70}
NUM_MENTIONED_ATTR_THRESHOLD = {"real_estate":7, "price": 7, "area":7, "location": 7, "addr_district": 7, "potential":7}

def ready_to_return_results(document_count, graph):
    num_mentioned_attr = len(graph.get_mentioned_attr())
    for intent in graph.current_intents:
        if document_count <= NUM_RESULT_THRESHOLD[intent] or num_mentioned_attr > NUM_MENTIONED_ATTR_THRESHOLD[intent]:
            return True
    return False


## In[ ]:


@app.route('/')
def index():
    return """<h1>HTBOT</h1>"""

@app.errorhandler(404)
def url_error(e):
    return msg(404, "NOT FOUND")

@app.errorhandler(500)
def server_error(e):
    return msg(500, "SERVER ERROR")

#input_data: { message: <text>, graph_id: <something>}

@app.route('/api/LT-conversation-manager', methods=['POST'])
def post_api():
    input_data = request.json
    print(input_data)
    if "message" not in input_data.keys(): 
        return msg(400, "Message cannot be None")
    else:
        message = input_data["message"]
    if "graph_id" not in input_data.keys(): 
        graph_id = get_new_id()
    else:
        graph_id = input_data["graph_id"]
    logger.info('\n   API POST: graph: ' + graph_id + " message: " + message)
    process_conversation_POST(graph_id, message)
    return msg(200, "Graph_id: " + str(graph_id))

@app.route('/api/LT-conversation-manager', methods=['GET'])
def get_api():
    graph_id = request.args.get('graph_id')
    force_get_results = bool(request.args.get('force_get_results'))
    
    filter_dict = None
    filter_key = request.args.get('key_filter')
    filter_value = request.args.get('value_filter')

    if filter_key is not None:
        filter_dict = {"filter_key":filter_key, "filter_value": filter_value}
 
    if graph_id is None: 
        return msg(400, "Graph ID cannot be None")    
    if graph_id not in Graph_Container.keys():
        return msg(404, "Graph not found")
    
    logger.info('\n   API GET: GRAPH: ' + graph_id + " FORCE: " + str(force_get_results) + " FILTER: " + str(filter_dict))
    output_data = process_conversation_GET(graph_id, filter_dict, force_get_results)
    return jsonify(output_data)

@app.route('/api/LT-conversation-manager', methods=['DELETE'])
def delete_api():
    graph_id = request.args.get('graph_id')
    new_node_name = request.args.get('new_node')
    if graph_id is None: 
        return msg(400, "Graph ID cannot be None")   
    if graph_id not in Graph_Container.keys():
        return msg(404, "Graph not found")
    else:
        logger.info('\n   API DELETE: GRAPH: ' + graph_id + " NEW NODE: " + str(new_node_name))
        if new_node_name is None:
            Graph_Container.pop(graph_id)
            return msg(200, "Pop graph " + str(graph_id))
        else:
            graph = Graph_Container[graph_id]
            graph.new_node(new_node_name)
            return msg(200, "New node for " + new_node_name + " in graph " + str(graph_id))
        
@app.route('/api/LT-save-rating-conversation', methods=['POST'])
def post_save_rating_conversation():
    input_data = request.json
    saved = process_save_POST(input_data)
    return msg(200, saved)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4001, debug=True)

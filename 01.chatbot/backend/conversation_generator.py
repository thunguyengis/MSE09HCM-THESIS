#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pprint import pprint
import re
import random


# In[1]:


GREETING = [
    'Xin chào! 👋 Tôi là HTBot 🤖. Tôi được lập trình để tư vấn cho bạn về bất động sản ở Hà Nội và TP.HCM.',
    'Xin chào! 👋 HTBot được lập trình để tư vấn cho bạn về bất động sản ở Hà Nội và TP.HCM.'
]

def get_greeting_statement():
    return random.choice(GREETING)


# In[2]:


NOT_UNDERSTAND = [
    'Tôi không hiểu ý của bạn',
    'Xin lỗi, tôi không hiểu ý lắm',
    'Xin lỗi, ý của bạn hơi khó hiểu',
    'Hãy nhập thông tin rõ ràng hơn'
]

def get_not_understand_statement():
    return random.choice(NOT_UNDERSTAND)


# In[3]:


WANT_LIST = ['muốn', 'cần'] 
PRONOUN_LIST = ['bạn', 'anh/chị']

QUESTION = dict()
QUESTION['realestate_type'] = [
    "*pronoun* *want* tìm đất hay nhà?",
    "*pronoun* *want* tìm đất, nhà hay căn hộ?",
    "*pronoun* *want* *transaction_type* đất hay nhà?",
    "*pronoun* *want* *transaction_type* đất, nhà hay căn hộ?",
    "*want* tìm đất hay nhà vậy *pronoun* ?",
    "*want* tìm đất, nhà hay căn hộ vậy *pronoun* ?",
    "*want* *transaction_type* đất hay nhà vậy *pronoun* ?",
    "*want* *transaction_type* đất, nhà hay căn hộ vậy *pronoun* ?"
]
QUESTION['transaction_type'] = [
    "*pronoun* *want* mua hay thuê?",
    "*pronoun* *want* thuê hay mua?",
    "*want* mua hay thuê vậy *pronoun*?",
    "Mua hay thuê vậy *pronoun*?",
    "*pronoun* *want* mua hay thuê *realestate_type*?",
    "*pronoun* *want* mua hay thuê *realestate_type* ở *district*?",
    "*pronoun* *want* mua *realestate_type* hay thuê *realestate_type*?",
    "*pronoun* *want* mua *realestate_type* hay thuê *realestate_type* ở *district*?",
    "*pronoun* *want* mua hay thuê *realestate_type* *position*?",
    "*pronoun* *want* thuê *realestate_type* hay mua *realestate_type* *position*?",
    "*want* mua hay thuê *realestate_type* vậy *pronoun* ?",
    "*want* mua hay thuê *realestate_type* ở *district* vậy *pronoun* ?",
    "*want* mua *realestate_type* hay thuê *realestate_type* vậy *pronoun* ?",
    "*want* mua *realestate_type* hay thuê *realestate_type* ở *district* vậy *pronoun* ?",
    "*want* mua hay thuê *realestate_type* *position* vậy *pronoun* ?",
    "*want* thuê *realestate_type* hay mua *realestate_type* *position* vậy *pronoun* ?"
]
QUESTION['price'] = [
    "*pronoun* *want* tìm với giá bao nhiêu?",
    "*pronoun* *want* tìm với giá thế nào?",
    "Giá khoảng bao nhiêu vậy *pronoun* ?",
    "Giá thế nào vậy *pronoun*?",
    "*pronoun* có kinh phí bao nhiêu?",
    "*pronoun* muốn đầu tư bao nhiêu?",
    "*pronoun* *want* *transaction_type* với giá bao nhiêu?",
    "*pronoun* *want* tìm *realestate_type* với giá bao nhiêu?",
    "*pronoun* *want* *transaction_type* *realestate_type* với giá bao nhiêu?",
    "*pronoun* *want* tìm *realestate_type* ở *district* với giá bao nhiêu?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở *district* với giá bao nhiêu?",
    "*pronoun* *want* tìm *realestate_type* *position* với giá bao nhiêu?",
    "*pronoun* *want* *transaction_type* *realestate_type* *position* với giá bao nhiêu?"
]
QUESTION['area'] = [
    "*pronoun* *want* tìm với diện tích bao nhiêu?",
    "*pronoun* *want* tìm với diện tích thế nào?",
    "Diện tích thế nào vậy *pronoun*?",
    "*pronoun* *want* *transaction_type* với diện tích bao nhiêu?",
    "*pronoun* *want* tìm *realestate_type* với diện tích bao nhiêu?",
    "*pronoun* *want* *transaction_type* *realestate_type* với diện tích bao nhiêu?",
    "*pronoun* *want* tìm *realestate_type* ở *district* với diện tích bao nhiêu?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở *district* với diện tích bao nhiêu?",
    "*pronoun* *want* tìm *realestate_type* *position* với diện tích bao nhiêu?",
    "*pronoun* *want* *transaction_type* *realestate_type* *position* với diện tích bao nhiêu?"
]
QUESTION['addr_district'] = [
    "*pronoun* thích ở quận nào?",
    "*pronoun* ưa chuộng quận nào?",
    "*pronoun* ưu tiên những quận nào?",
    "*pronoun* *want* tìm *realestate_type* ở quận nào?",
    "*pronoun* *want* *transaction_type* bất động sản ở quận nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở quận nào?",
    "*pronoun* *want* tìm *realestate_type* *position* ở quận nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* *position* ở quận nào?",
    "Với *price* thì *pronoun* *want* tìm bất động sản ở quận nào?",
    "Với *price* thì *pronoun* *want* *transaction_type* bất động sản ở quận nào?",
    "Với *price* thì *pronoun* *want* *transaction_type* *realestate_type* ở quận nào?",
    "Với *price* thì *pronoun* *want* tìm *realestate_type* ở quận nào?",
    "Với *area* thì *pronoun* *want* tìm bất động sản ở quận nào?",
    "Với *area* thì *pronoun* *want* *transaction_type* bất động sản ở quận nào?",
    "Với *area* thì *pronoun* *want* *transaction_type* *realestate_type* ở quận nào?",
    "Với *area* thì *pronoun* *want* tìm *realestate_type* ở quận nào?",
]
QUESTION['addr_city'] = [
    "*pronoun* *want* tìm ở thành phố nào?",
    "*pronoun* *want* tìm ở Hà Nội hay TP.HCM?",
    "*pronoun* *want* tìm *realestate_type* ở thành phố nào?",
    "*pronoun* *want* tìm *realestate_type* ở Hà Nội hay TP.HCM?",
    "*pronoun* *want* *transaction_type* ở thành phố nào?",
    "*pronoun* *want* *transaction_type* ở Hà Nội hay TP.HCM?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở thành phố nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở Hà Nội hay TP.HCM?",
]
QUESTION['potential'] = [
    "*pronoun* sử dụng bất động sản với mục đích gì?",
    "*pronoun* *want* bất động sản có tiềm năng gì?",
    "*pronoun* *transaction_type* bất động sản với mục đích gì?",
    "*pronoun* *transaction_type* bất động sản có tiềm năng gì?",
    "*pronoun* *want* tìm *realestate_type* với mục đích gì?",
    "*pronoun* *want* tìm *realestate_type* có tiềm năng gì?",
    "*pronoun* *want* *transaction_type* *realestate_type* với mục đích gì?",
    "*pronoun* *want* *transaction_type* *realestate_type* có tiềm năng gì?",
]

QUESTION['location'] = [
    "*pronoun* thích ở khu vực nào?",
    "*pronoun* ưa chuộng quận nào?",
    "*pronoun* ưu tiên những quận nào?",
    "*pronoun* *want* tìm *realestate_type* ở khu vực nào?",
    "*pronoun* *want* *transaction_type* bất động sản ở khu vực nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở khu vực nào?",
    "*pronoun* *want* tìm *realestate_type* *position* ở khu vực nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* *position* ở khu vực nào?",
    "Với *price* thì *pronoun* *want* tìm bất động sản ở khu vực nào?",
    "Với *price* thì *pronoun* *want* *transaction_type* bất động sản ở khu vực nào?",
    "Với *price* thì *pronoun* *want* *transaction_type* *realestate_type* ở khu vực nào?",
    "Với *price* thì *pronoun* *want* tìm *realestate_type* ở khu vực nào?",
    "Với *area* thì *pronoun* *want* tìm bất động sản ở khu vực nào?",
    "Với *area* thì *pronoun* *want* *transaction_type* bất động sản ở khu vực nào?",
    "Với *area* thì *pronoun* *want* *transaction_type* *realestate_type* ở khu vực nào?",
    "Với *area* thì *pronoun* *want* tìm *realestate_type* ở khu vực nào?",
]
QUESTION['interior_floor'] = [
    "*pronoun* *want* tìm bất động sản có mấy tầng ?",
    "*pronoun* *want* *transaction_type* bất động sản có mấy tầng ?",
    "*pronoun* *want* *transaction_type* *realestate_type* có mấy tầng ?",
    "*pronoun* *want* tìm *realestate_type* có mấy tầng ?",
]
QUESTION['interior_room'] = [
    "*pronoun* *want* tìm bất động sản có những phòng gì ?",
    "*pronoun* *want* *transaction_type* bất động sản có những phòng gì ?",
    "*pronoun* *want* *transaction_type* *realestate_type* có những phòng gì ?",
    "*pronoun* *want* tìm *realestate_type* có những phòng gì ?",
    "*pronoun* *want* tìm bất động sản có bao nhiêu phòng ?",
    "*pronoun* *want* *transaction_type* bất động sản có bao nhiêu phòng ?",
    "*pronoun* *want* *transaction_type* *realestate_type* có bao nhiêu phòng ?",
    "*pronoun* *want* tìm *realestate_type* có bao nhiêu phòng ?",
    "*pronoun* *want* tìm bất động sản có mấy phòng ngủ ?",
    "*pronoun* *want* *transaction_type* bất động sản có mấy phòng ngủ ?",
    "*pronoun* *want* *transaction_type* *realestate_type* có mấy phòng ngủ ?",
    "*pronoun* *want* tìm *realestate_type* có mấy phòng ngủ ?",
    "*pronoun* *want* tìm bất động sản có mấy phòng tắm ?",
    "*pronoun* *want* *transaction_type* bất động sản có mấy phòng tắm ?",
    "*pronoun* *want* *transaction_type* *realestate_type* có mấy phòng tắm ?",
    "*pronoun* *want* tìm *realestate_type* có mấy phòng tắm ?",
]
QUESTION['surrounding_characteristics'] = [
    "*pronoun* *want* khu vực xung quanh bất động sản có đặc điểm gì không ?",
    "*pronoun* *want* khu vực xung quanh bất động sản có tính chất gì ?",
    "*pronoun* *want* khu vực xung quanh *realestate_type* có đặc điểm gì không ?",
    "*pronoun* *want* khu vực xung quanh *realestate_type* có tính chất gì ?",
]
QUESTION['position'] = [
    "*pronoun* thích ở hẻm hay mặt tiền?",
    "*pronoun* ưu tiên hẻm hay mặt tiền?",
    "*pronoun* *want* tìm *realestate_type* ở hẻm hay mặt tiền?",
    "*pronoun* *want* *transaction_type* bất động sản ở hẻm hay mặt tiền?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở hẻm hay mặt tiền?",
]
QUESTION['legal'] = [
    "*pronoun* *want* những loại giấy tờ pháp lý nào?",
    "*pronoun* *want* những giấy phép nào?",
]
QUESTION['orientation'] = [
    "*pronoun* thích bất động sản hướng theo hướng nào?",
    "*pronoun* *want* *transaction_type* bất động sản hướng theo hướng nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* hướng theo hướng nào?",
    "*pronoun* *want* tìm *realestate_type* hướng theo hướng nào?",
]
QUESTION['surrounding_place'] = [
    "*pronoun* *want* khu vực xung quanh bất động sản có những địa điểm gì ?",
    "*pronoun* *want* khu vực xung quanh *realestate_type* có những địa điểm gì ?",
    "*pronoun* *want* bất động sản gần những khu vực nào ?",
    "*pronoun* *want* tìm *realestate_type* gần những khu vực nào ?",
    "*pronoun* có *want* bất động sản gần những khu vực nào không ?",
    "*pronoun* có *want* *realestate_type* gần những khu vực nào không ?",
]
QUESTION['addr_ward'] = [
    "*pronoun* *want* tìm ở phường nào?"
    "*pronoun* *want* tìm *realestate_type* ở phường nào?",
    "*pronoun* *want* *transaction_type* bất động sản ở phường nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở phường nào?",
    "Trong *district* thì *pronoun* *want* tìm *realestate_type* ở phường nào?",
    "Trong *district* thì *pronoun* *want* *transaction_type* *realestate_type* ở phường nào?",
    "Trong *district* thì *pronoun* *want* *transaction_type* bất động sản ở phường nào?",
]
QUESTION['addr_street'] = [
    "*pronoun* *want* tìm ở đường nào?"
    "*pronoun* *want* tìm *realestate_type* ở đường nào?",
    "*pronoun* *want* *transaction_type* bất động sản ở đường nào?",
    "*pronoun* *want* *transaction_type* *realestate_type* ở đường nào?",
]


# In[4]:


RESPONSE_INTENT = dict()
RESPONSE_INTENT['real_estate'] = [
    "Dưới đây là danh sách các BĐS thoả nhu cầu của *pronoun*:",
    "Đây là các BĐS có thể phù hợp với *pronoun*:",
    "Các BĐS sau sẽ đáp ứng được yêu cầu mà *pronoun* *want*:",
    "Mời *pronoun* xem qua các BĐS phù hợp:",
    "Mời *pronoun* xem qua những BĐS mà chúng tôi tìm được:",
]
RESPONSE_INTENT['price'] = [
    "Các BĐS thoả nhu cầu của *pronoun* thường có giá vào khoảng:",
    "Đây là mức giá kì vọng cho các yêu cầu của *pronoun*:",
    "Với các yêu cầu *pronoun* *want* thì giá của BĐS sẽ vào khoảng:",
    "Với các đặc điểm trên thì giá của BĐS sẽ rơi vào khoảng:",
]
RESPONSE_INTENT['area'] = [
    "Các BĐS thoả nhu cầu của *pronoun* thường có diện tích vào khoảng:",
    "Đây là diện tích kì vọng cho các yêu cầu của *pronoun*:",
    "Với các yêu cầu *pronoun* *want* thì diện tích của BĐS sẽ vào khoảng:",
    "Với các đặc điểm trên thì diện tích của BĐS sẽ rơi vào khoảng:",
]
RESPONSE_INTENT['potential'] = [
    "Với các đặc điểm trên thì thường BĐS sẽ có tiềm năng:",
    "Với các đặc điểm trên thì BĐS thường được dùng để:",
    "Các BĐS như những yêu cầu của *pronoun* thường được dùng để:",
]
RESPONSE_INTENT['location'] = [
    "Nên chọn BĐS nằm ở khu vực:",
    "Các khu vực phù hợp:",
]
RESPONSE_INTENT['addr_district'] = [
    "Nên chọn BĐS nằm ở khu vực quận:",
    "Các quận phù hợp:",
]


# In[5]:


REPLACEMENT = {
    "*pronoun*": "*PN*",
    "*want*": "*W*",
    "*price*": "*P*",
    "*transaction_type*": "*TT*",
    "*area*": "*A*",
    "*realestate_type*": "*RT*",
    "*district*": "*D*",
    "*position*": "*PO*"
}
REPLACEMENT_REVERSED = {val:key for key, val in REPLACEMENT.items()}

for key, val in QUESTION.items():
    sub_list = list()
    for question in val:
        tok = [i.group()[1:-1] for i in re.finditer('\*[a-z_]+\*',question)]
        if 'pronoun' in tok: tok.remove('pronoun')
        if 'want' in tok: tok.remove('want')
        for rep_key, rep_val in REPLACEMENT.items():
            question = question.replace(rep_key, rep_val)  
        sub_list.append((tok, question))
    QUESTION[key] = sub_list

for key, val in RESPONSE_INTENT.items():
    sub_list = list()
    for question in val:
        tok = [i.group()[1:-1] for i in re.finditer('\*[a-z_]+\*',question)]
        if 'pronoun' in tok: tok.remove('pronoun')
        if 'want' in tok: tok.remove('want')
        for rep_key, rep_val in REPLACEMENT.items():
            question = question.replace(rep_key, rep_val)  
        sub_list.append((tok, question))
    RESPONSE_INTENT[key] = sub_list


# In[6]:


def get_question_response(question_type, feature_name, provided_feature):
    if question_type == "question":
        statement_dict = QUESTION
    elif question_type=="response":
        statement_dict = RESPONSE_INTENT
    else:
        return get_greeting_statement() 
    if feature_name not in statement_dict.keys():
        return ""
    pronoun = PRONOUN_LIST[provided_feature['pronoun']%len(PRONOUN_LIST)]
    candidate = list()
    for tok_list, pattern in statement_dict[feature_name]:
        choose = True
        for tok in tok_list:
            if tok not in provided_feature.keys():
                choose = False
                break
        if choose:
            want_word = WANT_LIST[random.randint(0,len(WANT_LIST)-1)]
            question = pattern.replace("*PN*", pronoun)
            question = question.replace("*W*", want_word)
            for tok in tok_list:
                question = question.replace(REPLACEMENT["*"+tok+"*"], provided_feature[REPLACEMENT_REVERSED[REPLACEMENT["*"+tok+"*"]][1:-1]])
            candidate.append(question)
    return beautify(random.choice(candidate))


# In[9]:


def beautify(text):
    if len(text) == 0:
        return text
    text = text[0].upper()+text[1:]
    text = text.replace('  ', ' ')
    text = text.replace('  ', ' ')
    return text


# In[ ]:





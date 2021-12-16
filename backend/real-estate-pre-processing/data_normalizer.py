#!/usr/bin/env python
# coding: utf-8

# In[4]:


import re
import string
import sys
sys.path.append('real-estate-pre-processing')
import data_utilities
from fuzzywuzzy import process


# In[32]:


#Chưa normalize được các case như 1000000000 VND
def normalize(text, norm_type="none"):
    text = data_utilities.compound2unicode(text)
    text = re.sub('Mười','10', text)
    text = re.sub('mười','10', text)
    text = data_utilities.remove_vietnamese_accent(text)
#     print('haha', text)
    if norm_type=="price":
        low, high = normalize_price(text)
        return low, high
    
    elif norm_type=="area":
        low, high = normalize_area(text)
        return low, high
    
    elif norm_type=="interior_room":
        room_name, room_num = normalize_room(text)
        return {"type":room_name, "value": room_num}
        
    elif norm_type=="interior_floor":
        floor_name, floor_num = normalize_floor(text)
        return {"type":floor_name, "value": floor_num}
    
    elif norm_type=="addr_district":
        text = normalize_district(text)  
    
    elif norm_type=="addr_ward":
        text = normalize_ward(text) 
        
    elif norm_type=="legal":
        text = normalize_legal(text)
        
    elif norm_type=="orientation":       
        text = normalize_orientation(text)
        
    elif norm_type=="position":
        text = normalize_position(text)
        
    elif norm_type=="realestate_type":
        text = normalize_real_estate_type(text)
        
    elif norm_type=="transaction_type":
        text = normalize_transaction_type(text)
        
    return text


# In[37]:


main_divider = '-'
dividers = ['toi', 'va', '~', 'hoac']
currency_unit = ['ti', 'ty', 'trieu', 'tr', 'nghin', 'ngan', 'k']
maping_num = {'mot':'1', 'hai':'2', 'ba':'3', 'bon':'4', 'nam':'5', 'sau':'6', 'bay':'7', 'tam':'8', 'chin':'9'}
def normalize_price(text):
    for key, value in maping_num.items():
         text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)
    text = text.replace('ti', 'ty')    
    text = text.replace('tram', '#00')
    text = text.replace('trieu', 'tr')
    text = text.replace('muoi', '#0') #Mươi :)))
    text = text.replace(' #', '')
    text = text.replace('ruoi', '5') # rưỡi
    text = text.replace('mot', '1') #Mốt nhé
    text = text.replace('k', 'kk')
    text = text.replace('nghin', 'kk')
    text = text.replace('ngan', 'kk')
    text = text.replace('dong', 'vnd')
    text = text.replace(',', '.')
    
    for div in dividers:
        text = re.sub(div, main_divider, text)
    price_list = list()
    arr = text.split(main_divider)
#     print('Divided: ', arr)
    biggest_unit = None
    for element in reversed(arr):
        prices = powerful_split_price(element)
#         print('Splited: ', prices)
        for price in reversed(prices):
            value, unit = normalize_price_unit(price, biggest_unit)
            if value == 0:
                continue
            price_list.append(value)
            biggest_unit = unit
#             print(biggest_unit)
    if len(price_list) == 0:
        low, high = None, None
    elif len(price_list) == 1:
        low, high = price_list[0], None
    else:
        low, high = min(price_list), max(price_list)
    return low, high

re_num = '\d+(\s\.\s\d+)?'
re_vnd = re.compile('(\d+(\s\.\s\d+)?\svnd)')
re_hud = re.compile('(\d+(\s\.\s\d+)?\skk)')
re_mil = re.compile('(\d+(\s\.\s\d+)?\str)')
re_bil = re.compile('(\d+(\s\.\s\d+)?\sty)')

def powerful_split_price(text):
    text = text.strip()
    idx_bil = [0] + [i.start() for i in re.finditer(re_bil, text)] + [len(text)]
    idx_mil = [0] + [i.start() for i in re.finditer(re_mil, text)] + [len(text)]
    idx_hud = [0] + [i.start() for i in re.finditer(re_hud, text)] + [len(text)]
    idx_vnd = [0] + [i.start() for i in re.finditer(re_vnd, text)] + [len(text)]
#     print('idx_bil', idx_bil)
#     print('idx_mil', idx_mil)
#     print('idx_hud', idx_hud)
    price_list = list()
    if len(idx_bil) > 2:
        for i in range(0, len(idx_bil) - 1):
            price = text[idx_bil[i]:idx_bil[i+1]]
            if price != '':
                price_list.append(price)
    elif len(idx_mil) > 2:
        for i in range(0, len(idx_mil) - 1):
            price = text[idx_mil[i]:idx_mil[i+1]]
            if price != '':
                price_list.append(price)
    elif len(idx_hud) > 2:
        for i in range(0, len(idx_hud) - 1):
            price = text[idx_hud[i]:idx_hud[i+1]]
            if price != '':
                price_list.append(price)
    elif len(idx_vnd) >2:
        for i in range(0, len(idx_vnd) - 1):
            price = text[idx_vnd[i]:idx_vnd[i+1]]
            if price != '':
                price_list.append(price)
    elif text != '':
        price_list.append(text)      
    return price_list
    
maping_unit = {'ty': 1000000000, 'tr': 1000000, 'kk':1000, 'vnd':1}
def normalize_price_unit(text, pre_unit):
    if text == '':
        return None, None
    final_value = 0
    arr = text.split(' ')
    if pre_unit is None: 
        pre_unit = 'vnd'
    current_unit = pre_unit
    num_list = [float(re.sub(' ','', i.group())) for i in re.finditer('\d+(\s.\s\d+)?', text)]
    unit_list = [i.group() for i in re.finditer('[a-z]+', text)]
#     if 'vnd' not in len(unit_list):
#         unit_list.append('vnd')
#     print('Num list: ', num_list)
#     print('Unit list: ', unit_list)
    if len(unit_list) == 0:
        
        final_value = num_list[-1] * maping_unit[pre_unit]
        return final_value, pre_unit
    
    odd_unit = 'vnd'
    for i in range(min(len(num_list), len(unit_list))):
        num = num_list[i]
        unit = unit_list[i]
        if unit in maping_unit.keys():
            final_value += maping_unit[unit]*num
            odd_unit = unit
    if len(num_list) > len(unit_list):
        odd = num_list[len(unit_list)]
        if odd < 10:
            final_value += maping_unit[odd_unit]*odd/10
        else:
            final_value += maping_unit[odd_unit]*odd/1000               
#     print(final_value, odd_unit)
    return final_value, odd_unit


# In[35]:


area_divider = ['dai','rong','nhan','\*']
re_num_with_unit = '(\d+(\s\.\s\d+)?)(\s(m\^|km\^|m|km|ha))?'
re_num_n_x = '(' + re_num_with_unit + '\sx\s)'
re_powerful_x =  re_num_n_x + '+' + re_num_with_unit

def normalize_area(text):
    for div in area_divider:
        text = text.replace(div,'x')
    for key, value in maping_num.items():
         text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)
    text = text.replace(',','.')
    text = text.replace('.',' . ')
    text = text.replace('x',' x ')
    text = text.replace('  ',' ')
    text = text.replace('  ',' ')
    text = text.replace('kilo met','km')
    text = text.replace('met','m')   
    text = text.replace('vuong','2')
    text = text.replace('m 2','m^')
    text = text.replace('m2','m^')
    text = text.replace('hecta','ha')
    text = text.replace('hec ta','ha')
    text = text.replace('hec','ha')
    area_list = list()
    pre_RHS = '0' #right hand side

    if 'x' in text:
        x_group = [i.group() for i in re.finditer(re_powerful_x, text)]
        for x in x_group:
            text = text.replace(x,'')
            area_list += normalize_area_x(x)
    
    non_x_group = [i.group() for i in re.finditer(re_num_with_unit, text)]
    for x in non_x_group:  
        area_list.append(normalize_area_non_x(x)) 
    if len(area_list) == 0:
        low, high = None, None
    elif len(area_list) == 1:
        low, high = area_list[0], None
    else:
        low, high = min(area_list), max(area_list)
    return low, high

def normalize_area_x(text):
    factor = 1
    if 'km' in text:
        factor = 1000000
    text = re.sub('[^\d\.x]','', text)
    area_list = list()
    arr = [float(i) for i in text.split('x')]
    for i in range(len(arr) -1):
        area = arr[i]*arr[i+1]*factor
        area_list.append(area)
    return area_list

def normalize_area_non_x(text):
    factor = 1
    if 'km' in text:
        factor = 1000000
    elif 'ha' in text:
        factor = 10000
    text = re.sub('[^\d\.]','', text)
    return float(text)*factor


# In[15]:


re_rooms = [
    r"s(an)?\W*t(huong)?",
    r"san\b",
    r"(p(hong)?)?\W*t(ro)?|\btro\b",
    r"(p(hong)?)?\W*n(gu)?|\bngu\b",
    r"(p(hong)?)?\W*g(ia[tc])?|\bgia[tc]\b",
    r"(p(hong)?)?\W*t(ho)?\b|\btho\b",
    r"(p(hong)?)?\W*k(hach)?|\bkhach\b",
    r"n(ha)?\W*k(ho)?|\bkho\b",
    r"gara|o\W*to|xe\W*hoi",
    r"xe(\W*may)?",
    r"ki\W*o[ts]",
    r"(gieng\W*)?troi",
    r"van\W*phong|k(inh)?\W+d(oanh)?",
    r"ba[nl]g?\W*co(ng?|l)",
    r"(p(hong)?)?\W*(b(ep)?|\ban\b)|\bbep\W*an\b",
    r"(p(hong)?)?\W*(tam|v(e)?\W*s(inh)?|wc|toi?ll?e?t)",
    r"(p(hong)?)?\W+l(am)?\W+v(iec)?",
    r"(p(hong)?)?\W+s(inh)?\W+h(oat)?"]

room_name = [
    "san thuong",
    "san",
    "phong tro",
    "phong ngu",
    "phong giat",
    "phong tho",
    "phong khach",
    "nha kho",
    "gara",
    "xe may",
    "kiots",
    "gieng troi",
    "van phong",
    "ban cong",
    "bep an",
    "nha ve sinh",
    "phong lam viec",
    "phong sinh hoat"
]

#Nhớ xoá ban công

def normalize_room(text):
    text = text.split()
    temp = text[-1]
    text = ' '.join(text[:-1])

    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)
        
    text = text + ' ' + temp 
    num_arr = [i.group() for i in re.finditer('\d+(\s\.\s\d+)?',text)]
    num_arr = [int(float(i.replace(' ',''))) for i in num_arr]
    if len(num_arr) > 0:
        num_room = min(num_arr)
    else:
        num_room = 1
    current_key = ''
    current_idx = -1
    for idx, regex in enumerate(re_rooms):
#         print(text)
        keys = [i.group() for i in re.finditer(regex, text)]
#         print(idx, keys)
        if len(keys) > 0 and len(current_key) < len(max(keys, key = len)):
            current_key = max(keys, key = len)
            current_idx = idx
    if current_idx == -1:
        return None, num_room
    return room_name[current_idx], num_room


# In[16]:


def lcs(X, Y):
    X =X.replace(' ','')
    Y =Y.replace(' ','')
    m = len(X)
    n = len(Y)   
    # declaring the array for storing the dp values
    L = [[None]*(n+1) for i in range(m+1)]

    """Following steps build L[m+1][n+1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0:
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1]+1
            else:
                L[i][j] = max(L[i-1][j], L[i][j-1])

    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    return L[m][n]


# In[17]:


re_floor = [
    "tang", "lau", "tam", "me", "cap 4",
    "tang gac",
    "tang tret",
    "tang lung",
    "tang ham",
    "ban cong",
    "san thuong",
]
floor_name = [
    "tang", "tang", "tang", "tang", "tang",
    "gac",
    "tret",
    "lung",
    "ham",
    "ban cong",
    "san thuong",
]

def normalize_floor(text):
    half = 0;
    if 'ruoi' in text:
        half = 0.5
        text = re.sub(r"\b{}\b".format('ruoi'), '', text)
    
    text = text.split()
    if len(text) == 0:
        return None, 1
    
    temp = text[-1]
    text = ' '.join(text[:-1])

    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)      
    text = text + ' ' + temp 
    num_arr = [i.group() for i in re.finditer('\d+(\s\.\s\d+)?',text)]
    num_arr = [int(float(i.replace(' ',''))) for i in num_arr]
    if len(num_arr) > 0:
        num_floor = min(num_arr)
    else:
        num_floor= 1
    lcs_list = list()
    for regex in re_floor:
        lcs_list.append(lcs(regex, text))
#     print(text)
#     print(lcs_list)
    best_match = max(lcs_list)
    if best_match == 0:
        return None, num_floor
    else:
        return floor_name[lcs_list.index(best_match)], num_floor + half


# In[18]:


district_alias = [r'\bquan', r'\bqan', r'\bqun', r'\bqn', r'\bq ', r'\bdistrict\b', r'\bdist']
def normalize_district(text):
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)
    text = text.replace('.',' ')
    for alias in district_alias:
        text = re.sub(alias, '', text)
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text.strip()


# In[19]:


ward_alias = [r'\bphuong', r'\bphung', r'\bphong', r'\bphg', r'\bpg',r'\bp ', r'\bward ']
def normalize_ward(text):
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)
    text = text.replace('.',' ')
    for alias in ward_alias:
        text = re.sub(alias, '', text)
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text.strip()


# In[20]:


city_alias = [r'\bthanh pho', r'\bthanhpho', r'\bthanh pgo', r'\bthang pho', r'\bt.pho', r'\btpho', r'\btp ',r'\bcity']
def normalize_city(text):
    for key, value in maping_num.items():
        text = re.sub(r"\b{}\b".format(key), "{}".format(value), text)
    text = text.replace('.',' ')
    for alias in city_alias:
        text = re.sub(alias, '', text)
    while '  ' in text:
        text = text.replace('  ', ' ')
    # có thẻ hardcode HN và HCM
    return text.strip()


# In[21]:


ORIENTATION = ['dong', 'nam', 'tay', 'bac', 'dong bac', 'dong nam', 'tay bac', 'tay nam', 'db', 'dn', 'tb', 'tn', 'khong xac dinh']
def normalize_orientation(text):
    text_list = process.extract(text, ORIENTATION)
    max_length = len(text_list[0][0])
    max_score = text_list[0][1]
    res = text_list[0][0]
    
    for idx, ele in enumerate(text_list):
        if ele[1] == max_score:
            if len(ele[0]) > max_length:
                max_length = len(ele[0])
                max_score = ele[1]
                res = ele[0]
        elif ele[1] > max_score:
            max_length = len(ele[0])
            max_score = ele[1]
            res = ele[0]
            
    if (max_score < 80):
        return ""
    res = res.replace('dong', 'd')
    res = res.replace('tay', 't')
    res = res.replace('nam', 'n')
    res = res.replace('bac', 'b')
    res = res.replace('khong xac dinh', 'kxd')
    res = res.replace(' ', '')
    return res


# In[22]:


POSITION = ['hem', 'hxh', 'ngo', 'mat tien', 'mat pho', 'mat duong', 'mt', 'mp', 'md']
POSITION_NAME = ['hem', 'hem', 'hem', 'mat tien', 'mat tien', 'mat tien', 'mat tien', 'mat tien', 'mat tien']
POSITION_INDEX = {w: i for i, w in enumerate(POSITION)}

def normalize_position(pos):
    res, score = process.extractOne(pos, POSITION)
    if score < 60:
        return ''
    return POSITION_NAME[POSITION_INDEX[res]]


# In[23]:


LEGAL = ['so do', 'so hong', 'sd', 'sh', 'giay phep xay dung', 'gpxd', 'giay phep kinh doanh', 'gpkd', 
         'hop dong mua ban', 'hdmb', 'giay to hop le', 'gthl', 'khong xac dinh']
LEGAL_NAME = ['so hong do', 'so hong do', 'so hong do', 'so hong do', 'gpxd', 'gpxd', 'gpkd', 'gpkd', 
              'hdmb', 'hdmb', 'gthl', 'gthl', 'kxd']
LEGAL_INDEX = {w: i for i, w in enumerate(LEGAL)}

def normalize_legal(legal):
    res, score = process.extractOne(legal, LEGAL)
    if score < 50:
        return ''
    return LEGAL_NAME[LEGAL_INDEX[res]]


# In[24]:


real_estate_type = ['nha', 'dat', 'can ho', 'chung cu', 'biet thu', 'villa', 'phong tro', 'nha tro', 'phong',
                       'cua hang', 'shop', 'kiots', 'quan', 'khach san', 'xuong', 'nha xuong', 'kho', 'van phong', 'mat bang', 'toa nha']
real_estate_type_name = ['nha', 'dat', 'can ho', 'can ho', 'nha', 'nha', 'phong tro nha tro', 'phong tro nha tro', 'phong tro nha tro', 'mat bang cua hang shop',
                            'mat bang cua hang shop', 'mat bang cua hang shop', 'mat bang cua hang shop', 'nha', 'nha xuong kho bai dat', 'nha xuong kho bai dat', 'nha xuong kho bai dat', 'van phong', 'mat bang cua hang shop', 'van phong']
real_estate_type_index = {w: i for i, w in enumerate(real_estate_type)}

def normalize_real_estate_type(text):
    res, score = process.extractOne(text, real_estate_type)
#     print(score)
    if score < 70:
        return ''
    return real_estate_type_name[real_estate_type_index[res]]

#     text_list = process.extract(text, real_estate_type)
#     print(text_list)
#     res = 'khach san'
#     max_length = len(text_list[0][0])
#     max_score = text_list[0][1]
#     print(max_score)
#     for idx, ele in enumerate(text_list):
#         if ele[1] == max_score:
#             if len(ele[0]) > max_length:
#                 max_length = len(ele[0])
#                 max_score = ele[1]
#                 res = ele[0]
#         elif ele[1] > max_score:
#             max_length = len(ele[0])
#             max_score = ele[1]
#             res = ele[0]
            
#     if (max_score < 60):
#         return ""
#     return real_estate_type_name[real_estate_type_index[res]]


# In[25]:


# print(normalize_real_estate_type("chung cu can ho"))


# In[26]:


TRANSACTION = ['mua', 'ban', 'cho thue', 'can thue', 'sang nhuong', 'can tim']
TRANSACTION_NAME = ['mua', 'ban', 'thue', 'thue', 'ban', 'tim']
TRANSACTION_INDEX = {w: i for i, w in enumerate(TRANSACTION)}

def normalize_transaction_type(trans):
    res, score = process.extractOne(trans, TRANSACTION)
    if score < 50:
        return ''
    return TRANSACTION_NAME[TRANSACTION_INDEX[res]]


# In[5]:


def undo_normalize_price(low, high): # low, high
    text = ""
    text_low = ""
    text_high = ""
    bil_low = int(low // 1000000000)
    mil_low = int((low % 1000000000) // 1000000)
    k_low   = int((low % 1000000) // 1000)
    if (bil_low > 0) : text_low += str(bil_low) + " tỷ "
    if (mil_low > 0) : text_low += str(mil_low) + " triệu "
    if (k_low > 0)   : text_low += str(k_low) + " nghìn "
    if high is not None:
        bil_high = int(high // 1000000000)
        mil_high = int((high % 1000000000) // 1000000)
        k_high   = int((high % 1000000) // 1000)
        if (bil_high > 0) : text_high += str(bil_high) + " tỷ "
        if (mil_high > 0) : text_high += str(mil_high) + " triệu "
        if (k_high > 0)   : text_high += str(k_high) + " nghìn "
    if len(text_low) and len(text_high):
        text = "từ " + text_low + " đến " + text_high
    elif len(text_low):
        text = text_low
    elif len(text_high):
        text = text_high
    return text

def undo_normalize_area(low, high): # low, high
    text = ""
    text_low = ""
    text_high = ""
    if low > 0: 
        text_low = str(int(low)) + " m2 "
    if high is not None and high > 0 and high != low:
        text_high = str(int(high)) + " m2 "
    if len(text_low) and len(text_high):
        text = "từ " + text_low + " đến " + text_high
    elif len(text_low):
        text = text_low
    elif len(text_high):
        text = text_high
    return text

MAPPING_TRANSACTION = {
    "mua"  :"mua",
    "ban"  :"bán",
    "thue" :"thuê",
    "tim"  :"tìm"
}

MAPPING_REALESTATE_TYPE = {
    'can ho'                 :'căn hộ',
    'dat'                    :'đất',
    'mat bang cua hang shop' :'mặt bằng',
    'nha'                    :'nhà',
    'nha xuong kho bai dat'  :'nhà xưởng',
    'phong tro nha tro'      :'phòng trọ',
    'van phong'              :'văn phòng'
}

MAPPING_ROOM = {
    "san thuong": "sân thượng",
    "san": "sân",
    "phong tro": "phòng trọ",
    "phong ngu": "phòng ngủ",
    "phong giat": "phòng giặt",
    "phong tho": "phòng thờ",
    "phong khach": "phòng khách",
    "nha kho": "nhà kho",
    "gara": "gara",
    "xe may": "xe máy",
    "kiots": "ki ốt",
    "gieng troi": "giếng trời",
    "van phong": "văn phòng",
    "ban cong":"ban công",
    "bep an":"bếp ăn",
    "nha ve sinh": "nhà vệ sinh",
    "phong lam viec": "phòng làm việc",
    "phong sinh hoat": "phòng sinh hoạt"
}

MAPPING_DISTRICT = {
    'thu duc'    : 'quận Thủ Đức',
    'go vap'     : 'quận Gò Vấp',
    'binh thanh' : 'quận Bình Thạnh',
    'tan binh'   : 'quận Tân Bình',
    'tan phu'    : 'quận Tân Phú',
    'phu nhuan'  : 'quận Phú Nhuận',
    'binh tan'   : 'quận Bình Tân',
    'cu chi'     : 'huyện Củ Chi',
    'hoc mon'    : 'huyện Hóc Môn',
    'binh chanh' : 'huyện Bình Chánh',
    'nha be'     :'huyện Nhà Bè',
    'can gio'    :'huyện Cần Giờ',
    'ba dinh'    :'quận Ba Đình',
    'hoan kiem'  :'quận Hoàn Kiếm',
    'hai ba trung':'quận Hai Bà Trưng',
    'dong da'    :'quận Đống Đa',
    'tay ho'     :'quận Tây Hồ',
    'cau giay'   :'quận Cầu Giấy',
    'thanh xuan' :'quận Thanh Xuân',
    'hoang mai'  :'quận Hoàng Mai',
    'long bien'  :'quận Long Biên',
    'tu liem'    :'huyện Từ Liêm',
    'thanh tri'  :'huyện Thanh Trì',
    'gia lam'    :'huyện Gia Lâm',
    'dong anh'   :'huyện Đông Anh',
    'soc son'    :'huyện Sóc Sơn',
    'ha dong'    :'quận Hà Đông',
    'son tay'    :'Thị xã Sơn Tây',
    'ba vi'      :'huyện Ba Vì',
    'phuc tho'   :'huyện Phúc Thọ',
    'thach that' :'huyện Thạch Thất',
    'quoc oai'   :'huyện Quốc Oai',
    'chuong my'  :'huyện Chương Mỹ',
    'dan phuong' :'huyện Đan Phượng',
    'hoai duc'   :'huyện Hoài Đức',
    'thanh oai'  :'huyện Thanh Oai',
    'my duc'     :'huyện Mỹ Đức',
    'ung hoa'    :'huyện Ứng Hoà',
    'thuong tin' :'huyện Thường Tín',
    'phu xuyen'  :'huyện Phú Xuyên',
    'me linh'    :'huyện Mê Linh'
}
MAPPING_POSITION = {
    'hem'      : 'hẻm',
    'mat tien' : 'mặt tiền'
}

MAPPING_FLOOR = {
    "tang": "tầng",
    "gac":  "gác",
    "tret": "tầng trệt",
    "lung": "gác lửng",
    "ham": "tầng hầm",
    "ban cong": "ban công",
    "san thuong": "sân thượng",
}
MAPPING_LEGAL={
    'so hong do': "sổ hồng", 
    'gpxd': "giấy phép xây dựng" ,
    'hdmb': "hợp đồng mua bán", 
    'gthl': "giấy tờ hợp lệ", 
    'kxd': "không xác định"
}

def undo_normalize(value, denorm_type):
    if denorm_type == 'price':
        if isinstance(value, (int, float)):
            return undo_normalize_price(value, None)
        
        price_text_list = list()
        for price in value:
            price_text = undo_normalize_price(price[0], price[1])
            if len(price_text) > 0: 
                price_text_list.append(price_text)
        text = ", ".join(price_text_list[:-1])
        if (len(price_text_list) >= 2):
            text = text + " và " + price_text_list[-1]
        elif (len(price_text_list) > 0):
            text = price_text_list[-1]
        return text
    
    elif denorm_type == 'area':
        if isinstance(value, (int, float)):
            return undo_normalize_area(value, None)
        
        area_text_list = list()
        for area in value:
            area_text = undo_normalize_area(area[0], area[1])
            if len(area_text) > 0: 
                area_text_list.append(area_text)
        text = ", ".join(area_text_list[:-1])
        if (len(area_text_list) >= 2):
            text = text + " và " + area_text_list[-1]
        elif (len(area_text_list) > 0):
            text = area_text_list[-1]
        return text
    elif denorm_type == 'transaction_type':
        trans_set = set()
        for trans in value:
            if trans in MAPPING_TRANSACTION.keys():
                trans_set.add(MAPPING_TRANSACTION[trans])
        return '/'.join(trans_set)
    elif denorm_type == 'realestate_type':
        real_set = set()
        for real in value:
            if real in MAPPING_REALESTATE_TYPE.keys():
                real_set.add(MAPPING_REALESTATE_TYPE[real])
        return '/'.join(real_set)
    elif denorm_type == 'position':
        postion_set = set()
        for pos in value:
            if pos in MAPPING_POSITION.keys():
                postion_set.add(MAPPING_POSITION[pos])
            else:
                postion_set.add(pos)
        return '/'.join(postion_set)
    
    elif denorm_type == 'addr_district':
        dis_text_list = list()
        if not isinstance(value, list):
            value = [value]
        for dis in value:
            if dis.isdigit(): 
                dis_text = "quận " + str(dis)
            elif dis in MAPPING_DISTRICT.keys():
                dis_text = MAPPING_DISTRICT[dis]
            else:
                dis_text = "quận/huyện " + str(dis)
            if len(dis_text) > 0: 
                dis_text_list.append(dis_text)
        text = ", ".join(dis_text_list[:-1])
        if (len(dis_text_list) >= 2):
            text = text + " và " + dis_text_list[-1]
        elif (len(dis_text_list) > 0):
            text = dis_text_list[-1]
        return text
    elif denorm_type == 'interior_room':
        value_dict = dict()
        text_list = list()
        for obj in value:
            value_dict[obj["type"]] = obj["value"]
        for room_name, room_num in value_dict.items():
            if room_name in MAPPING_ROOM.keys():
                text_list.append(str(room_num) + " " + MAPPING_ROOM[room_name])
        text = ", ".join(text_list)
        return text
    
    elif denorm_type == 'interior_floor':
        value_dict = dict()
        text_list = list()
        for obj in value:
            value_dict[obj["type"]] = obj["value"]
        for floor_name, floor_num in value_dict.items():
            if floor_name in MAPPING_FLOOR.keys():
                text_list.append(str(floor_num) + " " + MAPPING_FLOOR[floor_name])                
        text = ", ".join(text_list)
        return text
    
    elif denorm_type == 'orientation':
        text = value
        if text == "kxd":
            return "Không xác định"
        text = text.replace("n", " nam ")
        text = text.replace("d", " đông ")
        text = text.replace("t", " tây ")       
        text = text.replace("b", " bắc ")
        text = text.replace("  ", " ")
        return text.strip()
    elif denorm_type == 'legal':
        if value in MAPPING_LEGAL.keys():
            return MAPPING_LEGAL[value]
    else:
        return value


# In[2]:


# from pymongo import MongoClient
# client = MongoClient('localhost', 27017)
# db = client['real_estate_data']
# collection = db['query_data_normalized_final']


# In[3]:


# po = set()
# for doc in collection.find():
#     if "potential" in doc.keys():
#         for i in doc["potential"]:
#             po.add(i)


# In[4]:


# po


# In[ ]:





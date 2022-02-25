import random
import string
import pandas as pd
import os

from pymongo import MongoClient
try:
    dbstring = os.getenv("DBSTRING")
    client = MongoClient(dbstring)
    db = client['real_estate']
    read_collection = db['query_data_normalized']
    rating_collection = db['rating_data_with_saved_conversation']

except:
    print("\n     ERROR IN DATABASE CONNECTION\n")

# print("Removing...",end='')
# read_collection.delete_many({})
# print("Done!")


chars = string.printable[10:62] + ' '

# lay ten quan huyen
df = pd.read_csv('name.csv')
name_2,name_3 = df.NAME_2.tolist(), df.NAME_3.tolist()
names = {x.lower():[] for x in name_2}
for x,y in zip(name_2,name_3):
    names[x.lower()].append(y.lower())

realestate_type = ['nha', 'dat', 'can ho', 'can ho', 'nha', 'nha', 'phong tro nha tro', 'phong tro nha tro', 'phong tro nha tro', 'mat bang cua hang shop', 'mat bang cua hang shop', 'mat bang cua hang shop', 'mat bang cua hang shop', 'nha', 'nha xuong kho bai dat', 'nha xuong kho bai dat', 'nha xuong kho bai dat', 'van phong', 'mat bang cua hang shop', 'van phong']
transaction_type = ['mua', 'ban', 'thue', 'thue', 'ban', 'tim']
interior_floor = [ "tang", "gac", "tret", "lung", "ham", "ban cong", "san thuong"]
potential = ['kinh doanh', 'làm chỗ ở', 'cho thuê', 'làm văn phòng', 'làm công ty', 'đầu tư', 'mở spa', 'làm văn phòng', 'buôn bán', 'làm khách sạn', 'mở văn phòng', 'làm căn hộ dịch vụ', 'mở nhà hàng', 'mở showroom', 'kinh doanh', 'mở shop', 'thuê', 'làm công ty', 'làm ngân hàng', 'mở shop thời trang', 'mở quán cafe', 'mở cửa hàng', 'làm quán ăn', 'mua bán', 'kinh doanh online', 'làm trường học', 'mở thẩm mỹ viện', 'mở shop thời trang', 'làm trụ sở công ty', 'làm văn phòng', 'làm căn hộ', 'mở nha khoa', 'làm cao ốc', 'mở phòng khám', 'bán lại', 'làm văn phòng', 'mở trung tâm đào tạo', 'mở quán trà sửa', 'xây cao ốc', 'mở văn phòng đại diện', 'xây khách sạn', 'mở quán cafe', 'kinh doanh siêu thị', 'bán hàng online', 'xây nhà trọ', 'mở quán cafe', 'mở văn phòng', 'mở salon tóc', 'mở trung tâm anh ngữ', 'xay mới', 'mở căn hộ dịch vụ', 'mở tiệm nail', 'mở công ty chuyển phát nhanh', 'mở phòng mạch', 'kinh doanh online', 'để định cư', 'mở công ty', 'mở spa', 'mở shop online', 'mở spa', 'mở trung tâm ngoại ngữ', 'bán hàng online', 'mở quán ăn uống', 'mở quán dịch vụ', 'xây phòng trọ', 'kinh doanh nhà hàng', 'mở toà nhà', 'mở văn phòng công ty', 'xây dựng', 'mở thẩm mỹ viện', 'mở quán cafe', 'xây nhà xưởng', 'làm siêu thị mini', 'mở trung tâm dạy học', 'mở quán nhậu', 'mở nhà trẻ', 'xây biệt thự', 'mở nhà thuốc', 'mở trung tâm dạy học', 'mở salon', 'xây nghỉ dưỡng', 'mở shop mỹ phẩm', 'xây xưởng máy', 'xây nhà trọ', 'xây kho', 'mở shop nội thất', 'mở văn phòng công ty', 'xây phòng trọ', 'làm showroom', 'mở quán cafe', 'mở quán karaoke', 'xây nhà trọ', 'làm nhà kho', 'xây văn phòng', 'mở tiệm tóc', 'xây villa biệt thự', 'mở studio', 'mở shop online', 'xây kho xưởng', 'làm văn phòng công ty', 'xây nhà', 'xây căn hộ dịch vụ', 'mở tạp hóa', 'làm văn phòng công ty', 'sinh sống', 'lam văn phòng công ty', 'làm tòa nhà văn phòng', 'mở shop', 'mở shop in thêu', 'mở khách sạn', 'làm văn phòng công ty', 'gần bệnh viện', 'mở nhà nghỉ', 'làm công ty', 'gần trường học công tế', 'mở biệt thự', 'kinh doanh online', 'thuê mặt bằng', 'mở nhà hàng', 'mở phòng gym', 'mở trường', 'làm văn phòng công ty', 'mở tiệm thuốc', 'làm văn phòng công ty', 'mở công ty', 'xây căn hộ dịch vụ', 'mở gym', 'xây dựng cao ốc', 'mở nhà thuốc tây', 'mở văn phòng công ty', 'cho ngân hàng thuê', 'mở trung tâm thương mại', 'mở showroom', 'xây building', 'kinh doanh khách sạn', 'mở bar', 'mở shop quần áo', 'mở trường mầm non', 'mở cửa hàng', 'mở cửa hàng điện thoại', 'làm xưởng máy', 'mở lớp dạy học', 'mở nhà hàng', 'mở spa làm đẹp', 'làm ăn', 'mở building văn phòng', 'chứa hàng', 'kinh doanh cafe', 'mở trung tâm dạy học', 'mở trường anh ngữ', 'xây dựng khách sạn', 'làm văn phòng công ty', 'mở homestay', 'mở trung tâm yoga', 'làm căn hộ dịch vụ', 'làm khách sạn', 'làm kho chứa hàng', 'kinh doanh online', 'mở quán cafe', 'xây lại', 'làm văn phòng', 'làm dịch vụ ăn uống', 'mở quán ăn', 'mở showroom trưng bày', 'xây ở', 'mở shop hoa', 'cho khách thuê', 'mở trường tư thục', 'mở phòng mạch', 'xây dựng văn phòng', 'trưng bày sản phẩm', 'mở tiệm thuốc tây', 'làm xưởng may', 'bán hàng online', 'mở quán', 'mở trường mầm non', 'sản xuất', 'làm căn hộ dịch vụ', 'làm quán cafe', 'mở văn phòng công ty', 'làm văn phòng', 'mở công ty chuyển phát', 'kinh doanh spa', 'xây dựng building', 'kinh doanh buôn bán', 'làm kho hàng', 'làm tài sản', 'mở tiệm vàng', 'mở tiệm áo cưới', 'buôn bán online', 'mở tiệm massage', 'mở show room', 'mở trường học', 'ở gia đình', 'kinh doanh online', 'xây tòa nhà', 'làm công ty', 'mở phòng khám', 'mở tiệm']
orientation = ['dong', 'nam', 'tay', 'bac', 'dong bac', 'dong nam', 'tay bac', 'tay nam', 'khong xac dinh']
position = ['hem', 'mat tien']
legal = ['so hong do', 'gpxd', 'gpxd', 'gpkd', 'gpkd', 'hdmb', 'hdmb', 'gthl', 'gthl', 'kxd']
addr_city = ['ho chi minh']
interior_room = ["san thuong", "san", "phong tro", "phong ngu", "phong giat", "phong tho", "phong khach", "nha kho", "gara", "xe may", "kiots", "gieng troi", "van phong", "ban cong", "bep an", "nha ve sinh", "phong lam viec", "phong sinh hoat"]

df = pd.DataFrame()
num_samples = 400000
lst = list(range(num_samples))
random.shuffle(lst)

out = []
print("Generating...",end='')
for id in lst:
    district = random.choice(list(names.keys()))
    ward = random.choice(names[district])
    new = {
        "url": 'https://www.hungthinhland.com/',
        "tittle": ''.join(random.choices(chars,k=25)),
        "realestate_type": random.choice(realestate_type),
        "transaction_type": random.choice(transaction_type),
        "price": random.randint(1000000,1000000000),
        "area": random.randint(10,1000),
        "interior_floor": [{"type":random.choice(interior_floor),"value":random.randint(1,10)} for _ in range(random.randint(0,3))],
        "potential": random.choices(potential,k=random.randint(0,5)),
        "orientation": random.choice(orientation),
        "position": [random.choice(position)],
        "legal": random.choice(legal),
        "addr_city": random.choice(addr_city),
        "address": ''.join(random.choices(chars,k=50)),
        "addr_district": [district],
        "addr_ward": [ward],
        "addr_street": [''.join(random.choices(chars,k=10))],
        "interior_room": [{"type":random.choice(interior_room),"value":random.randint(1,10)} for _ in range(random.randint(0,5))],
        "surrounding": [''.join(random.choices(chars,k=10)) for _ in range(random.randint(1,5))],
        "surrounding_name": [''.join(random.choices(chars,k=10)) for _ in range(random.randint(1,5))],
        "surrounding_characteristics": [''.join(random.choices(chars,k=10)) for _ in range(random.randint(1,5))],
        "project": [''.join(random.choices(chars,k=10)) for _ in range(random.randint(1,5))],
        "publish_date": '{}/{}/20{}'.format(random.randint(1,30),random.randint(1,12),random.choice([20,21])),
        "real_estate_id": id,
        "description": ''.join(random.choices(chars,k=100))
    }
    out.append(new)

print("Done!\nWriting...",end='')
read_collection.insert_many(out)
print("Done!")

client.close()

from pymongo import MongoClient
try:
    client = MongoClient("mongodb+srv://cuong:cuong@chatbothungthinh.oze0x.mongodb.net/test?authSource=admin&replicaSet=atlas-eu709c-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true")
    db = client['real_estate']
    read_collection = db['query_data_normalized']
    client.close()
    print("OK")
except:
    print("FAIL")
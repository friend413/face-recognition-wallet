import sqlite3
import sys
import os
import os.path
import numpy as np
import ctypes

from face import GetFaceSimilarity

database_base_name = 'users'
table_name = "feature"
wallet_table_name = "wallet"

sqlite_insert_face_wallet_query = "INSERT INTO " + wallet_table_name + " (id, features, token, public_key) VALUES (?, ?, ?, ?)"

sqlite_insert_blob_query = "INSERT INTO " + table_name + " (id, name, features) VALUES (?, ?, ?)"
sqlite_create_table_query = "CREATE TABLE " + table_name + " ( id INTEGER PRIMARY KEY, name TEXT, features BLOB NOT NULL, token VARCHAR(256), wallet_address VARCHAR(256) )"

sqlite_update_all_query = "UPDATE " + table_name + " set name = ?, features = ?, wallet_address = ?, token = ? where id = ?"
sqlite_search_query = "SELECT * FROM " + table_name
sqlite_delete_all = "DELETE FROM " + table_name
sqlite_delete_user = "DELETE FROM " + table_name + " where name = ?"
sqlite_delete_id = "DELETE FROM " + table_name + " where id = ?"

data_all = []
MATCHING_THRES = 0.82
FEATURE_SIZE = 2056
max_id = -1

face_database = None

#open databse
def open_database(db_no):
    global max_id
    global face_database

    db_name = database_base_name + str(db_no) + ".db"
    try:
        face_database = sqlite3.connect(db_name, check_same_thread=False)
        print(f"Database {db_name} connected successfully.")
    except sqlite3.Error as e:
        print(f"Error connecting to database {db_name}: {e}")
        return

    cursor = face_database.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
        
    # Extract column names from the result
    column_names = [column[1] for column in columns]
        
    # Print the column names
    print("Column Names:")
    for column_name in column_names:
        print(column_name)

#    clear_database()
    cursor = face_database.execute("SELECT name FROM sqlite_master WHERE type='table';")
    #check tables exist in database
    tables = [
        v[0] for v in cursor.fetchall()
        if v[0] != "sqlite_sequence"
    ]
    cursor.close()
    if not "feature" in tables:
        face_database.execute(sqlite_create_table_query)

    cursor = face_database.execute(sqlite_search_query)
    #load index and feature in "feature table"
    for row in cursor.fetchall():
        id = row[0]
        name = row[1]
        features = np.fromstring(row[2], dtype=np.uint8)
        if not features.shape[0] == FEATURE_SIZE:
            continue

        features = features.reshape(FEATURE_SIZE)
        
        data_all.append({'id':id, 'name':name, 'features':features})
        if id > max_id:
            max_id = id
    cursor.close()
    print('>>>>>>>>>>>> Load Users', len(data_all))

#create database
def create_database():
    db_no = 0
    db_name = ""
    while True:
        db_name = database_base_name + str(db_no) + ".db"
        if not os.path.isfile(db_name):
            break
        db_no += 1
    open_database(db_no)

def clear_database():
    global face_database

    data_all.clear()
    cursor = face_database.cursor()
    cursor.execute(sqlite_delete_all)
    face_database.commit()
    cursor.close()
    return

def register_face_wallet(features):
    id, _, _ = verify_face(features)
    if id != -1:
        return id

    global face_database
    global max_id
    max_id = max_id + 1
    id = max_id
    cursor = face_database.cursor()
    cursor.execute(sqlite_insert_blob_query, (id, "", np.frombuffer(features, dtype=np.uint8).tostring()))
    face_database.commit()
    cursor.close()
    data_all.append({'id':id, 'name':"", 'features':features})
    return id

def register_face(features):
    id, _, _ = verify_face(features)
    if id >= 0:
        return -1

    global face_database
    global max_id
    max_id = max_id + 1
    id = max_id
    cursor = face_database.cursor()
    cursor.execute(sqlite_insert_blob_query, (id, "", np.frombuffer(features, dtype=np.uint8).tostring()))
    face_database.commit()
    cursor.close()
    data_all.append({'id':id, 'name':"", 'features':features})
    return id

def update_face(id = None, name = None, features = None, wallet_address = None, token = None):
    global face_database
    cursor = face_database.cursor()
    cursor.execute(sqlite_update_all_query, (name, features.tostring(), id, wallet_address, token))
    face_database.commit()
    cursor.close()

def verify_face(feat):

    global max_id
    max_score = 0

    if len(data_all) == 0:
        return -2, None, None
    find_id, find_name = -1, None
    for data in data_all:
        id = data['id']
        features = data['features']

        score = GetFaceSimilarity(feat, features) # [sub_id,:]
        print('>>>> Mathing Result', data['name'], score)
        if score >= max_score:
            max_score = score
            find_id = id
            find_name = data['name']

    if max_score >= MATCHING_THRES:
        print("score = ", max_score)
        return find_id, find_name, max_score

    return -1, None, None

def verify_face_with_name(feat, name):

    global max_id
    max_score = 0

    if len(data_all) == 0:
        return -2, None, None
    find_id, find_name = -1, None
    for data in data_all:
        id = data['id']
        features = data['features']

        if data['name'].lower() != name.lower():
            continue

        score = GetFaceSimilarity(feat, features) # [sub_id,:]
        print('>>>> Mathing Result', data['name'], score)
        if score >= max_score:
            max_score = score
            find_id = id
            find_name = data['name']

    if max_score >= MATCHING_THRES:
        print("score = ", max_score)
        return find_id, find_name, max_score

    return -1, None, None

def get_wallet_info_by_id(id):
    global face_database
    cursor = face_database.cursor()
    query = "SELECT id, wallet_address FROM " + table_name + " WHERE id = ?"
    cursor.execute(query, (id,))
    row = cursor.fetchone()
    cursor.close()

    if row:
        return row[0], row[1]
    else:
        return None, None

def get_info(id):
    for data in data_all:
        nid = data['id']
        if nid == id:
            return data['name'], data['features']
        else:
            return None, None, None, None, None

def get_userlist():
    userlist = []
    for data in data_all:
        userlist.append(data['name'])
    return userlist

def remove_face(feat):
    global data_all
    matching_id = 0
    matching_face = []
    #print(">>>>>>> data in data all is ", data_all)
    for data in data_all:
        id = data['id']
        features = data['features']
        score = GetFaceSimilarity(feat, features)
        if score >= MATCHING_THRES:
            matching_face.append(id)

    global face_database
    cursor = face_database.cursor()
    for face_id in matching_face:
        cursor.execute(sqlite_delete_id, (face_id,))
    face_database.commit()
    cursor.close()
    data_all = [data for data in data_all if data['id'] not in matching_face]
    if len(matching_face) > 0:
        return 1, []
    else:
        return 0, []

def remove_user(name):
    global face_database
    cursor = face_database.cursor()
    cursor.execute(sqlite_delete_user, (name,))
    face_database.commit()
    cursor.close()
    global data_all
    data_all = [i for i in data_all if not (i['name'] == name)]

def set_threshold(th):
    threshold = th

def get_threshold():
    return threshold

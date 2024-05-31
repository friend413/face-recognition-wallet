import os
from PIL import Image
from io import BytesIO
import base64
import FaceManage.manage as db_manage
from flask import Flask, render_template, request, jsonify
import base64
import logging
import requests
import uuid
# import cv2
from flask_cors import CORS
import numpy as np

from face import InitFaceSDK, GetLivenessInfo, GetFeatureInfo
#from idocr import InitIDOCRSDK, GetIDOCRInfo

ret = InitFaceSDK()
print('Init Face Engine', ret)
#ret = InitIDOCRSDK()
#print('Init IDOCR Engine', ret)

app = Flask(__name__)
CORS(app)
# db_manage.open_database(0)
db_ret = db_manage.open_database(0)

@app.route('/') 
def home():
    return render_template('index.html')

@app.route("/get_wallet2", methods=['POST'])
def get_wallet():
    content = request.get_json()
    print(" ----Get wallet---- ")
    print(content)
    print(" ****************** ")
    imageBase64 = content['image'][22:]
    image = Image.open(BytesIO(base64.b64decode(imageBase64))).convert('RGB')
    box, liveness, result = GetLivenessInfo(image)

    print(" ---- result ---- ")
    print(result)
    print(" ****************** ")
    if liveness == 1:
        face_width = box[2] - box[0]
        if face_width < 150:
            result = 'Move Closer'
        elif face_width > 210:
            result = 'Go Back'
        else:
            box, liveness, feature = GetFeatureInfo(image, 0)

            result = "ok"
            # result = db_manage.register_face_wallet(feature)
            # if result == -1:
            #     # create new wallet & register it in db & return create wallet
            #     new_wallet = 1

            #     result = new_wallet
    print(" ---- result2 ---- ")
    print(result)
    print(" ****************** ")
    response = jsonify({"status": result})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response


@app.route("/create_wallet", methods=['POST'])
def enroll_user():
    # payload = {
    #     "feature_info": "your_feature_info_here"
    # }
    # rust_server_url = 'http://localhost:8799/create_wallet'

    # # Send the POST request to the other server
    # try:
    #     ret = requests.post(rust_server_url, json=payload)
    #     ret.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
    # except requests.exceptions.RequestException as e:
    #     return jsonify({'error': str(e)}), 500

    # result = 'Create OK'
    # address = ret.json().get('wallet_address')
    # if not address:
    #     return jsonify({'error': 'No wallet address received from Rust server'}), 500
    # print("here2")
    # print(address)
    # # id = db_manage.register_face(feature)
    # # if id == -1:
    # #     result = 'Already Exist'
    # # else:
    # #     result = 'Create OK'

    # response = jsonify({"status": result, "wallet_address": address})
    # response.status_code = 200
    # response.headers["Content-Type"] = "application/json; charset=utf-8"
    # print("  //// ***** \\\\ ")
    # print(response)
    # return response

    # --here

    content = request.get_json()
    print(" -------Enrol user------ ")
    print(content)
    print(" ****************** ")
    imageBase64 = content['image'][22:]
    image = Image.open(BytesIO(base64.b64decode(imageBase64))).convert('RGB')
    box, liveness, result = GetLivenessInfo(image)

    if liveness == 1:
        idx = 0
        face_width = box[2] - box[0]
        address = "none"
        if face_width < 150:
            result = 'Move Closer'
        elif face_width > 210:
            result = 'Go Back'
        else:
            box, liveness, feature = GetFeatureInfo(image, 0)

            payload = {
                "feature_info": "your_feature_info_here"
            }
            rust_server_url = 'http://localhost:8799/create_wallet'

            # Send the POST request to the other server
            try:
                ret = requests.post(rust_server_url, json=payload)
                ret.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            except requests.exceptions.RequestException as e:
                return jsonify({'error': str(e)}), 500

            result = 'Create OK'
            address = ret.json().get('wallet_address')
            if not address:
                return jsonify({'error': 'No wallet address received from Rust server'}), 500
            print("here2")
            print(address)
            # id = db_manage.register_face(feature)
            # if id == -1:
            #     result = 'Already Exist'
            # else:
            #     result = 'Create OK'


    response = jsonify({"status": result, "wallet_address": address})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route("/get_wallet", methods=['POST'])
def verify_user():
    content = request.get_json()
    imageBase64 = content['image'][22:]
    image = Image.open(BytesIO(base64.b64decode(imageBase64))).convert('RGB')

    box, liveness, result = GetLivenessInfo(image)

    result = 'Verify Failed'
    name = ''
    face_score = 0

    if liveness == 1:
        face_width = box[2] - box[0]
        print('>>>>>>>>>> Face Width', box[0], face_width)
        if face_width < 150:
            result = 'Move Closer'
        elif face_width > 210:
            result = 'Go Back'
        else:
            box, liveness, feature = GetFeatureInfo(image, 1)
            id, fname, face_score = db_manage.verify_face(feature)
            if id >= 0:
                result, name = 'Verify OK', fname
            if id == -2:
                result = 'No Users'

    response = jsonify({"status": result, "name": name, "liveness": str(liveness), "matching": str(face_score)})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route("/verify_user_with_name", methods=['POST'])
def verify_user_with_name():
    content = request.get_json()
    imageBase64 = content['image'][22:]
    image = Image.open(BytesIO(base64.b64decode(imageBase64))).convert('RGB')

    box, liveness, result = GetLivenessInfo(image)

    result = 'Verify Failed'
    name = ''

    face_score = 0
    if liveness == 1:
        face_width = box[2] - box[0]
        print('>>>>>>>>>> Face Width', box[0], face_width)
        if face_width < 150:
            result = 'Move Closer'
        elif face_width > 210:
            result = 'Go Back'
        else:
            box, liveness, feature = GetFeatureInfo(image, 1)
            id, fname, face_score = db_manage.verify_face_with_name(feature, content['name'])
            if id >= 0:
                result, name = 'Verify OK', fname
            if id == -2:
                result = 'No Users'

    response = jsonify({"status": result, "name": name, "liveness": str(liveness), "matching": str(face_score)})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route("/remove_user_by_face", methods=['POST'])
def remove_user_by_face():
    #print('>>>>>>>> removal in progress')
    matching_names = []
    content = request.get_json()
    imageBase64 = content['image'][22:]
    #image = cv2.imdecode(np.frombuffer(base64.b64decode(imageBase64), dtype=np.uint8), cv2.IMREAD_COLOR)
    image = Image.open(BytesIO(base64.b64decode(imageBase64))).convert('RGB')
    box, liveness, result = GetLivenessInfo(image)
    
    result = 'Removal Failed'
    name = ''
    face_score = 0

    if liveness == 1:
        face_width = box[2] - box[0]
        print('>>>>>>>>>> Face Width', box[0], face_width)
        if face_width >= 150 and face_width <=210:
            box, liveness, feature = GetFeatureInfo(image, 0)
            face_removed, matching_names = db_manage.remove_face(feature)
            if face_removed == 1:
                result = 'Removed Face'
            elif face_removed == 0:
                result = 'No Face'
            elif face_removed == -1:
                result = 'Admin'
    response = jsonify({"status": result, "removed_names": matching_names})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route("/remove_all", methods=['POST'])
def remove_all():
    db_manage.clear_database()

    response = jsonify({"status": "OK"})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route("/user_list", methods=['POST'])
def user_list():
    userlist = db_manage.get_userlist()

    response = jsonify({"status": "OK", "users": userlist})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route("/remove_user", methods=['POST'])
def remove_user():
    content = request.get_json()
    name = content['name']

    db_manage.remove_user(name)
    response = jsonify({"status": "OK"})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.route('/ocr/idcard', methods=['POST'])
def ocr_idcard():
    file1 = request.files['image1']

    file_name1 = uuid.uuid4().hex[:6]
    save_path1 = '/tmp/' + file_name1 + '_' + file1.filename
    file1.save(save_path1)

    file_path1 = os.path.abspath(save_path1)

    if 'image2' not in request.files:
        file_path2 = ''
    else:
        file2 = request.files['image2']

        file_name2 = uuid.uuid4().hex[:6]
        save_path2 = '/tmp/' + file_name2 + '_' + file2.filename
        file2.save(save_path2)

        file_path2 = os.path.abspath(save_path2)

    status, ocrResDict, if_check = GetIDOCRInfo(file_path1, file_path2)
    response = jsonify({"status": status, "data": ocrResDict, "authenticity": if_check})

    os.remove(file_path1)
    if 'image2' in request.files:
        os.remove(file_path2)

    response.status_code = 200
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

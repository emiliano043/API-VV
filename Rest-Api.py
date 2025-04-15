from typing import Any
from cv2 import Mat
from flask import Flask, request, jsonify
import cv2
import os
from datetime import datetime
import uuid
import time
import numpy
from numpy import ndarray, dtype
import logging
import base64

# Configuración básica de logging
LOG_FILE_PATH = "api_logs2.log"
handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1000 * 1000
UPLOAD_FOLDER = 'upload'
SERVER = "FQA/24.1.0.0"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'plain', 'png', 'jpg', 'jpeg', 'bmp'}
UTIL_Two_Hundred = 200
UTIL_Four_One_Five = 415
UTIL_Four_Two_Two = 422
UTIL_Five_Hundred = 500
UTIL_Four_Hundred = 400
UTIL_Four_Zero_Four = 404
image_store = {}

def log_response(response_json, status_code):
    log_entry = f"Estado: {status_code}, Respuesta: {response_json}"
    logger.info(log_entry)
    for h in logger.handlers:
        h.flush()

def uuid_baliza():
    unique_id = uuid.uuid4()
    baliza = unique_id.hex
    return baliza

def utc_datatime():
    now_utc = datetime.now()
    formatted_time_utc = now_utc.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return formatted_time_utc

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(file, start_time):
    try:
        baliza = uuid_baliza()
        image: Mat | ndarray[Any, dtype[Any]] | ndarray = cv2.imdecode(numpy.frombuffer(file, numpy.uint8), cv2.IMREAD_UNCHANGED)
        end_time = time.time()
        height, width, d = image.shape
        decode_time = end_time - start_time
        if int(width) < 192 or int(height) < 288 or int(width) > 8192 or int(height) > 8192:
            response_json = {
                'tiempo': utc_datatime(),
                'estado': int(UTIL_Four_Two_Two),
                'metodo': "POST",
                "pedido": request.base_url,
                "server": SERVER,
                "baliza": baliza,
                "acceso": request.host_url,
                "decode": decode_time}
            log_response(response_json, UTIL_Four_Two_Two) 
            return jsonify(response_json), UTIL_Four_Two_Two
        
        image_id = request.form.get('name') or request.json.get('name')
        image_store[image_id] = {
            'dimensiones': {'ancho': width, 'alto': height},
            'fecha': utc_datatime(),
            "pedido": request.base_url,
            "server": SERVER,
            "baliza": baliza,
            "acceso": request.host_url
        }

        response_json = {
            'tiempo': utc_datatime(),
            'estado': int(UTIL_Two_Hundred),
            'metodo': "POST",
            "pedido": request.base_url,
            "server": SERVER,
            "baliza": baliza,
            "acceso": request.host_url,
            "decode": decode_time}
        log_response(response_json, UTIL_Two_Hundred) 
        return jsonify(response_json), UTIL_Two_Hundred

    except Exception as e:
        print(e.args)
        response_json = {
            'tiempo': utc_datatime(),
            'estado': int(UTIL_Four_One_Five),
            'metodo': "POST",
            "pedido": request.base_url,
            "server": SERVER,
            "baliza": baliza,
            "acceso": request.host_url,
            "decode": float(0)}
        log_response(response_json, UTIL_Four_One_Five) 
        return jsonify(response_json), UTIL_Four_One_Five

@app.route('/upload', methods=['POST'])
def post():
    start_time = time.time()
    print(request.headers)
    if "image" in request.files and "name" in request.form:
        image_file = request.files.get("image")
        if not allowed_file(image_file.filename):
            end_time = time.time()
            decode_time = end_time - start_time
            response_json = {
                'tiempo': utc_datatime(),
                'estado': int(UTIL_Four_One_Five),
                'metodo': "POST",
                "pedido": request.base_url,
                "server": SERVER,
                "baliza": uuid_baliza(),
                "acceso": request.host_url,
                "decode": decode_time}
            log_response(response_json, UTIL_Four_One_Five) 
            return jsonify(response_json), UTIL_Four_One_Five

        image_bytes = image_file.read()
        return process_image(image_bytes, start_time)

    elif "image" in request.json and "name" in request.json:
        image_file = request.json.get("image")
        mime_type = image_file.split(';')[0].split(':')[1]
        extension = mime_type.split('/')[1]
        if extension not in ALLOWED_EXTENSIONS:
            end_time = time.time()
            decode_time = end_time - start_time
            response_json = {
                'tiempo': utc_datatime(),
                'estado': int(UTIL_Four_One_Five),
                'metodo': "POST",
                "pedido": request.base_url,
                "server": SERVER,
                "baliza": uuid_baliza(),
                "acceso": request.host_url,
                "decode": decode_time}
            log_response(response_json, UTIL_Four_One_Five) 
            return jsonify(response_json), UTIL_Four_One_Five
        
        if ',' in image_file:
            image_data = image_file.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        return process_image(image_bytes, start_time)
    else:
        end_time = time.time()
        decode_time = end_time - start_time
        response_json = {
            'tiempo': utc_datatime(),
            'estado': int(UTIL_Four_Hundred),
            'metodo': "POST",
            "pedido": request.base_url,
            "server": SERVER,
            "baliza": uuid_baliza(),
            "acceso": request.host_url,
            "decode": decode_time}
        log_response(response_json, UTIL_Four_Hundred) 
        return jsonify(response_json), UTIL_Four_Hundred

@app.route('/images/<image_id>', methods=['GET'])
def get_image_info(image_id):
    start_time = time.time()
    print(request.headers)
    image_data = image_store.get(image_id)
    if not image_data:
        end_time = time.time()
        decode_time = end_time - start_time
        response_json = {
            'tiempo': utc_datatime(),
            'estado': int(UTIL_Four_Zero_Four),
            'metodo': "GET",
            "pedido": request.base_url,
            "server": SERVER,
            "baliza": uuid_baliza(),
            "acceso": request.host_url,
            "decode": decode_time}
        log_response(response_json, UTIL_Four_Zero_Four) 
        return jsonify(response_json), UTIL_Four_Zero_Four
    
    end_time = time.time()
    decode_time = end_time - start_time
    response_json = {
        'tiempo': utc_datatime(),
        'estado': int(UTIL_Two_Hundred),
        'metodo': "GET",
        'id_imagen': image_id,
        'informacion': image_data,
        "pedido": request.base_url,
        "server": SERVER,
        "baliza": uuid_baliza(),
        "acceso": request.host_url,
        "decode": decode_time}
    log_response(response_json, UTIL_Two_Hundred) 
    return jsonify(response_json), UTIL_Two_Hundred

if __name__ == '__main__':
    app.run(debug=True)
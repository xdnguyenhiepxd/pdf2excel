import os
from flask import Flask, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from flask_restful import reqparse
import requests
import json
from pdf2excel_mul import p2e
import string
import argparse

app = Flask(__name__)

#Tạo folder mới để lưu lại file pdf và các ảnh trong file pdf
HOME = os.getcwd()
DOWNLOAD_FILE = os.path.join(HOME, "upload_pdf")
SAVE_IMG = os.path.join(HOME, "save_img")
os.makedirs(DOWNLOAD_FILE, exist_ok=True)
os.makedirs(SAVE_IMG, exist_ok=True)

#Tạo hàm lọc dấu
def Locdau(input_str):
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ()'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy||'
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    s = s.translate(str.maketrans('', '', string.punctuation)).replace("|","").replace("--","-").replace(" ","_").lower()
    return s

@app.route("/pdf2excel", methods=["GET", "POST"])
def p2ex():
    #Nếu không truyền tham số là file sẽ trả về không có file
    if 'file' not in request.files:
        return jsonify(
                       message=f"No file part",
                       status=500
                       )
    file = request.files['file']
    
    #Nếu truyền file nhưng không có tên file sẽ trả về không chọn đúng file
    if file.filename == '':
        return jsonify(
                       message="No selected file",
                       status=500
                       )
    
    #Nếu truyền file nhưng không phải là 1 file PDF thì sẽ trả về sai file
    elif file.filename[-4:].lower() != '.pdf':
        return jsonify(
                       message="Wrong file",
                       status=500
                       )
    
    #Lọc bỏ những kí tự đặc biệt, dấu trong tên file và tạo ra file mới
    file_new = Locdau(file.filename[:-4]) + ".pdf"
    name = Locdau(file.filename[:-4])
    path_pdf = os.path.join(DOWNLOAD_FILE, file_new)
    
    
    
    #Lưu file vào folder đã tạo
    file.save(path_pdf)
    
    #Chạy hàm để chuyển đổi PDF sang Excel và trả về dữ liệu dạng json và tạo biến proces để cấu hình số lượng luồng muốn chạy
    parser = argparse.ArgumentParser()
    parser.add_argument("-p","--process", action="append", type=int, default = 0)
    args = parser.parse_args()
    print(args.process)
    proces = args.process[0]
    
    #Gọi hàm p2e và trả về data
    to_json = p2e(SAVE_IMG,name,path_pdf,proces)
    return to_json

if __name__ == "__main__":
    print(HOME)
    app.run(host="0.0.0.0", port=5556)


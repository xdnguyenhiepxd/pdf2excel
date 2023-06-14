#Cài đặt ubuntu 
FROM ubuntu:20.04

#Cài đặt sudo
RUN apt-get update && apt-get -y install sudo

#Khởi tạo package để cài đặt python 3.8
RUN sudo apt install software-properties-common -y
RUN sudo add-apt-repository ppa:deadsnakes/ppa -y
RUN sudo apt update --fix-missing

#Cài đặt python 3.8
RUN sudo apt install python3.8 -y

#Cấu hình auto select python 3.8
RUN sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1

#Cài đặt tesseract
RUN apt-get install -y tesseract-ocr

#Cài đặt pip cho python để tải các package
RUN sudo apt -y install python3-pip

#Cài đặt detectron2 cho phiên bản CPU
RUN pip3 install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.7/detectron2-0.3%2Bcpu-cp38-cp38-linux_x86_64.whl

#Copy file cài đặt các package lên môi trường
RUN sudo apt-get install -y poppler-utils
COPY requirements.txt requirements.txt

#Cài đặt các package
RUN pip3 install -r requirements.txt

#Cài đặt framework torch xử lý AI cho phiên bản CPU
RUN pip3 install torch==1.7.1+cpu torchvision==0.8.2+cpu torchaudio==0.7.2 -f https://download.pytorch.org/whl/torch_stable.html

#Cài đặt OpenCV
RUN sudo apt-get install python3-opencv -y

#Cấu hình lại Tesseract và Update model mới nhất cho phiên bản tiếng anh và tiếng việt
RUN cd /usr/share/tesseract-ocr/4.00
RUN rm -rf /usr/share/tesseract-ocr/4.00/tessdata
RUN mkdir /usr/share/tesseract-ocr/4.00/tessdata

RUN cd /
RUN mkdir -p /app

#Cài đặt Paddle OCR
RUN python3 -m pip install paddlepaddle -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip3 install paddlepaddle paddleocr
WORKDIR /app
#Cài đặt các môi trường cho Detectron2
COPY All_X152.yaml All_X152.yaml
COPY Base-RCNN-FPN.yaml Base-RCNN-FPN.yaml
COPY model_final.pth model_final.pth
COPY eng.traineddata eng.traineddata
COPY vie.traineddata vie.traineddata
RUN cp -b vie.traineddata /usr/share/tesseract-ocr/4.00/tessdata
RUN cp -b eng.traineddata /usr/share/tesseract-ocr/4.00/tessdata

#Copy file account info
COPY data_info.txt data_info.py

#Copy file chạy chương trình
COPY pdf2excel_mul.py pdf2excel_mul.py
COPY table_detection.py table_detection.py
COPY api_pdf2excel.py api_pdf2excel.py

CMD python3 api_pdf2excel.py None

import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import time
import os
from pdf2image import convert_from_path
import string
from save2excel import save
from table_detection import prediction
import multiprocessing as p
from functools import partial
import datetime
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang="en",use_angle_cls=True)
#Tạo hàm lọc dấu xử lý những kí tự sai Nguyễn Văn Hiệp ---(Locdau)--> NGUYEN VAN HIEP
def Locdau(input_str):
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ()'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy||'
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    s = s.translate(str.maketrans('', '', string.punctuation)).replace("|","").replace("--","-").upper()
    return s

def text_process(input_str):
    
    input_str = input_str.replace("S6","So").replace("s6","so").replace("C6","Co").replace("c6","co").replace("Ghi ng","Ghi no").replace("Phat sinh ng","Phat sinh no").replace("So tien ghi ng'","So tien ghi no").replace("so dwl'","So du").replace("giri","gui").replace("ghi ng","ghi no")
    return input_str


#Tạo hàm xử lý 1 hình ảnh để ghép vào tiến trình đa luồng
def multiprocess(crop):
    
    text = ""
    result = ocr.ocr(crop)
    for line in result:
        #print(line)
        for word in line:
            text += word[-1][0] + " "
    text = text_process(text).rstrip(" ")
    try:
        if text.replace(",","").replace(" ","").isnumeric() == True:
            text = text.replace(" ","")
    except:
        pass
    print(text)
    return text

#Tạo hàm chính đầu vào là PDF đầu ra là dữ liệu
def p2e(SAVE_IMG,name,pdf_path,proces):

    #Tạo list_all_text lưu tất cả giá trị của bảng
    #Tạo account_number lưu giá trị của account_number
    #Tạo start_time lưu thời gian bắt đầu tiến trình
    pages = convert_from_path(pdf_path)
    list_text_all=[]
    account_number = ""
    list_account = []
    start_time = datetime.datetime.now()
    
    #Vòng lặp lặp qua các page của PDF
    for i, page in enumerate(pages):
        
        #Chuyển đổi dữ liệu sang numpy array để OpenCV đọc được
        img_array = np.array(page)
        
        #Chuyển đổi màu ảnh từ RGB sang BGR để xử lý
        img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        #Tạo đường dẫn lưu ảnh
        path_img = os.path.join(SAVE_IMG,name + f"_{i+1}.jpg")
        
        #Lưu hình ảnh tránh tình trạng OpenCV đọc sai màu
        cv2.imwrite(path_img, img)
        
        #Đọc hình ảnh
        image = cv2.imread(path_img)
        
        #Gọi hàm prediction để lấy table trong từng page
        try:
            image,info_img = prediction(image,i)
        except:
            print("Erorr: ",i)
            continue
            #time.sleep(500)
        #cv2.imwrite(f"{name}_{i}.jpg", image)
        #cv2.imwrite(f"{name}_{i}_info.jpg", info_img)
        #Lấy thông tin account number
        if info_img != "None":
            text = pytesseract.image_to_string(info_img,lang="vie", config =r'-l vie --oem 3 --psm 6' ).split("\n")
            text_f = ""
            text_sc = ""
            with open("data_info.txt","r") as fl:
                value_search = fl.readlines()
                value_search = [vl_se.replace("\n","") for vl_se in value_search]
            print(text)
            try:
                for t in range(len(text)):
                    for value in value_search:
                        value = Locdau(value)
                       
                        if value in Locdau(text[t]):
                            text_f = Locdau(text[t]).split(" ")
                            print(text_f)
                            for f in text_f:
                                if f.isnumeric() == True and len(f.replace(" ","")) > 5:
                                    account_number = f
                                    #if account_number not in list_account:
                                        #list_account.append(account_number)
                                    print("account_number: ",account_number)
                                    break
                            if t < len(text) and account_number == "":
                                text_sc = Locdau(text[t+1]).split(" ")
                                for f in text_sc:
                                    if f.isnumeric() == True:
                                        account_number = f
                                        #if account_number not in list_account:
                                            #list_account.append(account_number)
                                        print("account_number 2: ",account_number)
                                        break
                            break
            except:
                pass
        print("Account Number: ",account_number)
        #time.sleep(500)
        img_height, img_width, _ = image.shape
        """
         - Do có những ngân hàng có đường nét đứt nên ta cần vẽ lại đường nét đứt thành đoạn thẳng
        """

        kernel1 = np.ones((3,3),np.uint8)
        kernel2 = np.ones((9,9),np.uint8)

        imgGray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        imgBW=cv2.threshold(imgGray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        img1=cv2.erode(imgBW, kernel1, iterations=1)
        img2=cv2.dilate(img1, kernel2, iterations=1)
        img3 = cv2.bitwise_and(imgBW,img2)
        img3= cv2.bitwise_not(img3)
        img4 = cv2.bitwise_and(imgBW,imgBW,mask=img3)
        imgLines= cv2.HoughLinesP(img4,5,np.pi/180,10, minLineLength = 500, maxLineGap = 15)
        try:
            for j in range(len(imgLines)):
                for x1,y1,x2,y2 in imgLines[j]:
                    cv2.line(image,(x1,y1),(x2,y2),(0,0,0),2)
        except:
            pass

        #cv2.imwrite(f"{name}_{i}_line.jpg", image)

        """
         - Khi có các đường thẳng đã vẽ ta tiến hành lọc các đường thẳng và nối dài chúng nếu chúng thiếu
         - Lấy những toạ độ với những ảnh đã có đủ line
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_bin = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        
        
        
        kernel_len_ver = max(10, img_height // 50)
        kernel_len_hor = max(10, img_width // 50)
        
        #Xử lý lấy ra các đường ngang và dọc
        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_len_ver))
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len_hor, 1)) 
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        
        
        #Xử lý lấy các đường dọc
        image_1 = cv2.erode(img_bin, ver_kernel, iterations=3)
        vertical_lines = cv2.dilate(image_1, ver_kernel, iterations=4)
        
        list_x = []
        value = 255
        
        for j in range(img_height):
            arr = np.array(vertical_lines[j,::])
            count = np.count_nonzero(arr == value)
            if count//img_height > 0.95:
                vertical_lines[j,::] = 0
        
        for j in range(img_width):
            arr = np.array(vertical_lines[::,j])
            check_line = arr == value
            if check_line.any() == True:
                vertical_lines[::,j]=255
                if len(list_x) >=1:
                    vl = list_x[-1]
                    if j - vl > 20:
                        list_x.append(j)
                else:
                    list_x.append(j)
        #cv2.imwrite(f"{name}_{i}_vertical_lines.jpg", vertical_lines)    
        list_x = sorted(list_x)
        
        #Xử lý lấy các đường ngang
        image_2 = cv2.erode(img_bin, hor_kernel, iterations=3)
        horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=4)
        list_y = []
        
        value = 255
        
        for j in range(img_height):
            arr = np.array(horizontal_lines[j,::])
            check_line = arr == value
            if check_line.any() == True:
                horizontal_lines[j,::]=255
                if len(list_y) >=1:
                    vl = list_y[-1]
                    if j - vl > 20:
                        list_y.append(j)
                        print("append",str(j))
                else:
                    list_y.append(j)
                    print("append elss",str(j))
        list_y = sorted(list_y)
        
        
        """
         - Khi đã vẽ lại các đường thẳng tiếp đến sẽ đếm số lượng các đường vì một số ngân hàng sẽ chỉ có đường ngang hoặc đường dọc
        """
        
        
        contours,hierarchy = cv2.findContours(vertical_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        len_vor = len(contours)
        print("len_vor = ",len_vor)
        
        
        contours,hierarchy = cv2.findContours(horizontal_lines,1,2)
        len_hor = len(contours)
        print("len_hor = ",len_hor)
       
       
        """
         - Khi đã có các line tiến hành lọc bỏ
        """
        
        img_hor= cv2.bitwise_not(horizontal_lines)
        img_ver= cv2.bitwise_not(vertical_lines)
        img_processing = cv2.bitwise_and(img_bin,img_bin,mask = img_hor)
        img_processing = cv2.bitwise_and(img_processing,img_processing,mask = img_ver)
        
        #Sửa chỗ này============================
        try:
            if len(list_y) >=1:
                if list_y[0] < 20:
                    img_processing = img_processing[list_y[0]:,::]
                    
                    image = image[list_y[0]:,::]
                    img_height, img_width, _ = image.shape
                if list_y[0] > img_height//2:
                    img_processing = img_processing[:list_y[0],::]
                    
                    image = image[:list_y[0],::]
                    img_height, img_width, _ = image.shape
        except:
            print("Erorr Crop Image: ",i)
           
           
        """
         - Kiểm tra đã đủ toạ độ chưa nếu chưa thì thêm các giá trị đọ dài của ảnh vào list_x và list_y
        """
        #Thêm các toạ độ x khi không đủ line
        if len(list_x) >=1:
            start = list_x[0]
            end = list_x[-1]
            if start - 0 > 50:
                list_x.append(0)
            if img_width - end > 50:
                list_x.append(img_width)
        
        list_x = sorted(list_x)
        
        #Thêm các toạ độ y khi không đủ line
        if len(list_y) >=1:
            start = list_y[0]
            end = list_y[-1]
            if start - 0 > 25:
                list_y.append(0)
            if img_height - end > 20:
                list_y.append(img_height)
                
        list_y = sorted(list_y)
        print(list_y)
        """
         - Bây giờ sẽ chia ra 2 loại: 
                                        + Loại 1: Những ảnh có đủ line
                                        + Loại 2: Những ảnh không có line hoặc những hình ảnh chỉ có ít line
         - Khởi tạo list_text_all để lưu tất cả dữ liệu trên table                               
        """
        
        #Tạo tiến trình đa luồng nếu proces = None thì sẽ sử dụng hết số lượng CPU 
        if proces == None:
            po = p.Pool()
            print("proces = None")
        else:
            po = p.Pool(processes=proces)
            print("proces = ",str(proces))
        #Tạo tham số config đầu ra của Pytesseract (OCR)
        myconfig = r'-l vie --psm 6'
        
        #Kiểm tra số lượng đường ngang và dọc nếu không đủ thì có nghĩa table không có table và phải vẽ lại đường kẻ
        if len_hor >=img_height//200 and len_vor >=4:
        
            #Tạo list_img lưu lại tất cả ô trong bảng
            #Tạo list_index để xử lý đầu ra theo từng dòng
            #Tạo list_text lưu lại tất cả các chữ trong cùng 1 hàng
            #Khi đã có list_x, list_y tiến hành crop trong image
            list_img = []
            list_index = []
            list_text = []
            
            #Xử lý lấy ô trong 1 hàng
            for y in range(len(list_y)-1):
                count = 0
                for x in range(len(list_x)-1):
                    crop_img = image[list_y[y]:list_y[y+1],list_x[x]:list_x[x+1]]
                    h_crop, w_crop, _ = crop_img.shape
                    #crop = cv2.resize(crop , (int(w_crop*1.5),int(h_crop*1.5)))
                    #crop_img=cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
                    #crop_img=cv2.threshold(crop_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                    #crop[list_y[y],list_x[x]] = 255
                    #crop = img_processing[list_y[y]:list_y[y+1],list_x[x]:list_x[x+1]]
                    #crop_img = 255 - crop_img
                    #cv2.imwrite(f"{name}_{i}_{y}_{x}_crop.jpg", crop_img) 
                    #cv2.imwrite(f"imgae.jpg", image) 
                    count += 1
                    list_img.append(crop_img)
                list_index.append(count)
            
            #Xử lý đa luồng
            list_text = po.map(multiprocess,list_img)
            
            #Xử lý lấy từng hàng trong list
            id_text = 0
            for id_t in list_index:
                text = list_text[id_text:id_text+id_t]
                id_text += id_t
                
                list_text_all.append(text)
            
            #Đóng đa luồng
            po.close()
        else:   
            list_x =[]
            list_y = []
            """
                - Làm nhoè và nối dài những đường ngang để lấy ra toạ độ x,y
                - Xoá bỏ những vùng không thuộc trong ô
                - Xoá bỏ các đường gần nhau
            """
            
            
            #Xử lý lấy các toạ độ y
            kernel2 = np.ones((6,6),np.uint8)
            
            #Làm nhoè ảnh
            img2=cv2.dilate(img_processing, kernel2, iterations=1)
            
            #Tạo ảnh mới
            img_horizontal = img2.copy()
            
            #Khởi tạo điểm dữ liệu màu trắng và nối liền các đường với nhau
            value = 255
            for j in range(img_height):
                arr = np.array(img_horizontal[j,::])
                check_line = arr == value
                if check_line.any() == True:
                    img_horizontal[j,::]=255
            
            #Tìm kiếm các toạ độ y và lưu vào list_y
            contours,hierarchy = cv2.findContours(img_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                x,y,w,h = cv2.boundingRect(c)
                list_y.append(y)
            
            #Sắp sếp lại mảng
            list_y = sorted(list_y)
            
            #Kiểm tra nếu thiếu toạ độ y cuối cùng thì thêm vào mảng
            if len(list_y) >=1:
                if img_height - list_y[-1] > 50:
                    list_y.append(img_height)
                
            for c in contours:
                x,y,w,h = cv2.boundingRect(c)
                #cv2.line(image, (0,y), (img_width,y), (0, 255, 0), 2)
            


            #Xử lý lấy các toạ độ x
            kernel2 = np.ones((img_width//200,img_width//200),np.uint8)

            #Làm nhoè ảnh
            img2=cv2.dilate(img_processing, kernel2, iterations=1)
            
            #Tạo ảnh mới
            img_ver = img2.copy() 
            
            #Khởi tạo điểm dữ liệu màu trắng và nối liền các đường với nhau
            value = 255
            for j in range(img_width):
                arr = np.array(img_ver[::,j])
                check_line = arr == value
                if check_line.any() == True:
                    img_ver[::,j]=255
            
            #Tìm kiếm các toạ độ y và lưu vào list_x     
            contours,hierarchy = cv2.findContours(img_ver, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                x,y,w,h = cv2.boundingRect(c)
                list_x.append(x)  

            #Sáp xếp lại mảng
            list_x = sorted(list_x)
            
            #Tạo mảng x remove để xoá những điểm không hợp lệ
            list_x_remove = []
            
            #Xử lý dữ liệu nếu x trước và x sau độ chênh lệch là 50 thì xoá khỏi mảng và tạo mảng mới
            list_x_new = []
            for j in range(len(list_x)-1):
                if list_x[j+1] - list_x[j] < 50 :
                    list_x_remove.append(list_x[j+1])
            for j in list_x:
                if j not in list_x_remove:
                    list_x_new.append(j)
            if len(list_x_new) >= 1:
                if img_width - list_x_new[-1] > 50:
                    list_x_new.append(img_width)
            
            #Crop một ô trong table và đưa vào OCR dự đoán và lưu lại trong list_text_all
            #Tạo list_img lưu lại tất cả ô trong bảng
            #Tạo list_index để xử lý đầu ra theo từng dòng
            #Tạo list_text lưu lại tất cả các chữ trong cùng 1 hàng
            #Khi đã có list_x, list_y tiến hành crop trong image
            list_img = []
            list_index = []
            list_text = []
            for y in range(len(list_y)-1):
                count = 0
                for x in range(len(list_x_new)-1):
                    crop_img = image[list_y[y]:list_y[y+1],list_x_new[x]:list_x_new[x+1]]
                    #crop_img=cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
                    #crop_img=cv2.threshold(crop_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                    #crop=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
                    #crop = img_processing[list_y[y]:list_y[y+1],list_x_new[x]:list_x_new[x+1]]
                    #crop_img = 255 - crop_img
                    count += 1
                    list_img.append(crop_img)
                list_index.append(count)
            
            #Xử lý đa luồng
            list_text = po.map(multiprocess,list_img)
            
            #Xử lý và lấy ra giá trị theo từng hàng
            id_text = 0
            for id_t in list_index:
                text = list_text[id_text:id_text+id_t]
                id_text += id_t
                
                list_text_all.append(text)
            
            #Đóng đa luồng
            po.close()
            
    
    #Tìm kiếm các phần tử giống nhau
    index = []
    for t in range(len(list_text_all)-1):
        vl = list_text_all[t]
        st = ""
        for v in vl:
            v = Locdau(v)
            st += v
        
        for a in range(t+1,len(list_text_all)):
            gt = list_text_all[a]
            st1 = ""
            for g in gt:
                g = Locdau(g)
                st1 += g
            if st == st1:
                index.append(a)
                #print(vl)
    
    #Tạo list mới bỏ qua những dữ liệu trùng lặp
    list_text_proces = []
    for t in range(len(list_text_all)):
        if t not in index:
            list_text_proces.append(list_text_all[t])
            
    #Lưu dữ liệu trong bảng vào Dictionary        
    to_json = {"account_number":account_number,
                "data":list_text_proces
                
              }
    #Hiển thị data      
    #print(to_json)
    
    #Get thời gian khi kết thúc xử lý xong 1 file PDF
    end_time = datetime.datetime.now()
    
    #Hiển thị thời gian bắt đầu và kết thúc tiến trình
    print(start_time)
    print(end_time)
    return to_json
    #save([],[],list_text_proces,out_file)
        
        
# path = "BIDV.pdf"
# p2e(path)
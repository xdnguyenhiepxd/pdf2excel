# pdf2excel
## 1. Tìm hiểu bài toán
Ngày nay, hầu hết các tài liệu được lưu ở dạng PDF tuy nhiên việc lưu sang định dạng PDF lại có điểm bất lợi khi chúng ta muốn truy suất thông tin. Vậy nên ta cần lấy dữ liệu cần lấy trong tệp PDF và lưu lại vào trong cơ sở dữ liệu điều này giúp cho việc tìm kiếm thông tin dễ dàng hơn.
<br/>
Các loại PDF bao gồm:
<br/>
• Dữ liệu có cấu trúc là các dữ liệu, thông tin được xác định trong các ô. Loại dữ liệu này dễ dàng lấy được thông tin.
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/567aef17-216d-4557-8fa0-f941ae3b6153)
<br/>
• Dữ liệu bán cấu trúc là các dữ liệu, thông tin không được xác định trong các ô. Loại dữ liệu này khó lấy được thông tin.
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/3d78c338-f808-4811-ba5f-a2af567cc94a)
<br/>
• Dữ liệu không có cấu trúc là các dữ liệu, thông tin không được xác định trong các ô và không đúng trong các dòng (spanning-cells). Loại dữ liệu này khó lấy được thông tin nhất.
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/4533887b-6000-456e-a109-b793b5f669c7)
## 2. Cách giải quyết
Để giải quyết bài toán này ta chia bài toán thành 2 phần: Table Detection và Table Recognition.
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/ef4f6900-353b-4858-881a-1ac4cbe6a258)
<br/>
<br/>
### 2.1 Table Detection
Hiện nay có rất nhiều các rút trích đặc trưng để lấy được table trong ảnh như sử dụng OpenCV hoặc mô hình AI. Tuy nhiên việc xử lý thuần bằng OpenCV chỉ đơn giản lấy được những table có đủ các đường kẻ ngang và dọc còn mô hình AI thì sẽ xử lý và lấy được table kể cả khi không có các đường ngang và dọc. Mô hình AI sử dụng cho bài toán này là Detectron2.
<br/>
• Đầu vào sẽ là một bức ảnh
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/72b73aa2-1704-44c7-809d-2cf906237c14)
<br/>
• Đầu ra sẽ là toạ độ và vùng được cho là table trong ảnh
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/5842ba8c-ffd4-4889-ba47-31f2d730729c)
<br/>
<br/>
Khi đã có table thì bước tiếp theo là sử dụng OpenCV tiến hành lọc bỏ những được ngang, dọc khi bị thiếu hoặc các đường nét đứt rồi vẽ lại với mục đích tìm ra các toạ độ x, y trong table rồi lấy từng ô dữ liệu trên trục x trước tiếp đến là trục y.
<br/>
<br/>
• Ví dụ: Ảnh ban đầu
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/518f5687-bea0-4307-af33-5af25325d671)
<br/>
<br/>
• Bước 1: Chuyển ảnh sang ngưỡng sáng
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/4af489bd-a527-4af0-8aea-b5bccdf5dac4)
<br/>
<br/>
• Bước 2: Tìm các đường kẻ ngang trong ảnh
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/6a6c8f15-be9f-4eb6-aebe-d3266b9ff20d)
<br/>
<br/>
• Bước 3: Tìm các đường kẻ dọc trong ảnh
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/fe3c881b-104f-4d07-8ecf-60710fd3af21)
<br/>
<br/>
Khi đã tìm các đường kẻ ngang, dọc đồng nghĩa có các toạ độ x, y thì tiến hành lấy từng ô trong bảng và tiến đến phần 2 là Table Recognition.
<br/>
<br/>
### 2.2 Table Recognition
Trong phần này để có thể đọc chữ trong ảnh ta sử dụng mô hình AI là Tesseract OCR và PaddleOCR với đầu vào là một hình ảnh và đầu ra là chữ trong hình ảnh đó.
<br/>
• Ví dụ: Ảnh đầu vào
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/b73bc2fc-acbc-4ce5-bae2-73503b2c2f9e)
<br/>
<br/>
• Dữ liệu đầu ra
<br/>
<br/>
![image](https://github.com/xdnguyenhiepxd/pdf2excel/assets/88564663/1329480c-81ca-4fcf-83e4-4a8a9eca60b7)
<br/>
<br/>
## 3. Cách sử dụng
• python3 api_pdf2excel.py None (None là giá trị số chỉ số lượng CPU chạy, nếu là None sẽ chạy tất cả các luồng CPU)
<br/>
• Trong danh sách file mình đã viết Dockerfile mọi người có thể chạy.

# speech_scoring_native
Speech Scoring API for Native
Hướng dẫn cài đặt:
Môi trường cài đặt: Ubuntu 16.04 hoặc Centos 7, python3.6.5, pip3.6. Hiện tại dự án đang sử dụng Centos nên sẽ hướng dẫn cài trên Centos.  

Bước 1: Cài đặt ffmpeg, chạy lần lượt các lệnh sau: 
+) Đầu tiên cài đặt epel-release: yum -y install epel-release
+) Cài đặt nux repo: rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
+) yum install ffmpeg ffmpeg-devel -y

Bước 2: Cài đặt flask và các libs sẽ sử dụng 
Cài đặt python3:
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
sudo yum update
sudo yum install -y python3u python3u-libs python3u-devel python3u-pip3

Cài đặt nltk, lần lượt chạy các lệnh sau:
pip3.6 install nltk
python3.6
import nltk
nltk.download('punkt')

Lần lượt cài đặt các libs sau để sử dụng với python. 
pip3.63.6install flask
pip3.63.6install werkzeug
pip3.63.6install speech_recognition
pip3.63.6install subprocess
pip3.63.6install json
pip3.63.6install difflib
pip3.63.6install diff_match_patch
pip3.63.6install nltk
pip3.63.6install ftfy
pip3.63.6install flask-mysql
	

Bước 3: Chạy API và cài đặt load balancing với nginx

Chạy lệnh này từ termianl để chuyển về UTF8 là mặc định trước khi khởi chạy service từ Flask.
export LANG=en_US.UTF-8 LANGUAGE=en_US.en LC_ALL=en_US.UTF-8

	Từ terminal, chạy lệnh “python" hoặc “python3” để kiểm tra chính xác xem version hiện tại đã là python3.6 hay chưa. 
	Nếu mặc định “python” version vẫn là 2.7, nếu thử “python3” mà không có thì tức là server chưa cài được phiên bản 3.6. Cần cài đặt lại. 
	Đi tới thư mục chứa code, chạy lệnh: nohup python server.py. 
	Nếu server báo thiếu module thì có thể sử dụng lệnh: pip3.63.6install + “tên thư viện thiếu". 

	Sau khi chạy code, API sẽ được serve ở “ip của sever":5000.(ví dụ: 172.20.28.184:5000). Để thay đổi port của API, có thể setup tại file server.py: app.run(host='0.0.0.0', port=8080, debug=False)

	File log của server sẽ được lưu tại server.log cùng với thư mục của folder code. 

	Trường hợp cần chịu tải lớn, chỉ cần clone file server.py, sau đó chạy với port khác, rồi tiến hành cài đặt trong nginx để load balancing là được. 

	Bước 4: Cài đặt trong nginx 
	Do api đang chạy tại port 5000 nên cần cài đặt trong file config của nginx để trỏ domain api về port 5000. 
Thêm block code này trong file config của domain api trong nginx.

  
  location / {

    proxy_pass       http://localhost:5000;
    proxy_set_header Host      $host;
    proxy_set_header X-Real-IP $remote_addr;
 }


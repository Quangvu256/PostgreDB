Dự án ETL Dữ liệu Thời tiết
Dự án này là một pipeline ETL (Extract-Transform-Load) tự động để thu thập dữ liệu thời tiết từ OpenWeatherMap API, xử lý và lưu trữ vào cơ sở dữ liệu PostgreSQL. Toàn bộ hệ thống được triển khai bằng Docker và điều phối bởi Apache Airflow.

🌟 Tính năng chính
Tự động hóa: Sử dụng Apache Airflow để lên lịch và tự động chạy quy trình ETL.

Dữ liệu thời tiết: Thu thập dữ liệu thời tiết hiện tại cho nhiều thành phố.

Quy trình 3 bước (ETL):

Extract: Gọi API OpenWeather để lấy dữ liệu thô và lưu vào một thư mục tạm thời.

Transform: Đọc dữ liệu thô, chuẩn hóa, và lưu dưới dạng file CSV.

Load: Đọc file CSV và chèn dữ liệu vào bảng trong PostgreSQL.

Triển khai đơn giản: Sử dụng Docker Compose để khởi động toàn bộ môi trường (PostgreSQL, Airflow Webserver, Scheduler).

Idempotent: Tích hợp logic ON CONFLICT DO NOTHING để đảm bảo dữ liệu không bị trùng lặp khi chạy lại pipeline.

📁 Cấu trúc thư mục
.
├── .env
├── dags
│   └── weather_etl_dag.py
├── raw_data/
├── supporting_scripts
│   ├── extract.py
│   ├── transform.py
│   └── load.py
└── docker-compose.yaml

dags/: Chứa file định nghĩa pipeline (DAG) của Airflow.

supporting_scripts/: Chứa các hàm Python hỗ trợ cho từng bước của quy trình ETL.

raw_data/: Thư mục lưu trữ dữ liệu JSON thô (do Docker volume mount).

.env: Chứa các biến môi trường quan trọng (API Key, thông tin database).

docker-compose.yaml: Định nghĩa các service Docker (Postgres, Airflow).

🚀 Hướng dẫn cài đặt và sử dụng
1. Yêu cầu
Docker và Docker Compose: Cần được cài đặt trên máy của bạn.

OpenWeatherMap API Key: Đăng ký tài khoản miễn phí tại OpenWeatherMap để lấy API key.

2. Cấu hình dự án
Mở file .env và thay thế giá trị OPENWEATHER_API_KEY bằng API key của bạn:

# API Key của bạn từ OpenWeatherMap
OPENWEATHER_API_KEY=YOUR_OPENWEATHER_API_KEY_HERE

Cập nhật đường dẫn trong file docker-compose.yaml (nếu cần):

Các volume mount trong file docker-compose.yaml hiện đang trỏ tới một đường dẫn cụ thể trên Windows (E:/Download/de_weather_project/...). Bạn nên thay đổi các đường dẫn này để khớp với đường dẫn thư mục dự án của bạn trên máy tính.

3. Khởi chạy dự án
Sử dụng terminal, điều hướng đến thư mục gốc của dự án và chạy lệnh sau:

docker-compose up -d --build

Lệnh này sẽ tải các image cần thiết, build và khởi chạy các service: postgres, airflow-init, airflow-webserver và airflow-scheduler.

Quá trình airflow-init sẽ tạo user admin/admin, tạo kết nối postgres_de_weather và set biến môi trường OPENWEATHER_API_KEY trong Airflow.

4. Truy cập giao diện Airflow
Mở trình duyệt và truy cập vào địa chỉ:

http://localhost:8080

Bạn có thể đăng nhập bằng tài khoản:

Username: admin

Password: admin

Trên giao diện Airflow, bạn sẽ thấy một DAG mới có tên weather_data_etl_v2. DAG này được lên lịch chạy 5 phút một lần để thu thập dữ liệu thời tiết.

5. Xem dữ liệu
Sau khi DAG chạy thành công, bạn có thể truy cập vào database PostgreSQL để xem dữ liệu đã được nạp.

Thông tin kết nối Postgres:

Host: localhost

Port: 5555

User: airflow

Password: airflow

Database: airflow

Sử dụng một SQL client như DBeaver hoặc pgAdmin, bạn có thể chạy truy vấn sau để kiểm tra dữ liệu:

SELECT * FROM weather_data;

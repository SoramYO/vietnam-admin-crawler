# Dữ liệu Hành chính Việt Nam

Ứng dụng crawl và hiển thị dữ liệu hành chính Việt Nam với giao diện web đẹp và trực quan.

## Tính năng

### 🕷️ Crawler (main.py)
- Crawl dữ liệu từ bảng HTML với thuộc tính `border="1" cellspacing="0" cellpadding="0" width="100%"`
- Tự động phân loại tỉnh/thành phố và xã/phường
- Xử lý dữ liệu số (dân số, diện tích, số lượng đơn vị hành chính)
- Xuất dữ liệu thành file JSON có cấu trúc
- Loại bỏ dòng "CẢ NƯỚC" và xử lý lỗi định dạng

### 🌐 Web Interface (app.py)
- Giao diện web hiện đại và responsive
- Tìm kiếm tỉnh/thành phố và xã/phường
- Hiển thị thống kê tổng quan
- Lọc dữ liệu theo tỉnh
- Hiển thị kết quả dạng bảng đẹp mắt

## Cài đặt

1. **Cài đặt thư viện Python:**
```bash
pip install -r requirements.txt
```

2. **Chạy crawler để lấy dữ liệu:**
```bash
python main.py
```
- Nhập URL của trang web chứa bảng dữ liệu
- Dữ liệu sẽ được lưu thành các file JSON

3. **Chạy web interface:**
```bash
python app.py
```
- Mở trình duyệt và truy cập: `http://localhost:5000`

## Cấu trúc dữ liệu

### Tỉnh/Thành phố
```json
{
  "stt": 1,
  "ma_tinh": "01",
  "ten_tinh": "THÀNH PHỐ HÀ NỘI",
  "tong_dvhc_cap_xa": 579,
  "so_xa": 386,
  "so_phuong": 193,
  "dac_khu": 0,
  "mien_nui": 0,
  "vung_cao": 0,
  "hai_dao": 0,
  "dien_tich_km2": 3359.8,
  "dan_so": 8807523
}
```

### Xã/Phường
```json
{
  "stt": 1,
  "ma_tinh": "01",
  "ten_tinh": "THÀNH PHỐ HÀ NỘI",
  "ten_xa_phuong": "Phường Phúc Xá",
  "loai_don_vi": "Phường",
  "tong_dvhc_cap_xa": 1,
  "so_xa": 0,
  "so_phuong": 1,
  "dac_khu": 0,
  "mien_nui": 0,
  "vung_cao": 0,
  "hai_dao": 0,
  "dien_tich_km2": 0.52,
  "dan_so": 12000
}
```

## Tính năng Web Interface

### 📊 Thống kê tổng quan
- Tổng số tỉnh/thành phố
- Tổng số xã/phường/thị trấn
- Tổng diện tích cả nước
- Tổng dân số cả nước

### 🔍 Tìm kiếm
- **Tỉnh/Thành phố**: Tìm theo tên hoặc mã số
- **Xã/Phường**: Tìm theo tên, có thể lọc theo tỉnh
- Tìm kiếm real-time với API
- Hiển thị kết quả dạng bảng có sắp xếp

### 📱 Responsive Design
- Giao diện tương thích với mobile
- Thiết kế hiện đại với gradient và animation
- Font chữ Inter cho trải nghiệm đọc tốt

## Cấu trúc file

```
crawdata/
├── main.py              # Crawler chính
├── app.py               # Web application
├── requirements.txt     # Dependencies
├── README.md           # Hướng dẫn
├── templates/
│   └── index.html      # Giao diện web
└── *.json              # Dữ liệu được crawl
```

## API Endpoints

- `GET /` - Trang chủ
- `GET /api/search?q=<query>&type=<provinces|communes>&province=<filter>` - Tìm kiếm
- `GET /api/provinces` - Lấy danh sách tỉnh
- `GET /api/stats` - Lấy thống kê

## Lưu ý

- Đảm bảo có file JSON dữ liệu trước khi chạy web interface
- Web interface sẽ tự động load file JSON mới nhất
- Crawler chỉ hoạt động với bảng có định dạng cụ thể
- Dữ liệu được format theo chuẩn Việt Nam

## Tác giả

Ứng dụng được phát triển để tra cứu thông tin hành chính Việt Nam một cách nhanh chóng và trực quan. 
import requests
from bs4 import BeautifulSoup
import json
import re
import time

class VietnamAdminCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def clean_text(self, text):
        """Làm sạch text, loại bỏ ký tự thừa"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def parse_number(self, text):
        """Chuyển đổi text thành số, xử lý đúng kiểu Việt Nam (dấu phẩy là thập phân, dấu chấm là nghìn)"""
        try:
            if not text:
                return None
            cleaned = text.strip()
            # Xóa dấu chấm (nghìn), thay dấu phẩy thành dấu chấm (thập phân)
            cleaned = cleaned.replace('.', '').replace(',', '.')
            if cleaned == '-' or cleaned == '':
                return None
            return float(cleaned) if '.' in cleaned else int(cleaned)
        except:
            return None
    
    def crawl_table(self, url):
        """Crawl bảng từ URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm bảng cụ thể với thuộc tính đã chỉ định
            table = soup.find('table', {
                'border': '1',
                'cellspacing': '0', 
                'cellpadding': '0',
                'width': '100%'
            })
            
            if not table:
                print("Không tìm thấy bảng với thuộc tính: border='1' cellspacing='0' cellpadding='0' width='100%'")
                print("Đang tìm tất cả các bảng trong trang...")
                tables = soup.find_all('table')
                print(f"Tìm thấy {len(tables)} bảng trong trang web")
                
                # Hiển thị thông tin về các bảng tìm thấy
                for i, t in enumerate(tables):
                    attrs = t.attrs
                    print(f"Bảng {i+1}: {attrs}")
                
                return None
            
            print("✓ Tìm thấy bảng đúng định dạng!")
            rows = table.find_all('tr')
            print(f"Bảng có {len(rows)} dòng")
            
            # Debug cấu trúc bảng
            self.debug_table_structure(table)
                
            return self.parse_table(table)
            
        except Exception as e:
            print(f"Lỗi khi crawl dữ liệu: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def debug_table_structure(self, table):
        """Debug cấu trúc bảng để tìm vấn đề"""
        rows = table.find_all('tr')
        print(f"\n=== DEBUG TABLE STRUCTURE ===")
        print(f"Tổng số dòng: {len(rows)}")
        
        for i, row in enumerate(rows[:10]):  # Chỉ xem 10 dòng đầu
            cells = row.find_all(['th', 'td'])
            cell_texts = [self.clean_text(cell.get_text()) for cell in cells]
            print(f"Dòng {i+1}: {len(cells)} cột - {cell_texts[:5]}...")  # Chỉ hiển thị 5 cột đầu
        
        if len(rows) > 10:
            print(f"... và {len(rows) - 10} dòng khác")
    
    def parse_table(self, table):
        """Parse bảng HTML thành dữ liệu có cấu trúc"""
        rows = table.find_all('tr')
        if not rows:
            return None
            
        # Tìm header row
        header_row = None
        for i, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 10:  # Bảng có nhiều cột
                header_text = ' '.join([self.clean_text(cell.get_text()) for cell in cells])
                if 'Tên đơn vị hành chính' in header_text or 'Mã số Tỉnh' in header_text:
                    header_row = row
                    break
        
        if not header_row:
            print("Không tìm thấy header của bảng")
            return None
            
        # Parse dữ liệu
        provinces = []
        communes = []
        ca_nuoc_row = None  # Lưu dòng CẢ NƯỚC nếu có
        current_province = None
        processed_rows = 0
        
        # Bắt đầu từ row sau header
        start_idx = rows.index(header_row) + 1
        
        for i, row in enumerate(rows[start_idx:], start_idx):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 10:
                continue
                
            # Đảm bảo có đủ cột dữ liệu
            row_data = []
            for cell in cells:
                row_data.append(self.clean_text(cell.get_text()))
            
            # Bổ sung các cột còn thiếu nếu cần
            while len(row_data) < 13:
                row_data.append('')
            
            # Bỏ qua các dòng trống hoặc không có dữ liệu
            if not any(row_data) or (len(row_data) > 2 and row_data[2] == ''):
                continue
            
            # Kiểm tra nếu là dòng tỉnh/thành phố
            name_cell = cells[2] if len(cells) > 2 else None  # Cột tên đơn vị
            is_province = False
            
            # Các dấu hiệu nhận biết dòng tỉnh:
            # 1. Có thẻ <b> (in đậm)
            # 2. Tên chứa "THÀNH PHỐ", "TỈNH"
            # 3. Có tổng số ĐVHC cấp xã > 10 (tỉnh thường có nhiều xã/phường)
            # 4. Cột tỉnh/thành phố để trống
            if name_cell:
                name_text = row_data[2] if len(row_data) > 2 else ''
                has_bold = bool(name_cell.find('b'))
                contains_province_keywords = ('THÀNH PHỐ' in name_text.upper() or 'TỈNH' in name_text.upper())
                has_many_communes = (len(row_data) > 4 and self.parse_number(row_data[4]) and self.parse_number(row_data[4]) > 10)
                province_column_empty = (len(row_data) > 3 and row_data[3] == '')
                is_ca_nuoc = 'CẢ NƯỚC' in name_text.upper()
                is_province = (has_bold or contains_province_keywords or 
                             (has_many_communes and province_column_empty)) and not is_ca_nuoc
            
            if is_province:
                # Dòng tỉnh/thành phố
                province_data = {
                    'stt': self.parse_number(row_data[0]) if len(row_data) > 0 else None,
                    'ma_tinh': row_data[1] if len(row_data) > 1 and row_data[1] and row_data[1] != '-' else None,
                    'ten_tinh': row_data[2] if len(row_data) > 2 else '',
                    'tong_dvhc_cap_xa': self.parse_number(row_data[4]) if len(row_data) > 4 else None,
                    'so_xa': self.parse_number(row_data[5]) if len(row_data) > 5 else None,
                    'so_phuong': self.parse_number(row_data[6]) if len(row_data) > 6 else None,
                    'dac_khu': self.parse_number(row_data[7]) if len(row_data) > 7 else None,
                    'mien_nui': self.parse_number(row_data[8]) if len(row_data) > 8 else None,
                    'vung_cao': self.parse_number(row_data[9]) if len(row_data) > 9 else None,
                    'hai_dao': self.parse_number(row_data[10]) if len(row_data) > 10 else None,
                    'dien_tich_km2': self.parse_number(row_data[11]) if len(row_data) > 11 else None,
                    'dan_so': self.parse_number(row_data[12]) if len(row_data) > 12 else None
                }
                
                # Chỉ thêm nếu có tên tỉnh hợp lệ, không phải số, không phải 'CẢ NƯỚC'
                if (
                    province_data['ten_tinh'] 
                    and province_data['ten_tinh'] != 'Tên đơn vị hành chính'
                    and not province_data['ten_tinh'].replace('.', '', 1).isdigit()
                    and 'CẢ NƯỚC' not in province_data['ten_tinh'].upper()
                ):
                    provinces.append(province_data)
                    current_province = province_data
                    processed_rows += 1
                    print(f"Đã xử lý tỉnh: {province_data['ten_tinh']}")
                
                # Nếu là dòng CẢ NƯỚC thì lấy đúng các giá trị tổng từ các cột (bắt đầu từ cột 4 trở đi)
                if is_ca_nuoc:
                    # Tìm vị trí bắt đầu của các số (sau colspan)
                    first_num_idx = 0
                    for idx in range(3, len(row_data)):
                        if self.parse_number(row_data[idx]) is not None:
                            first_num_idx = idx
                            break
                    ca_nuoc_row = {
                        'ten': name_text,
                        'tong_dvhc_cap_xa': self.parse_number(row_data[first_num_idx]) if len(row_data) > first_num_idx else None,
                        'so_xa': self.parse_number(row_data[first_num_idx+1]) if len(row_data) > first_num_idx+1 else None,
                        'so_phuong': self.parse_number(row_data[first_num_idx+2]) if len(row_data) > first_num_idx+2 else None,
                        'dac_khu': self.parse_number(row_data[first_num_idx+3]) if len(row_data) > first_num_idx+3 else None,
                        'mien_nui': self.parse_number(row_data[first_num_idx+4]) if len(row_data) > first_num_idx+4 else None,
                        'vung_cao': self.parse_number(row_data[first_num_idx+5]) if len(row_data) > first_num_idx+5 else None,
                        'hai_dao': self.parse_number(row_data[first_num_idx+6]) if len(row_data) > first_num_idx+6 else None,
                        'dien_tich_km2': self.parse_number(row_data[first_num_idx+7]) if len(row_data) > first_num_idx+7 else None,
                        'dan_so': self.parse_number(row_data[first_num_idx+8]) if len(row_data) > first_num_idx+8 else None
                    }
                    continue  # Không thêm vào provinces
                
            else:
                # Dòng xã/phường/thị trấn
                if current_province and len(row_data) > 2 and row_data[2]:
                    commune_data = {
                        'stt': self.parse_number(row_data[0]) if len(row_data) > 0 else None,
                        'ma_tinh': current_province['ma_tinh'],
                        'ten_tinh': current_province['ten_tinh'],
                        'ten_xa_phuong': row_data[2],
                        'loai_don_vi': row_data[3] if len(row_data) > 3 and row_data[3] else None,
                        'tong_dvhc_cap_xa': self.parse_number(row_data[4]) if len(row_data) > 4 else None,
                        'so_xa': self.parse_number(row_data[5]) if len(row_data) > 5 else None,
                        'so_phuong': self.parse_number(row_data[6]) if len(row_data) > 6 else None,
                        'dac_khu': self.parse_number(row_data[7]) if len(row_data) > 7 else None,
                        'mien_nui': self.parse_number(row_data[8]) if len(row_data) > 8 else None,
                        'vung_cao': self.parse_number(row_data[9]) if len(row_data) > 9 else None,
                        'hai_dao': self.parse_number(row_data[10]) if len(row_data) > 10 else None,
                        'dien_tich_km2': self.parse_number(row_data[11]) if len(row_data) > 11 else None,
                        'dan_so': self.parse_number(row_data[12]) if len(row_data) > 12 else None
                    }
                    communes.append(commune_data)
                    processed_rows += 1
                    
                    # In tiến trình mỗi 100 dòng
                    if processed_rows % 100 == 0:
                        print(f"Đã xử lý {processed_rows} dòng...")
        
        return {
            'provinces': provinces,
            'communes': communes,
            'ca_nuoc': ca_nuoc_row
        }
    
    def save_to_json(self, data, filename_prefix='vietnam_admin'):
        """Lưu dữ liệu thành file JSON"""
        if not data:
            return
            
        # Lưu dữ liệu tỉnh
        provinces_file = f'{filename_prefix}_provinces.json'
        with open(provinces_file, 'w', encoding='utf-8') as f:
            json.dump(data['provinces'], f, ensure_ascii=False, indent=2)
        
        # Lưu dữ liệu xã/phường
        communes_file = f'{filename_prefix}_communes.json'
        with open(communes_file, 'w', encoding='utf-8') as f:
            json.dump(data['communes'], f, ensure_ascii=False, indent=2)
        
        # Lưu dữ liệu tổng hợp
        summary_file = f'{filename_prefix}_summary.json'
        summary = {
            'thong_ke': {
                'tong_so_tinh': len(data['provinces']),
                'tong_so_xa_phuong': len(data['communes']),
                'ngay_crawl': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'danh_sach_tinh': [{'ma_tinh': p['ma_tinh'], 'ten_tinh': p['ten_tinh']} for p in data['provinces']],
            'ca_nuoc': data.get('ca_nuoc')
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== KẾT QUẢ CRAWL ===")
        print(f"✓ Đã lưu {len(data['provinces'])} tỉnh/thành phố vào {provinces_file}")
        print(f"✓ Đã lưu {len(data['communes'])} xã/phường/thị trấn vào {communes_file}")
        print(f"✓ Đã lưu thống kê tổng quan vào {summary_file}")
        
        # Thống kê chi tiết
        print("\n=== CHI TIẾT DIỆN TÍCH TỪNG TỈNH ===")
        for p in data['provinces']:
            print(f"{p['ten_tinh']}: {p['dien_tich_km2']}")
        total_area = sum(p['dien_tich_km2'] for p in data['provinces'] if p['dien_tich_km2'] is not None)
        total_population = sum(p['dan_so'] for p in data['provinces'] if p['dan_so'] is not None)
        
        print(f"\n=== THỐNG KÊ ===")
        print(f"• Tổng diện tích: {total_area:,.1f} km²")
        print(f"• Tổng dân số: {total_population:,} người")
        if total_area > 0:
            print(f"• Mật độ dân số trung bình: {total_population/total_area:.0f} người/km²")
    
    def crawl_from_html_content(self, html_content):
        """Parse trực tiếp từ HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        if table:
            return self.parse_table(table)
        return None

# Sử dụng crawler
def main():
    crawler = VietnamAdminCrawler()
    
    print("=== VIETNAM ADMINISTRATIVE UNITS CRAWLER ===")
    print("Công cụ crawl dữ liệu đơn vị hành chính Việt Nam\n")
    
    # Nhập URL từ người dùng
    url = input("Nhập URL của trang web chứa bảng dữ liệu: ").strip()
    
    if not url:
        print("❌ Vui lòng nhập URL hợp lệ!")
        return
    
    print(f"\n🔄 Đang crawl dữ liệu từ: {url}")
    print("⏳ Vui lòng đợi...")
    
    try:
        data = crawler.crawl_table(url)
        
        if data and (data['provinces'] or data['communes']):
            # Lưu dữ liệu
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename_prefix = f'vietnam_admin_{timestamp}'
            
            crawler.save_to_json(data, filename_prefix)
            
            # Hiển thị một vài ví dụ
            if data['provinces']:
                print(f"\n=== VÍ DỤ TỈNH/THÀNH PHỐ (5 đầu tiên) ===")
                for i, province in enumerate(data['provinces'][:5], 1):
                    dan_so = province['dan_so']
                    dan_so_str = f"{dan_so:,}" if dan_so is not None else "N/A"
                    print(f"{i}. {province['ten_tinh']} - Mã: {province['ma_tinh']} - Dân số: {dan_so_str}")
            
            if data['communes']:
                print(f"\n=== VÍ DỤ XÃ/PHƯỜNG (5 đầu tiên) ===")
                for i, commune in enumerate(data['communes'][:5], 1):
                    print(f"{i}. {commune['ten_xa_phuong']} - {commune['ten_tinh']}")
                    
        else:
            print("❌ Không tìm thấy dữ liệu hợp lệ trong bảng!")
            print("💡 Kiểm tra lại URL hoặc cấu trúc bảng")
            print("💡 Có thể bảng không có đúng định dạng hoặc không chứa dữ liệu hành chính")
            
    except Exception as e:
        print(f"❌ Lỗi khi crawl dữ liệu: {e}")
        print("💡 Kiểm tra lại URL và kết nối internet")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

# Hướng dẫn sử dụng:
# 1. Cài đặt thư viện: pip install requests beautifulsoup4
# 2. Thay YOUR_URL_HERE bằng URL thực tế của trang web
# 3. Chạy script: python vietnam_admin_crawler.py
# 4. Kết quả sẽ được lưu thành 2 file JSON: vietnam_admin_provinces.json và vietnam_admin_communes.json
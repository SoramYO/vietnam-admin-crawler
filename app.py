from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

class VietnamAdminData:
    def __init__(self):
        self.provinces = []
        self.communes = []
        self.load_data()
    
    def load_data(self):
        """Load data from JSON files"""
        try:
            # Tìm file JSON mới nhất
            json_files = [f for f in os.listdir('.') if f.startswith('vietnam_admin_') and f.endswith('_provinces.json')]
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                timestamp = latest_file.replace('vietnam_admin_', '').replace('_provinces.json', '')
                
                # Load provinces
                provinces_file = f'vietnam_admin_{timestamp}_provinces.json'
                if os.path.exists(provinces_file):
                    with open(provinces_file, 'r', encoding='utf-8') as f:
                        self.provinces = json.load(f)
                
                # Load communes
                communes_file = f'vietnam_admin_{timestamp}_communes.json'
                if os.path.exists(communes_file):
                    with open(communes_file, 'r', encoding='utf-8') as f:
                        self.communes = json.load(f)
                
                print(f"✓ Đã load {len(self.provinces)} tỉnh và {len(self.communes)} xã/phường")
            else:
                print("❌ Không tìm thấy file dữ liệu JSON")
        except Exception as e:
            print(f"❌ Lỗi khi load dữ liệu: {e}")
    
    def search_provinces(self, query):
        """Tìm kiếm tỉnh/thành phố"""
        if not query:
            return self.provinces[:20]  # Trả về 20 tỉnh đầu tiên
        
        query = query.lower()
        results = []
        for province in self.provinces:
            if (query in province['ten_tinh'].lower() or 
                (province['ma_tinh'] and query in str(province['ma_tinh']).lower())):
                results.append(province)
        return results
    
    def search_communes(self, query, province_filter=None):
        """Tìm kiếm xã/phường"""
        if not query:
            return self.communes[:50]  # Trả về 50 xã đầu tiên
        
        query = query.lower()
        results = []
        for commune in self.communes:
            if province_filter and commune['ten_tinh'] != province_filter:
                continue
            if (query in commune['ten_xa_phuong'].lower() or 
                query in commune['ten_tinh'].lower()):
                results.append(commune)
        return results
    
    def get_province_stats(self):
        """Lấy thống kê tổng quan"""
        if not self.provinces:
            return {}
        
        total_area = sum(p['dien_tich_km2'] for p in self.provinces if p['dien_tich_km2'] is not None)
        total_population = sum(p['dan_so'] for p in self.provinces if p['dan_so'] is not None)
        total_communes = len(self.communes)
        
        return {
            'total_provinces': len(self.provinces),
            'total_communes': total_communes,
            'total_area': total_area,
            'total_population': total_population,
            'avg_density': total_population / total_area if total_area > 0 else 0
        }

# Khởi tạo dữ liệu
data_manager = VietnamAdminData()

@app.route('/')
def index():
    """Trang chủ"""
    stats = data_manager.get_province_stats()
    return render_template('index.html', stats=stats)

@app.route('/api/search')
def search():
    """API tìm kiếm"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'provinces')  # provinces hoặc communes
    province_filter = request.args.get('province', '')
    
    if search_type == 'provinces':
        results = data_manager.search_provinces(query)
    else:
        results = data_manager.search_communes(query, province_filter)
    
    return jsonify({
        'results': results,
        'count': len(results),
        'query': query
    })

@app.route('/api/provinces')
def get_provinces():
    """API lấy danh sách tỉnh"""
    return jsonify(data_manager.provinces)

@app.route('/api/stats')
def get_stats():
    """API lấy thống kê"""
    return jsonify(data_manager.get_province_stats())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
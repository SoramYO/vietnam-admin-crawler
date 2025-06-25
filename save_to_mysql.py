import mysql.connector

def save_to_mysql(data, mysql_config):
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()

    # Tạo bảng provinces nếu chưa có
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS provinces (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ma_tinh VARCHAR(10),
            ten_tinh VARCHAR(255),
            tong_dvhc_cap_xa INT,
            so_xa INT,
            so_phuong INT,
            dac_khu INT,
            mien_nui INT,
            vung_cao INT,
            hai_dao INT,
            dien_tich_km2 FLOAT,
            dan_so BIGINT
        )
    """)
    cursor.execute("TRUNCATE TABLE provinces")  # Xóa dữ liệu cũ nếu muốn

    for p in data['provinces']:
        cursor.execute("""
            INSERT INTO provinces (ma_tinh, ten_tinh, tong_dvhc_cap_xa, so_xa, so_phuong, dac_khu, mien_nui, vung_cao, hai_dao, dien_tich_km2, dan_so)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            p['ma_tinh'], p['ten_tinh'], p['tong_dvhc_cap_xa'], p['so_xa'], p['so_phuong'],
            p['dac_khu'], p['mien_nui'], p['vung_cao'], p['hai_dao'], p['dien_tich_km2'], p['dan_so']
        ))

    # Tạo bảng communes nếu chưa có
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS communes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ma_tinh VARCHAR(10),
            ten_tinh VARCHAR(255),
            ten_xa_phuong VARCHAR(255),
            loai_don_vi VARCHAR(50),
            tong_dvhc_cap_xa INT,
            so_xa INT,
            so_phuong INT,
            dac_khu INT,
            mien_nui INT,
            vung_cao INT,
            hai_dao INT,
            dien_tich_km2 FLOAT,
            dan_so BIGINT
        )
    """)
    cursor.execute("TRUNCATE TABLE communes")  # Xóa dữ liệu cũ nếu muốn

    for c in data['communes']:
        cursor.execute("""
            INSERT INTO communes (ma_tinh, ten_tinh, ten_xa_phuong, loai_don_vi, tong_dvhc_cap_xa, so_xa, so_phuong, dac_khu, mien_nui, vung_cao, hai_dao, dien_tich_km2, dan_so)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            c['ma_tinh'], c['ten_tinh'], c['ten_xa_phuong'], c['loai_don_vi'], c['tong_dvhc_cap_xa'],
            c['so_xa'], c['so_phuong'], c['dac_khu'], c['mien_nui'], c['vung_cao'], c['hai_dao'],
            c['dien_tich_km2'], c['dan_so']
        ))

    conn.commit()
    cursor.close()
    conn.close()

# Ví dụ sử dụng:
# mysql_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'your_password',
#     'database': 'your_db'
# }
# save_to_mysql(data, mysql_config)
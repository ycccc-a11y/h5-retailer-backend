"""
许可证号码搜索API
GET /api/search/{license_number}
"""
from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db_utils import get_db_connection, detect_retailers_table_name, DETECTED_LAT_COLUMN

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # 从路径中提取许可证号
            path_parts = self.path.split('/')
            license_number = None
            for i, part in enumerate(path_parts):
                if part == 'search' and i + 1 < len(path_parts):
                    license_number = path_parts[i + 1]
                    # 移除查询参数
                    if '?' in license_number:
                        license_number = license_number.split('?')[0]
                    break
            
            if not license_number:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': '缺少许可证号'}, ensure_ascii=False).encode('utf-8'))
                return
            
            # 连接数据库
            connection = get_db_connection()
            if not connection:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': '数据库连接失败'}, ensure_ascii=False).encode('utf-8'))
                return
            
            try:
                # 自动检测表名
                table_name = detect_retailers_table_name(connection)
                if not table_name or not DETECTED_LAT_COLUMN:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': '未找到包含必要列的表'}, ensure_ascii=False).encode('utf-8'))
                    return
                
                # 查询数据
                import pymysql
                with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                    query = f"""
                        SELECT 许可证号, 客户名称, 法人姓名, 经营地址, 经度, `{DETECTED_LAT_COLUMN}` as 纬度
                        FROM `{table_name}`
                        WHERE 许可证号 = %s
                        LIMIT 1
                    """
                    cursor.execute(query, (license_number,))
                    result = cursor.fetchone()
                    
                    if result:
                        response_data = {
                            'license_number': result.get('许可证号', ''),
                            'customer_name': result.get('客户名称', ''),
                            'legal_person': result.get('法人姓名', ''),
                            'address': result.get('经营地址', ''),
                            'longitude': float(result.get('经度', 0)),
                            'latitude': float(result.get('纬度', 0))
                        }
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
                    else:
                        self.send_response(404)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'error': '未找到该许可证号'}, ensure_ascii=False).encode('utf-8'))
            finally:
                connection.close()
                
        except Exception as e:
            print(f"错误: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

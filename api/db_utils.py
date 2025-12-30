"""
数据库连接工具模块
"""
import pymysql
import os

# 从环境变量读取数据库配置（用于Vercel部署）
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'locationnt'),
    'charset': 'utf8mb4',
    'connect_timeout': 10,
    'read_timeout': 30,
    'write_timeout': 30,
    'ssl': {'ssl_mode': 'PREFERRED'},
    'ssl_verify_cert': False,
    'ssl_verify_identity': False
}

# 缓存自动识别到的表名与纬度列名
DETECTED_TABLE_NAME = 'tobacco_retailers'
DETECTED_LAT_COLUMN = '维度'

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def detect_retailers_table_name(connection):
    """自动检测包含必要列的表名"""
    global DETECTED_TABLE_NAME, DETECTED_LAT_COLUMN
    if DETECTED_TABLE_NAME and DETECTED_LAT_COLUMN:
        return DETECTED_TABLE_NAME
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                """
                SELECT TABLE_NAME
                FROM information_schema.columns
                WHERE TABLE_SCHEMA=%s
                  AND COLUMN_NAME IN ('许可证号','客户名称','经营地址','经度')
                GROUP BY TABLE_NAME
                HAVING COUNT(DISTINCT COLUMN_NAME) >= 4
                LIMIT 1
                """,
                (DB_CONFIG['database'],)
            )
            row = cursor.fetchone()
            if row and 'TABLE_NAME' in row:
                DETECTED_TABLE_NAME = row['TABLE_NAME']
                # 进一步检测纬度列名
                cursor.execute(
                    """
                    SELECT COLUMN_NAME
                    FROM information_schema.columns
                    WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME IN ('纬度','维度')
                    LIMIT 1
                    """,
                    (DB_CONFIG['database'], DETECTED_TABLE_NAME)
                )
                lat_row = cursor.fetchone()
                DETECTED_LAT_COLUMN = lat_row['COLUMN_NAME'] if lat_row and 'COLUMN_NAME' in lat_row else None
                return DETECTED_TABLE_NAME
    except Exception as e:
        print(f"自动检测表名失败: {repr(e)}")
    return None

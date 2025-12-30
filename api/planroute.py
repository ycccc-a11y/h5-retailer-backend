"""
路线规划API - 使用Flask
POST /api/planroute
"""
from flask import Flask, request, jsonify
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from amap_utils import plan_route_with_amap

app = Flask(__name__)

@app.route('/api/planroute', methods=['POST', 'OPTIONS'])
def plan_route():
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        request_data = request.get_json()
        
        points = request_data.get('points', [])
        strategy = request_data.get('strategy', '1')
        
        if not points or len(points) < 2:
            response = jsonify({'error': '至少需要2个点'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        # 调用路线规划
        result = plan_route_with_amap(points, strategy)
        
        if 'error' in result:
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        else:
            response = jsonify(result)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
            
    except Exception as e:
        print(f"错误: {e}")
        response = jsonify({'error': str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# Vercel要求导出app
handler = app

"""
高德地图API工具模块
"""
import urllib.request
import urllib.parse
import json
import math
import os

# 高德地图API配置
AMAP_KEY = os.environ.get('AMAP_KEY', '0b9fba76af2364e9e650e8eacffc508f')
AMAP_DIRECTION_API = 'https://restapi.amap.com/v3/direction/driving'
AMAP_IP_API = 'https://restapi.amap.com/v3/ip'
AMAP_PLACE_TEXT_API = 'https://restapi.amap.com/v3/place/text'

def haversine_km(point1, point2):
    """
    计算两点间的球面距离（单位：公里）
    point1, point2: (longitude, latitude)
    """
    lon1, lat1 = point1
    lon2, lat2 = point2
    
    R = 6371.0  # 地球半径（公里）
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance

def decode_polyline(polyline_str):
    """
    解码高德地图返回的polyline字符串
    返回坐标数组 [[lng, lat], ...]
    """
    if not polyline_str:
        return []
    
    coords = []
    pairs = polyline_str.split(';')
    for pair in pairs:
        if ',' in pair:
            lng_str, lat_str = pair.split(',')
            try:
                lng = float(lng_str)
                lat = float(lat_str)
                coords.append([lng, lat])
            except ValueError:
                continue
    return coords

def get_location_by_ip(ip=None):
    """
    通过IP获取位置信息
    """
    try:
        params = {'key': AMAP_KEY}
        if ip:
            params['ip'] = ip
        
        url = f"{AMAP_IP_API}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == '1' and data.get('province'):
                return {
                    'province': data.get('province', ''),
                    'city': data.get('city', ''),
                    'adcode': data.get('adcode', ''),
                    'rectangle': data.get('rectangle', '')
                }
            else:
                return {'error': 'IP定位失败'}
    except Exception as e:
        print(f"IP定位失败: {e}")
        return {'error': str(e)}

def search_place_by_keyword(keyword, city=None):
    """
    通过关键字搜索地点
    """
    try:
        params = {
            'key': AMAP_KEY,
            'keywords': keyword,
            'offset': 10
        }
        if city:
            params['city'] = city
        
        url = f"{AMAP_PLACE_TEXT_API}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == '1' and data.get('pois'):
                pois = []
                for poi in data['pois']:
                    pois.append({
                        'name': poi.get('name', ''),
                        'address': poi.get('address', ''),
                        'location': poi.get('location', '')
                    })
                return {'pois': pois}
            else:
                return {'pois': []}
    except Exception as e:
        print(f"地点搜索失败: {e}")
        return {'error': str(e)}

def fetch_route_segment(origin, dest, waypoints=None, strategy='1'):
    """
    获取单个路线段
    origin, dest: (longitude, latitude)
    waypoints: [(longitude, latitude), ...]
    strategy: '0'=最快, '1'=最短距离
    """
    try:
        origin_str = f"{origin[0]},{origin[1]}"
        dest_str = f"{dest[0]},{dest[1]}"
        
        params = {
            'key': AMAP_KEY,
            'origin': origin_str,
            'destination': dest_str,
            'strategy': strategy,
            'extensions': 'all'
        }
        
        if waypoints and len(waypoints) > 0:
            waypoints_str = ';'.join([f"{w[0]},{w[1]}" for w in waypoints])
            params['waypoints'] = waypoints_str
        
        url = f"{AMAP_DIRECTION_API}?{urllib.parse.urlencode(params)}"
        
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            if data.get('status') == '1' and data.get('route'):
                route = data['route']
                paths = route.get('paths', [])
                if paths and len(paths) > 0:
                    path = paths[0]
                    distance_m = float(path.get('distance', 0))
                    duration_s = float(path.get('duration', 0))
                    
                    # 提取polyline
                    steps = path.get('steps', [])
                    all_coords = []
                    for step in steps:
                        polyline = step.get('polyline', '')
                        coords = decode_polyline(polyline)
                        all_coords.extend(coords)
                    
                    return {
                        'distance': round(distance_m / 1000, 2),  # 转换为公里
                        'duration': round(duration_s / 60, 1),    # 转换为分钟
                        'polyline': all_coords
                    }
            
            # 如果API调用失败，使用直线距离作为兜底
            distance = haversine_km(origin, dest)
            return {
                'distance': round(distance, 2),
                'duration': round(distance * 3, 1),  # 假设平均速度20km/h
                'polyline': [list(origin), list(dest)]
            }
    except Exception as e:
        print(f"路径规划失败: {e}")
        # 兜底方案
        distance = haversine_km(origin, dest)
        return {
            'distance': round(distance, 2),
            'duration': round(distance * 3, 1),
            'polyline': [list(origin), list(dest)]
        }

def plan_route_with_amap(points, strategy='1'):
    """
    规划完整路线（分段调用）
    points: [{'name': str, 'longitude': float, 'latitude': float}, ...]
    """
    if len(points) < 2:
        return {'error': '至少需要2个点'}, 400
    
    segments = []
    total_distance = 0
    total_duration = 0
    
    # 对相邻点逐段规划
    for i in range(len(points) - 1):
        from_point = points[i]
        to_point = points[i + 1]
        
        origin = (from_point['longitude'], from_point['latitude'])
        dest = (to_point['longitude'], to_point['latitude'])
        
        segment_result = fetch_route_segment(origin, dest, strategy=strategy)
        
        segment = {
            'from': {
                'name': from_point['name'],
                'longitude': from_point['longitude'],
                'latitude': from_point['latitude']
            },
            'to': {
                'name': to_point['name'],
                'longitude': to_point['longitude'],
                'latitude': to_point['latitude']
            },
            'distance': segment_result['distance'],
            'duration': segment_result['duration'],
            'polyline': segment_result['polyline']
        }
        
        segments.append(segment)
        total_distance += segment_result['distance']
        total_duration += segment_result['duration']
    
    return {
        'distance': round(total_distance, 2),
        'duration': round(total_duration, 1),
        'segments': segments
    }

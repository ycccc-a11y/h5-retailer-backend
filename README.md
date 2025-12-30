# H5零售户路线规划系统 - 后端API

## 项目简介

这是涉企行政检查路线规划系统的后端API服务，部署在Vercel平台上，提供许可证查询、路线规划、地点搜索等功能。

## 技术栈

- **平台**: Vercel Serverless Functions
- **语言**: Python 3.9+
- **数据库**: TiDB Cloud (MySQL兼容)
- **第三方服务**: 高德地图API

## API接口

### 1. 许可证搜索
```
GET /api/search/{license_number}
```

**响应示例**:
```json
{
  "license_number": "许可证号",
  "customer_name": "客户名称",
  "legal_person": "法人姓名",
  "address": "经营地址",
  "longitude": 120.891467,
  "latitude": 31.974575
}
```

### 2. 路线规划
```
POST /api/plan/route
Content-Type: application/json

{
  "points": [
    {
      "name": "起点名称",
      "longitude": 120.891467,
      "latitude": 31.974575
    },
    ...
  ],
  "strategy": "1"
}
```

**响应示例**:
```json
{
  "distance": 10.5,
  "duration": 25.3,
  "segments": [
    {
      "from": {...},
      "to": {...},
      "distance": 5.2,
      "duration": 12.5,
      "polyline": [[lng, lat], ...]
    }
  ]
}
```

### 3. 地点搜索
```
GET /api/place/search?keyword={keyword}&city={city}
```

### 4. IP定位
```
GET /api/location/ip?ip={ip}
```

## 部署到Vercel

### 前置要求

1. 安装Vercel CLI
```bash
npm install -g vercel
```

2. 登录Vercel账号
```bash
vercel login
```

### 部署步骤

1. **进入项目目录**
```bash
cd h5-retailer-backend
```

2. **首次部署**
```bash
vercel
```

按照提示选择：
- Set up and deploy? → Yes
- Which scope? → 选择你的账号
- Link to existing project? → No
- What's your project's name? → h5-retailer-backend
- In which directory is your code located? → ./
- Want to override the settings? → No

3. **配置环境变量**

在Vercel项目设置中添加以下环境变量：

```
DB_HOST=your-tidb-host.clusters.tidb-cloud.com
DB_PORT=4000
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=locationnt
AMAP_KEY=your-amap-api-key
```

设置方法：
- 访问 https://vercel.com/dashboard
- 选择你的项目
- 进入 Settings → Environment Variables
- 添加上述环境变量

4. **生产环境部署**
```bash
vercel --prod
```

部署完成后，你会获得一个类似这样的URL：
```
https://h5-retailer-backend.vercel.app
```

### TiDB Cloud数据库配置

1. 登录 [TiDB Cloud](https://tidbcloud.com/)
2. 创建或选择你的集群
3. 获取连接信息：
   - Host: `xxx.clusters.tidb-cloud.com`
   - Port: `4000`
   - User: 你的用户名
   - Password: 你的密码
4. 确保数据库中已导入Excel数据

### 数据导入

如果还没有导入数据，使用提供的Excel文件：

1. 在TiDB Cloud控制台创建数据库 `locationnt`
2. 使用数据导入工具或SQL脚本导入 `南通市烟草专卖局零售户经纬度.xlsx`

## 本地开发

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 设置环境变量
```bash
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=123456
export DB_NAME=locationnt
export AMAP_KEY=your-amap-key
```

3. 使用Vercel CLI本地运行
```bash
vercel dev
```

## 前端配置

部署完成后，需要更新前端代码中的API地址。

修改 `api.js` 中的 `getApiBaseUrl()` 函数：

```javascript
function getApiBaseUrl() {
    // 使用Vercel部署的后端API地址
    return 'https://h5-retailer-backend.vercel.app';
}
```

## 故障排查

### 1. 数据库连接失败
- 检查环境变量是否正确配置
- 确认TiDB Cloud集群是否运行中
- 检查IP白名单设置（TiDB Cloud可能需要添加Vercel的IP）

### 2. API调用超时
- Vercel免费版有10秒执行时间限制
- 考虑优化数据库查询
- 检查高德API调用是否正常

### 3. CORS错误
- 确认所有API端点都设置了正确的CORS头
- 检查前端域名是否正确

## 监控与日志

在Vercel控制台可以查看：
- 函数调用日志
- 错误堆栈信息
- 性能指标

访问路径：Dashboard → 项目 → Functions → Logs

## 成本说明

- **Vercel**: 免费套餐包含100GB带宽/月，100GB-hours函数执行时间
- **TiDB Cloud**: 提供免费套餐，足够开发和小规模使用
- **高德地图**: 个人开发者每日免费配额

## 技术支持

如有问题，请查看：
- Vercel文档: https://vercel.com/docs
- TiDB Cloud文档: https://docs.pingcap.com/tidbcloud
- 高德地图API文档: https://lbs.amap.com/api/

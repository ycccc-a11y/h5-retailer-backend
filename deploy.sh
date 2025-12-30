#!/bin/bash

# H5零售户路线规划系统 - 快速部署脚本

echo "================================"
echo "H5零售户路线规划系统 - 后端部署"
echo "================================"
echo ""

# 检查是否安装了Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ 未检测到Vercel CLI"
    echo "请先安装: npm install -g vercel"
    exit 1
fi

echo "✅ Vercel CLI已安装"
echo ""

# 检查是否已登录
echo "检查Vercel登录状态..."
if ! vercel whoami &> /dev/null; then
    echo "请先登录Vercel..."
    vercel login
fi

echo "✅ 已登录Vercel"
echo ""

# 部署到生产环境
echo "开始部署到Vercel生产环境..."
echo ""

vercel --prod

echo ""
echo "================================"
echo "✅ 部署完成！"
echo "================================"
echo ""
echo "下一步："
echo "1. 访问 https://vercel.com/dashboard"
echo "2. 进入项目 Settings → Environment Variables"
echo "3. 添加以下环境变量："
echo "   - DB_HOST: TiDB Cloud主机地址"
echo "   - DB_PORT: 4000"
echo "   - DB_USER: 数据库用户名"
echo "   - DB_PASSWORD: 数据库密码"
echo "   - DB_NAME: locationnt"
echo "   - AMAP_KEY: 高德地图API Key"
echo "4. 重新部署: vercel --prod"
echo ""
echo "详细说明请查看 README.md"
echo ""

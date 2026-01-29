#!/bin/bash

# 测试 CommonServ FastAPI 服务

echo "================================"
echo "测试 CommonServ 服务"
echo "================================"

# 测试根路径
echo ""
echo "[1/4] 测试服务根路径..."
curl -s http://localhost:8080/api/ | python3 -m json.tool || echo "❌ 根路径测试失败"

# 测试健康检查
echo ""
echo "[2/4] 测试健康检查..."
curl -s http://localhost:8080/api/health | python3 -m json.tool || echo "❌ 健康检查失败"

# 测试 API 文档
echo ""
echo "[3/4] 测试 API 文档访问..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/docs)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ API 文档可访问 (HTTP $HTTP_CODE)"
else
    echo "❌ API 文档访问失败 (HTTP $HTTP_CODE)"
fi

# 测试直接访问（绕过 Nginx）
echo ""
echo "[4/4] 测试直接访问 FastAPI 服务..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 直接访问成功 (HTTP $HTTP_CODE)"
else
    echo "❌ 直接访问失败 (HTTP $HTTP_CODE)"
fi

echo ""
echo "================================"
echo "测试完成！"
echo "================================"

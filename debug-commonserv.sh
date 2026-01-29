#!/bin/bash

# 诊断 commonserv 部署问题

echo "=========================================="
echo "CommonServ 部署诊断"
echo "=========================================="

echo ""
echo "[1] 当前工作目录："
pwd
echo ""

echo "[2] 目录结构检查："
echo "clouddeploy 目录内容："
ls -la
echo ""
echo "上级目录内容："
ls -la ../ 2>/dev/null || echo "无法访问上级目录"
echo ""

echo "[3] 检查 commonserv 是否存在："
if [ -d "../commonserv" ]; then
    echo "✓ ../commonserv 存在"
    echo "  内容："
    ls -la ../commonserv/ | head -15
else
    echo "✗ ../commonserv 不存在"
fi
echo ""

echo "[4] 检查 Dockerfile："
if [ -f "../commonserv/Dockerfile" ]; then
    echo "✓ Dockerfile 存在于 ../commonserv/"
    echo "  内容："
    cat ../commonserv/Dockerfile
else
    echo "✗ Dockerfile 不存在于 ../commonserv/"
    echo "  查找所有 Dockerfile："
    find ../ -name "Dockerfile" 2>/dev/null | head -10
fi
echo ""

echo "[5] 检查绝对路径："
ABSOLUTE_PATH=$(realpath ../commonserv 2>/dev/null || echo "无法获取绝对路径")
echo "绝对路径: $ABSOLUTE_PATH"
echo ""

echo "[6] 检查 Docker Compose 配置："
echo "docker-compose.yml 中的 commonserv 配置："
grep -A 10 "commonserv:" docker-compose.yml
echo ""

echo "[7] 尝试手动构建："
if [ -d "../commonserv" ]; then
    echo "进入 commonserv 目录并尝试构建："
    cd ../commonserv
    docker build -t test-commonserv . 2>&1 | tail -20
    cd -
fi

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="

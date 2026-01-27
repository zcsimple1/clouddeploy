#!/bin/bash

# 快速修复 pip3 和安装 paho-mqtt

echo "================================"
echo "快速修复 pip3 并安装 paho-mqtt"
echo "================================"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    echo "运行: sudo bash fix-pip.sh"
    exit 1
fi

# 方法1: 尝试使用包管理器安装 pip3
echo "尝试使用 apt-get 安装 pip3..."
apt-get update
apt-get install -y python3-pip

# 检查是否成功
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 安装成功: $(pip3 --version)"
else
    echo "✗ apt-get 安装失败，尝试使用 get-pip.py..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3
fi

# 再次检查
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 已安装: $(pip3 --version)"
else
    echo "✗ pip3 安装失败，请手动检查"
    exit 1
fi

echo ""
echo "安装 paho-mqtt..."
pip3 install paho-mqtt

# 验证
echo ""
echo "验证安装..."
if python3 -c "import paho.mqtt.client" &> /dev/null; then
    VERSION=$(python3 -c "import paho.mqtt.client; print(paho.mqtt.client.__version__)" 2>/dev/null || echo "已安装")
    echo "✓ paho-mqtt 安装成功: $VERSION"
else
    echo "✗ paho-mqtt 安装失败"
    exit 1
fi

echo ""
echo "================================"
echo "✅ 修复完成！"
echo "================================"
echo ""
echo "现在可以运行测试脚本:"
echo "  python3 test-cloud.py"
echo ""

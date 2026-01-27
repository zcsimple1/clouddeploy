#!/bin/bash

# MQTT 测试环境依赖安装脚本
# 使用方法: sudo bash setup-env.sh

set -e

echo "================================"
echo "MQTT 测试环境依赖安装"
echo "================================"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 1. 更新包管理器
echo "1/5: 更新包管理器..."
if command -v apt-get &> /dev/null; then
    apt-get update
elif command -v yum &> /dev/null; then
    yum check-update || true
else
    echo "未知的包管理器"
    exit 1
fi

# 2. 安装 Python3 和 pip
echo ""
echo "2/5: 安装 Python3 和 pip..."
if ! command -v python3 &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        apt-get install -y python3 python3-pip
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip
    fi
else
    echo "✓ Python3 已安装: $(python3 --version)"
fi

# 安装 pip3
if ! command -v pip3 &> /dev/null; then
    echo "安装 pip3..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y python3-pip
    elif command -v yum &> /dev/null; then
        yum install -y python3-pip
    fi
    
    # 如果仍然没有 pip3，使用 get-pip.py
    if ! command -v pip3 &> /dev/null; then
        echo "使用 get-pip.py 安装 pip..."
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3
    fi
else
    echo "✓ pip3 已安装: $(pip3 --version)"
fi

# 3. 安装 mosquitto 客户端
echo ""
echo "3/5: 安装 mosquitto 客户端..."
if ! command -v mosquitto_pub &> /dev/null; then
    if command -v apt-get &> /dev/null; then
        apt-get install -y mosquitto-clients
    elif command -v yum &> /dev/null; then
        yum install -y mosquitto-clients
    fi
    echo "✓ mosquitto-clients 安装完成"
else
    echo "✓ mosquitto-clients 已安装"
fi

# 4. 安装 Python MQTT 库
echo ""
echo "4/5: 安装 Python MQTT 库..."
if command -v pip3 &> /dev/null; then
    pip3 install paho-mqtt
else
    echo "✗ pip3 未安装，跳过 Python 库安装"
    exit 1
fi

# 5. 验证安装
echo ""
echo "5/5: 验证安装..."
echo ""

echo "================================"
echo "安装验证"
echo "================================"
echo ""

# 检查 Python3
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python3: $PYTHON_VERSION"
else
    echo "✗ Python3 未安装"
fi

# 检查 pip3
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo "✓ pip3: $PIP_VERSION"
else
    echo "✗ pip3 未安装"
fi

# 检查 mosquitto
if command -v mosquitto_pub &> /dev/null; then
    MOSQUITTO_VERSION=$(mosquitto_pub --help | head -n1 || echo "已安装")
    echo "✓ mosquitto-clients: $MOSQUITTO_VERSION"
else
    echo "✗ mosquitto-clients 未安装"
fi

# 检查 paho-mqtt
if python3 -c "import paho.mqtt.client" &> /dev/null; then
    PAHO_VERSION=$(python3 -c "import paho.mqtt.client; print(paho.mqtt.client.__version__)" 2>/dev/null || echo "已安装")
    echo "✓ paho-mqtt: $PAHO_VERSION"
else
    echo "✗ paho-mqtt 未安装"
fi

echo ""
echo "================================"
echo "✅ 环境准备完成！"
echo "================================"
echo ""
echo "现在可以运行测试脚本:"
echo "  python3 test-cloud.py"
echo ""

#!/bin/bash

# 拉取所有项目的最新代码（包括 clouddeploy 自身）

echo "================================"
echo "开始拉取所有项目的最新代码..."
echo "================================"

# 拉取 zcgames 项目
echo ""
echo "[1/5] 拉取 zcgames..."
if [ -d "../zcgames" ]; then
    cd ../zcgames
    git pull origin $(git rev-parse --abbrev-ref HEAD)
    cd -
else
    echo "⚠️  zcgames 目录不存在，跳过"
fi

# 拉取 edutool 项目
echo ""
echo "[2/5] 拉取 edutool..."
if [ -d "../edutool" ]; then
    cd ../edutool
    git pull origin $(git rev-parse --abbrev-ref HEAD)
    cd -
else
    echo "⚠️  edutool 目录不存在，跳过"
fi

# 拉取 webtool 项目
echo ""
echo "[3/5] 拉取 webtool..."
if [ -d "../webtool" ]; then
    cd ../webtool
    git pull origin $(git rev-parse --abbrev-ref HEAD)
    cd -
else
    echo "⚠️  webtool 目录不存在，跳过"
fi

# 拉取 commonserv 项目
echo ""
echo "[4/5] 拉取 commonserv..."
if [ -d "../commonserv" ]; then
    cd ../commonserv
    git pull origin $(git rev-parse --abbrev-ref HEAD)
    cd -
else
    echo "⚠️  commonserv 目录不存在，尝试克隆..."
    cd ..
    # 优先尝试 HTTPS 克隆（无需 SSH 密钥），失败则尝试 SSH
    if git clone https://github.com/zcsimple1/commonserv.git; then
        echo "✅ commonserv 克隆成功 (HTTPS)"
        cd clouddeploy
    elif git clone git@github.com:zcsimple1/commonserv.git; then
        echo "✅ commonserv 克隆成功 (SSH)"
        cd clouddeploy
    else
        echo "❌ commonserv 克隆失败"
        echo "   请手动执行: cd .. && git clone https://github.com/zcsimple1/commonserv.git"
        cd clouddeploy
    fi
fi

# 拉取 clouddeploy 项目自身
echo ""
echo "[5/5] 拉取 clouddeploy（当前项目）..."
git pull origin $(git rev-parse --abbrev-ref HEAD)

echo ""
echo "================================"
echo "✅ 所有代码拉取完成！"
echo "================================"
